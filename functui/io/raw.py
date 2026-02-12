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
from ..classes import InputEvent, Coordinate, Rect
import sys
import ctypes
import shutil

@dataclass
class TerminalFeatures:
    mouse: bool = False
    bracketed_paste: bool = False
    alternate_screen: bool = False
    line_wrap: bool = True
    # in_band_window_resize: bool = False

DEFAULT_FEATURES = TerminalFeatures()
APPLICATION_MODE_FEATURES = TerminalFeatures(True, True, True, False)



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

    # if features.in_band_window_resize:
    #     stdout.write("\x1b[?2048h")
    #     stdout.write("\x1b[?2048$p") # querry
    #
    # else:
    #     stdout.write("\x1b[?2048l")

    stdout.flush()


class TerminalIO(ABC):
    """Termian input output object that has both windows and unix implemintions.
    see also:
        :func:`create_terminal_io`
    """
    def __init__(self, stdin: TextIO | None = None, stdout: TextIO | None = None) -> None:
        self.stdin: TextIO = stdin if stdin is not None else sys.__stdin__ # type: ignore
        self.stdout: TextIO = stdout if stdout is not None else sys.__stdout__ # type: ignore

    @abstractmethod
    def run(self, *,callback: Callable, features: TerminalFeatures = APPLICATION_MODE_FEATURES):
        """Run the application."""
        ...
    @abstractmethod
    def get_terminal_size(self) -> Rect:
        """Get terminal size."""
        ...
    def print(self, ansi_data: str):
        """Write a string with ansi codes to output and flush.

        see also:
            Ways of generating the ``ansi_data`` string can be found in :obj:`functui.io.ansi`."""
        self.stdout.write(ansi_data)
        self.stdout.flush()

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
                            data = "mouse wheel up"
                        elif button_nr == "64":
                            data = "mouse wheel down"

                        return InputEvent(key_event=data, mouse_position_event=Coordinate(int(x), int(y)))
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

class WindowsTerminalIO(TerminalIO):
    def get_terminal_size(self) -> Rect:
        size = shutil.get_terminal_size()
        return Rect(size.columns, size.lines)
    def run(
        self,
        *,
        callback: Callable,
        features: TerminalFeatures = APPLICATION_MODE_FEATURES
    ):
        # windows specific setup
        kernel32 = ctypes.windll.kernel32 # type: ignore
        stdin_handle = kernel32.GetStdHandle(-10)
        old_mode = ctypes.c_uint()
        kernel32.GetConsoleMode(stdin_handle, ctypes.byref(old_mode))

        # Disable:
        # ENABLE_LINE_INPUT (0x0002)
        # ENABLE_ECHO_INPUT (0x0004)
        # ENABLE_PROCESSED_INPUT (0x0001)
        new_mode = (old_mode.value & ~(0x0002 | 0x0004 | 0x0001)) | 0x0200 # ENABLE_VIRTUAL_TERMINAL_INPUT (for xterm compatability)
        kernel32.SetConsoleMode(stdin_handle, new_mode)
        # end

        byte_parser = ByteParser()
        raw_parser = RawInputParser()

        try:
            set_xterm_features(self.stdout, features)
            while True:
                input = self.stdin.buffer.read(1)
                if raw_event := byte_parser.feed(input[0]):
                    # print(repr(raw_event.data), raw_event.type)
                    if event := raw_parser.feed(raw_event):
                        should_quit = callback(event)
                        if should_quit:
                            break
        finally:
            set_xterm_features(self.stdout, DEFAULT_FEATURES)
            # windows specific cleanup
            kernel32.SetConsoleMode(stdin_handle, old_mode)
            # end


class UnixTerminalIO(TerminalIO):
    def get_terminal_size(self) -> Rect:
        size = shutil.get_terminal_size()
        return Rect(size.columns, size.lines)
    def run(
        self,
        *,
        callback: Callable[[InputEvent], Any],
        features: TerminalFeatures = APPLICATION_MODE_FEATURES,
    ):
        byte_parser = ByteParser()
        raw_parser = RawInputParser()


        # unix specific setup
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_attrs = termios.tcgetattr(fd)
        tty.setraw(fd)
        # end
        try:
            set_xterm_features(self.stdout, features)
            while True:
                input = self.stdin.buffer.read(1)
                if raw_event := byte_parser.feed(input[0]):
                    if event := raw_parser.feed(raw_event):
                        should_quit = callback(event)
                        if should_quit:
                            break
                        # if event.key_event == "unknown":
                        #     print(repr(raw_event.data), raw_event.type.name)
        finally:
            set_xterm_features(self.stdout, DEFAULT_FEATURES)
            # unix specific cleanup
            tty.setcbreak(fd)
            termios.tcsetattr(fd, termios.TCSANOW, old_attrs)
            # end



def create_terminal_io():
    """Create a :obj:`TerminalIO` for the appropriate environment."""
    IS_WINDOWS = sys.platform == "win32"
    if IS_WINDOWS:
        return WindowsTerminalIO()
    else:
        return UnixTerminalIO()

