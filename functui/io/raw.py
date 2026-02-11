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
# CSI ? 200 ~ -- bracketed paste start
# CSI ? 201 ~ -- bracketed paste end

# MOUSE
# 
from abc import ABC, abstractmethod
from enum import Enum, auto
import sys
from typing import Any, Callable, TextIO
from dataclasses import dataclass

@dataclass
class TerminalFeatures:
    mouse: bool = True
    bracketed_paste: bool = True
    alternate_screen: bool = True

DEFAULT_FEATURES = TerminalFeatures(False, False, False)
APPLICATION_MODE_FEATURES = TerminalFeatures()

class ParserState(Enum):
    GROUND = auto()
    UTF_2_BYTES = auto()
    UTF_3_BYTES = auto()
    UTF_4_BYTES = auto()
    ESC = auto()
    CSI = auto()
    OSC = auto()
    MAYBE_ST = auto() # string terminator


class RawInputType(Enum):
    CHAR = auto()
    DEL = auto()
    CSI = auto()
    OSC = auto()
    C0 = auto()

@dataclass
class RawInputEvent:
    data: str
    type: RawInputType

ESCAPE_BYTE = ord("\x1b")
class ByteParser:
    buffer: list[int] = []
    state: ParserState = ParserState.GROUND

    def feed(self, byte: int) -> RawInputEvent | None:
        match self.state:
            case ParserState.GROUND:
                if 0x00 <= byte <= 0x1F:
                    if byte == ESCAPE_BYTE:
                        self.buffer.append(byte)
                        self._change_state(ParserState.ESC)
                        return

                    data = chr(byte)
                    return RawInputEvent(data, RawInputType.C0)
                if byte==0x7F:
                    data = chr(byte)
                    return RawInputEvent(data, RawInputType.DEL)
                elif (byte >> 5) == 0b0000_0110: # utf, 2 bytes
                    self.buffer.append(byte)
                    self._change_state(ParserState.UTF_2_BYTES)
                    return
                elif (byte >> 4) == 0b0000_1110: # utf, 2 bytes
                    self.buffer.append(byte)
                    self._change_state(ParserState.UTF_3_BYTES)
                elif (byte >> 3) == 0b0001_1110: # utf, 2 bytes
                    self.buffer.append(byte)
                    self._change_state(ParserState.UTF_4_BYTES)

                # ascii printable character
                # no need to clear buffer because nothing was put in.
                return RawInputEvent(chr(byte), RawInputType.CHAR)
            case ParserState.ESC:
                if byte == ord("["):
                    self.buffer.append(byte)
                    self._change_state(ParserState.CSI)
                    return
                if byte == ord("]"):
                    self.buffer.append(byte)
                    self._change_state(ParserState.OSC)
                    return
            case ParserState.OSC:
                if byte == 0x07: # BEL
                    self.buffer.append(byte)
                    data = bytearray(self.buffer).decode()
                    self._change_state(ParserState.GROUND)
                    return RawInputEvent(data, RawInputType.OSC) 
                if byte == ESCAPE_BYTE:
                    self._change_state(ParserState.MAYBE_ST)
                    self.buffer.append(byte)
                    return
                self.buffer.append(byte)
            case ParserState.MAYBE_ST:
                if byte == 0x5C: # is string terminator
                    self.buffer.append(byte)
                    data = bytearray(self.buffer).decode()
                    self._change_state(ParserState.GROUND)
                    return RawInputEvent(data, RawInputType.OSC)
                # was not string terminator, just data
                self._change_state(ParserState.OSC)
                self.buffer.append(byte)
                return
            case ParserState.CSI:
                if 0x30 <= byte <= 0x3F: # (ASCII 0–9:;<=>?)
                    # we are in parameter bytes, the escape code will continue
                    self.buffer.append(byte)
                    return
                self.buffer.append(byte)
                char = bytearray(self.buffer).decode()
                self._change_state(ParserState.GROUND)
                return RawInputEvent(char, RawInputType.CSI)

            case ParserState.UTF_2_BYTES:
                if (byte >> 6) == 0b0000_0010:
                    self.buffer.append(byte)
                    char = bytearray(self.buffer).decode()
                    self._change_state(ParserState.GROUND)
                    return RawInputEvent(
                        char,
                        RawInputType.CHAR,
                    )

    def _change_state(self, new_state: ParserState) -> None:
        if new_state == ParserState.GROUND:
            self.buffer.clear()
        self.state = new_state


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

    # if not features.alternate_screen:
    #     stdout.write("\x1b[?1049l") # Alt screen

    stdout.flush()

class TerminalIO(ABC):
    @abstractmethod
    def run(self, *,callback: Callable, features: TerminalFeatures = APPLICATION_MODE_FEATURES):
        ...
    
class WindowsTerminalIO(TerminalIO):
    def run(
        self,
        *,
        callback: Callable,
        features: TerminalFeatures = APPLICATION_MODE_FEATURES
    ):
        stdin = sys.stdin
        stdout = sys.stdout
        try:
            set_xterm_features(stdout, features)
            for _ in range(10):
                input = stdin.buffer.read(1)
                callback(repr(input))
        finally:
            set_xterm_features(stdout, DEFAULT_FEATURES)


class UnixTerminalIO(TerminalIO):
    def __init__(self) -> None:
        super().__init__()
        # self.old_terminal_attrs: None | list[Any] = None


    def run(
        self,
        *,
        callback: Callable,
        features: TerminalFeatures = APPLICATION_MODE_FEATURES,
    ):
        stdin = sys.stdin
        stdout = sys.stdout
        parser = ByteParser()

        # unix specific setup
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_attrs = termios.tcgetattr(fd)
        tty.setraw(fd)
        # end
        try:
            set_xterm_features(stdout, features)
            for _ in range(1000):
                input = stdin.buffer.read(1)
                if event := parser.feed(input[0]):
                    callback(event)
        finally:
            set_xterm_features(stdout, DEFAULT_FEATURES)
            # unix specific cleanup
            tty.setcbreak(fd)
            termios.tcsetattr(fd, termios.TCSANOW, old_attrs)
            # end



def create_terminal_io():
    IS_WINDOWS = sys.platform == "win32"
    if IS_WINDOWS:
        return WindowsTerminalIO()
    else:
        return UnixTerminalIO()

