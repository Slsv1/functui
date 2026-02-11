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
import sys
from typing import Any, Callable, TextIO
from dataclasses import dataclass

@dataclass
class TerminalFeatures:
    mouse: bool = True
    bracketed_paste: bool = True
    alternate_screen: bool = True

ALL_FEATURES = TerminalFeatures()



def enable_xterm_features(stdout: TextIO, features: TerminalFeatures):
    if features.alternate_screen:
        stdout.write("\x1b[?1049h") # Alt screen
    if features.mouse:
        stdout.write("\x1b[?1000h") # SET_VT200_MOUSE
        stdout.write("\x1b[?1003h") # SET_ANY_EVENT_MOUSE
        stdout.write("\x1b[?1006h") # SET_ANY_EVENT_MOUSE
    if features.bracketed_paste:
        stdout.write("\x1b[?2004h") # set bracketed paste mode, xterm.
    stdout.flush()

def disable_xterm_features(stdout: TextIO, features: TerminalFeatures):
    if features.mouse:
        stdout.write("\x1b[?1000l") # RESET_VT200_MOUSE
        stdout.write("\x1b[?1003l") # RESET_ANY_EVENT_MOUSE
        stdout.write("\x1b[?1006l") # RESET_ANY_EVENT_MOUSE
    if features.bracketed_paste:
        stdout.write("\x1b[?2004l") # reset bracketed paste mode, xterm.
    # leave altscreen after 
    if features.alternate_screen:
        stdout.write("\x1b[?1049l") # Alt screen
    stdout.flush()

class TerminalIO(ABC):
    @abstractmethod
    def run(self, *,callback: Callable, features: TerminalFeatures = ALL_FEATURES):
        ...
    
class WindowsTerminalIO(TerminalIO):
    def run(self, *, features: TerminalFeatures = ALL_FEATURES):
        stdin = sys.stdin
        stdout = sys.stdout
        try:
            stdin.buffer.read()
            enable_xterm_features(stdout, features)
        finally:
            disable_xterm_features(stdout, ALL_FEATURES)


class UnixTerminalIO(TerminalIO):
    def __init__(self) -> None:
        super().__init__()
        self.old_terminal_attrs: None | list[Any] = None


    def run(self, *,callback: Callable, features: TerminalFeatures = ALL_FEATURES):
        stdin = sys.stdin
        stdout = sys.stdout

        # unix specific setup
        import termios
        import tty
        fd = sys.stdin.fileno()
        self._old_terminal_atrs = termios.tcgetattr(fd)
        tty.setraw(fd)
        # end
        
        try:
            stdin.buffer.read()
            enable_xterm_features(stdout, features)
            ...
            while True:
                input = stdin.buffer.read(1)
                callback(input)
        finally:
            disable_xterm_features(stdout, ALL_FEATURES)



def create_terminal_io():
    IS_WINDOWS = sys.platform == "win32"
    if IS_WINDOWS:
        return WindowsTerminalIO()
    else:
        return UnixTerminalIO()

