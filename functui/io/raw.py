"""Cross platform input and output implemintation."""
# xterm sequence docs
# https://invisible-island.net/xterm/ctlseqs/ctlseqs.html

# term definitions
# ----------------

# ESC = strings startign with \x1b in hex (or \033 in octal)
# CSI = ESC [
# SS3 = ESC 0

# codes that switch modes start with CSI ?
# DECSET means private mode set (CSI ? <mode number> h)
# DECRST means private mode reset (CSI ? <mode number> l)
#
# RAW MODE - means that 

# Ranges
# ------

# C0           = 0x00–0x1F
# DEL          = 0x7F
# ESC          = 0x1B
# INTERMEDIATE = 0x20–0x2F
# PARAM        = 0x30–0x3F
# FINAL        = 0x40–0x7E
# UTF8_CONT    = 0x80–0xBF

# escape codes by topic
# ---------------------

# ALTERNATE BUFFER
# CSI ? 1049 h -- enter alt buffer + save cursor
# CSI ? 1049 l -- exit + restore cursor

# BRACKETED PASTE
# CSI 200 ~ -- bracketed paste start
# CSI 201 ~ -- bracketed paste end

# MOUSE
# 
from ._xterm_parser import ByteParser, RawInputEvent, RawInputType
from ._xterm_escape_data import SUQUENCE_TO_KEY

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Callable, TextIO
from dataclasses import dataclass
from ..classes import InputEvent, Coordinate, Rect, intersperse, Result, Screen, ResultCreatedWith
from .ansi import result_to_str, _render_ansi

from queue import SimpleQueue, Empty
import threading
import sys
import ctypes
import shutil
import os

class RawInputParserState(Enum):
    GROUND = auto()
    PASTE = auto()

class RawInputParser:
    def __init__(self) -> None:
        self.state = RawInputParserState.GROUND
        self._paste_buffer: list[str] = []

    def feed(self, raw_event: RawInputEvent) -> InputEvent | None:
        match self.state:
            case RawInputParserState.GROUND:
                if raw_event.type == RawInputType.CHAR:
                    return InputEvent(key_event=raw_event.data)
                if raw_event.type == RawInputType.CSI:
                    if raw_event.data == "\x1b[200~": # bracketed paste start
                        self.state = RawInputParserState.PASTE
                        return
                    if raw_event.data.startswith("\x1b[<"): # mouse
                        first_sep_at = raw_event.data.find(";")
                        button_nr = raw_event.data[3:first_sep_at]
                        released = raw_event.data.endswith("m")
                        released_suffix = " released" if released else ""
                        prefix, x, y_and_suffix = raw_event.data.split(";", 3)
                        y = y_and_suffix[:-1]
                        data = "unknown"
                        if button_nr == "0":
                            data = "left mouse" + released_suffix
                        elif button_nr == "1":
                            data = "middle mouse" + released_suffix
                        elif button_nr == "2":
                            data = "right mouse" + released_suffix
                        elif button_nr in ("35", "34", "33", "32"): # mouse move
                            data = None
                        elif button_nr == "65":
                            data = "mouse wheel down"
                        elif button_nr == "64":
                            data = "mouse wheel up"

                        return InputEvent(key_event=data, mouse_position_event=Coordinate(int(x)-1, int(y)-1))
                if parsed_key := SUQUENCE_TO_KEY.get(raw_event.data, None):
                    return InputEvent(key_event=parsed_key)
                return InputEvent(key_event="unknown")
            case RawInputParserState.PASTE:
                if raw_event.type == RawInputType.CHAR:
                    self._paste_buffer.append(raw_event.data)
                    return
                if raw_event.type == RawInputType.CSI and raw_event.data == "\x1b[201~": # bracketed paste start
                    data = f"[{"".join(self._paste_buffer)}]"
                    self._paste_buffer.clear()
                    self.state = RawInputParserState.GROUND
                    return InputEvent(key_event=data)

@dataclass(frozen=True, eq=True)
class TerminalFeatures:
    mouse: bool = False
    bracketed_paste: bool = False
    alternate_screen: bool = False
    line_wrap: bool = True
    hidden_cursor: bool = False
    # in_band_window_resize: bool = False

DEFAULT_FEATURES = TerminalFeatures()
APPLICATION_MODE_FEATURES = TerminalFeatures(True, True, True, True, True)



def set_xterm_features(stdout: TextIO, features: TerminalFeatures):
    if features.alternate_screen:
        stdout.write("\x1b[?1049h") # Alt screen
        stdout.flush()
    else:
        stdout.write("\x1b[?1049l") # Alt screen
        stdout.flush()

    if features.mouse:
        stdout.write("\x1b[?1000h") # SET_VT200_MOUSE
        stdout.write("\x1b[?1003h") # SET_ANY_EVENT_MOUSE
        stdout.write("\x1b[?1006h") # SET_ANY_EVENT_MOUSE
    else:
        stdout.write("\x1b[?1000l") # RESET_VT200_MOUSE
        stdout.write("\x1b[?1003l") # RESET_ANY_EVENT_MOUSE
        stdout.write("\x1b[?1006l") # RESET_ANY_EVENT_MOUSE

    if features.bracketed_paste:
        stdout.write("\x1b[?2004h") # set bracketed paste mode, xterm.
    else:
        stdout.write("\x1b[?2004l") # reset bracketed paste mode, xterm.
    if features.line_wrap:
        stdout.write("\x1b[?7h")
    else:
        stdout.write("\x1b[?7l")
    if features.hidden_cursor:
        stdout.write("\x1b[?25l")
    else:
        stdout.write("\x1b[?25h")

    # if features.in_band_window_resize:
    #     stdout.write("\x1b[?2048h")
    #     stdout.write("\x1b[?2048$p") # querry
    #
    # else:
    #     stdout.write("\x1b[?2048l")

    stdout.flush()


class TerminalIO(ABC):
    """Terminal input output object that has both windows and unix implemintions.
    see also:
        :func:`terminal`
    """
    def __init__(
        self,
        event_queue: SimpleQueue[InputEvent],
        stdout: TextIO
    ) -> None:
        self.event_queue = event_queue
        self.stdout: TextIO = stdout

        x, y = self.get_terminal_size()
        self._last_terminal_size = Rect(x, y)
        self._screen = Screen(x, y)

    @abstractmethod
    def get_terminal_size(self) -> Rect:
        """Get terminal size."""
        ...
    @abstractmethod
    def print(self, ansi_data: str):
        """Write a string with ansi codes to output and flush.

        see also:
            Ways of generating the ``ansi_data`` string can be found in :obj:`functui.io.ansi`."""

    def block_untill_input(self, ignore_excess_mouse: bool = True) -> InputEvent:

        # if rendering is taking time and we cant handle every event
        # if self.event_queue.qsize() > 1 and ignore_excess_mouse:
        while self.event_queue.qsize() > 1 and ignore_excess_mouse:
            event = self.event_queue.get()
            if event.key_event is not None:
                return event

        return self.event_queue.get()
    def display_result(self, res: Result):

        data = res.expect_data(ResultCreatedWith)
        # don't recreate the screen unless forced to
        if data.screen_size != self._last_terminal_size:
            self._last_terminal_size = data.screen_size
            self._screen = Screen(*self._last_terminal_size)
        else:
            self._screen.clear()

        self._screen.apply_draw_commands(data.measure_text_func, res.get_commands()) # 20 %
        out_str =  _render_ansi(self._screen) # 30 %
        self.print("\x1b[H" + out_str + "\033[39m\033[49m")

class TerminalContext(ABC):
    def __init__(
        self,
        features: TerminalFeatures,
        stdin: TextIO,
        stdout: TextIO,
    ) -> None:
        self.stdin = stdin
        self.stdout = stdout
        self.features = features
    @abstractmethod
    def __enter__(self) -> TerminalIO:
        ...
    @abstractmethod
    def __exit__(self, value, exception, traceback):
        ...

def _create_reader_thread(stdin: TextIO, queue: SimpleQueue[InputEvent]):
    def _reader_thread():
        byte_parser = ByteParser()
        raw_parser = RawInputParser()
        while True:
            input = stdin.buffer.read(1)
            if raw_event := byte_parser.feed(input[0]):
                # print(repr(raw_event.data), raw_event.type)
                if event := raw_parser.feed(raw_event):
                    queue.put(event)
    return threading.Thread(target=_reader_thread, daemon=True)

def _get_all_queue_items[T](queue: SimpleQueue[T]) -> list[T]:
    out = []
    try:
        item = queue.get_nowait()
        out.append(item)
    except Empty:
        pass
    return out




class WindowsTerminalContext(TerminalContext):
    @classmethod
    def _set_console_mode(cls, console: TextIO, mode: int) -> bool:
        import msvcrt
        kernel32 = ctypes.windll.kernel32
        filehandle = msvcrt.get_osfhandle(console.fileno())  # type: ignore
        success = kernel32.SetConsoleMode(filehandle, mode) # type: ignore
        return success

    @classmethod
    def _get_console_mode(cls, console: TextIO) -> int:
        import msvcrt
        kernel32 = ctypes.windll.kernel32
        filehandle = msvcrt.get_osfhandle(console.fileno())
        mode = ctypes.c_uint()
        kernel32.GetConsoleMode(filehandle, ctypes.byref(mode))
        return mode.value

    def __enter__(self):
        os.system("")
        # windows specific setup
        ENABLE_LINE_INPUT = 0x0002
        ENABLE_ECHO_INPUT = 0x0004
        ENABLE_PROCESSED_INPUT = 0x0001
        ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200
        # output modes
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        old_console_mode_in = self._get_console_mode(self.stdin)
        old_console_mode_out = self._get_console_mode(self.stdout)

        def restore():
            self._set_console_mode(self.stdin, old_console_mode_in)
            self._set_console_mode(self.stdout, old_console_mode_out)
        self.restore = restore

        self._set_console_mode(self.stdin, (old_console_mode_in | ENABLE_VIRTUAL_TERMINAL_INPUT) & ~ (ENABLE_ECHO_INPUT | ENABLE_LINE_INPUT | ENABLE_PROCESSED_INPUT))
        self._set_console_mode(self.stdout, old_console_mode_out | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
        # end

        event_queue: SimpleQueue[InputEvent] = SimpleQueue()
        self.reader_thread = _create_reader_thread(self.stdin, event_queue)
        self.reader_thread.start()

        set_xterm_features(self.stdout, self.features)
        return WindowsTerminalIO(event_queue, self.stdout)

    def __exit__(self, value, exception, traceback):
        set_xterm_features(self.stdout, DEFAULT_FEATURES)

        # windows specific cleanup
        self.restore()
        # end





class WindowsTerminalIO(TerminalIO):
    def get_terminal_size(self) -> Rect:
        size = shutil.get_terminal_size()
        return Rect(size.columns, size.lines)
    def print(self, ansi_data: str):
        self.stdout.write(ansi_data)
        self.stdout.flush()

class UnixTerminalContext(TerminalContext):
    def __enter__(self):
        # unix specific setup
        import termios
        import tty
        self.fd = sys.stdin.fileno()
        self.old_attrs = termios.tcgetattr(self.fd)
        tty.setraw(self.fd)
        # end
        event_queue: SimpleQueue[InputEvent] = SimpleQueue()
        self.reader_thread = _create_reader_thread(self.stdin, event_queue)
        self.reader_thread.start()
        set_xterm_features(self.stdout, self.features)
        return UnixTerminalIO(event_queue, self.stdout)

    def __exit__(self, value, exception, traceback):
        set_xterm_features(self.stdout, DEFAULT_FEATURES)
        # unix specific cleanup
        import termios
        import tty
        tty.setcbreak(self.fd)
        termios.tcsetattr(self.fd, termios.TCSANOW, self.old_attrs)
        # end

class UnixTerminalIO(TerminalIO):
    def get_terminal_size(self) -> Rect:
        size = shutil.get_terminal_size()
        return Rect(size.columns, size.lines)
    def print(self, ansi_data: str):
        ansi_data = "".join(intersperse(ansi_data.split("\n"), sep="\n\r"))
        self.stdout.write(ansi_data)
        self.stdout.flush()





def terminal(features: TerminalFeatures = APPLICATION_MODE_FEATURES):
    """Create a :obj:`TerminalContext` for the appropriate environment."""
    IS_WINDOWS = sys.platform == "win32"
    stdin = sys.__stdin__
    stdout = sys.__stdout__
    if IS_WINDOWS:
        return WindowsTerminalContext(features,stdin, stdout)
    else:
        return UnixTerminalContext(features,stdin, stdout)
