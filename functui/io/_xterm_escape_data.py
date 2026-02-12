# data from (https://github.com/prompt-toolkit/python-prompt-toolkit/blob/main/src/prompt_toolkit/input/ansi_escape_sequences.py)

SUQUENCE_TO_KEY: dict[str, str] = {
    # Control keys.
    "\x00": "ctrl+@",  # Control-At (Also for Ctrl-Space)
    "\x01": "ctrl+a",  # Control-A (home)
    "\x02": "ctrl+b",  # Control-B (emacs cursor left)
    "\x03": "ctrl+c",  # Control-C (interrupt)
    "\x04": "ctrl+d",  # Control-D (exit)
    "\x05": "ctrl+e",  # Control-E (end)
    "\x06": "ctrl+f",  # Control-F (cursor forward)
    "\x07": "ctrl+g",  # Control-G
    "\x08": "ctrl+h",  # Control-H (8) (Identical to '\b')
    "\x09": "tab",  # Control-I (9) (Identical to '\t')
    "\x0a": "enter",  # Control-J (10) (Identical to '\n')
    "\x0b": "ctrl+k",  # Control-K (delete until end of line; vertical tab)
    "\x0c": "ctrl+l",  # Control-L (clear; form feed)
    "\x0d": "enter",  # Control-M (13) (Identical to '\r')
    "\x0e": "ctrl+n",  # Control-N (14) (history forward)
    "\x0f": "ctrl+o",  # Control-O (15)
    "\x10": "ctrl+p",  # Control-P (16) (history back)
    "\x11": "ctrl+q",  # Control-Q
    "\x12": "ctrl+r",  # Control-R (18) (reverse search)
    "\x13": "ctrl+s",  # Control-S (19) (forward search)
    "\x14": "ctrl+y",  # Control-T
    "\x15": "ctrl+u",  # Control-U
    "\x16": "ctrl+v",  # Control-V
    "\x17": "ctrl+w",  # Control-W
    "\x18": "ctrl+x",  # Control-X
    "\x19": "ctrl+y",  # Control-Y (25)
    "\x1a": "ctrl+z",  # Control-Z
    "\x1b": "escape",  # Also Control-[
    "\x9b": "shift+escape",
    "\x1c": "ctrl+\\",  # Both Control-\ (also Ctrl-| )
    "\x1d": "ctrl+]",  # Control-]
    "\x1e": "ctrl+^",  # Control-^
    "\x1f": "ctrl+_",  # Control-underscore (Also for Ctrl-hyphen.)
    # ASCII Delete (0x7f)
    # Vt220 (and Linux terminal) send this when pressing backspace. We map this
    # to ControlH, because that will make it easier to create key bindings that
    # work everywhere, with the trade-off that it's no longer possible to
    # handle backspace and control-h individually for the few terminals that
    # support it. (Most terminals send ControlH when backspace is pressed.)
    # See: http://www.ibb.net/~anne/keyboard.html
    "\x7f": "backspace",
    # --
    # Various
    "\x1b[1~": "home",  # tmux
    "\x1b[2~": "insert",
    "\x1b[3~": "delete",
    "\x1b[4~": "end",  # tmux
    "\x1b[5~": "page up",
    "\x1b[6~": "page down",
    "\x1b[7~": "home",  # xrvt
    "\x1b[8~": "end",  # xrvt
    "\x1b[Z": "shift+tab",  # shift + tab
    "\x1b\x09": "shift+tab",  # Linux console
    "\x1b[~": "shift+tab",  # Windows console
    # --
    # Function keys.
    "\x1bOP": "f1",
    "\x1bOQ": "f2",
    "\x1bOR": "f3",
    "\x1bOS": "f4",
    "\x1b[[A": "f1",  # Linux console.
    "\x1b[[B": "f2",  # Linux console.
    "\x1b[[C": "f3",  # Linux console.
    "\x1b[[D": "f4",  # Linux console.
    "\x1b[[E": "f5",  # Linux console.
    "\x1b[11~": "f1",  # rxvt-unicode
    "\x1b[12~": "f2",  # rxvt-unicode
    "\x1b[13~": "f3",  # rxvt-unicode
    "\x1b[14~": "f4",  # rxvt-unicode
    "\x1b[15~": "f5",
    "\x1b[17~": "f6",
    "\x1b[18~": "f7",
    "\x1b[19~": "f8",
    "\x1b[20~": "f9",
    "\x1b[21~": "f10",
    "\x1b[23~": "f11",
    "\x1b[24~": "f12",
    "\x1b[25~": "f13",
    "\x1b[26~": "f14",
    "\x1b[28~": "f15",
    "\x1b[29~": "f16",
    "\x1b[31~": "f17",
    "\x1b[32~": "f18",
    "\x1b[33~": "f19",
    "\x1b[34~": "f20",
    # Xterm
    "\x1b[1;2P": "f13",
    "\x1b[1;2Q": "f14",
    # '\x1b[1;2R': Keys.F15,  # Conflicts with CPR response.
    "\x1b[1;2S": "f16",
    "\x1b[15;2~": "f17",
    "\x1b[17;2~": "f18",
    "\x1b[18;2~": "f19",
    "\x1b[19;2~": "f20",
    "\x1b[20;2~": "f21",
    "\x1b[21;2~": "f22",
    "\x1b[23;2~": "f23",
    "\x1b[24;2~": "f24",
    # --
    # CSI 27 disambiguated modified "other" keys (xterm)
    # Ref: https://invisible-island.net/xterm/modified-keys.html
    # These are currently unsupported, so just re-map some common ones to the
    # unmodified versions
    # "\x1b[27;2;13~": Keys.ControlM,  # Shift + Enter
    # "\x1b[27;5;13~": Keys.ControlM,  # Ctrl + Enter
    # "\x1b[27;6;13~": Keys.ControlM,  # Ctrl + Shift + Enter
    # # --
    # # Control + function keys.
    # "\x1b[1;5P": Keys.ControlF1,
    # "\x1b[1;5Q": Keys.ControlF2,
    # # "\x1b[1;5R": Keys.ControlF3,  # Conflicts with CPR response.
    # "\x1b[1;5S": Keys.ControlF4,
    # "\x1b[15;5~": Keys.ControlF5,
    # "\x1b[17;5~": Keys.ControlF6,
    # "\x1b[18;5~": Keys.ControlF7,
    # "\x1b[19;5~": Keys.ControlF8,
    # "\x1b[20;5~": Keys.ControlF9,
    # "\x1b[21;5~": Keys.ControlF10,
    # "\x1b[23;5~": Keys.ControlF11,
    # "\x1b[24;5~": Keys.ControlF12,
    # "\x1b[1;6P": Keys.ControlF13,
    # "\x1b[1;6Q": Keys.ControlF14,
    # # "\x1b[1;6R": Keys.ControlF15,  # Conflicts with CPR response.
    # "\x1b[1;6S": Keys.ControlF16,
    # "\x1b[15;6~": Keys.ControlF17,
    # "\x1b[17;6~": Keys.ControlF18,
    # "\x1b[18;6~": Keys.ControlF19,
    # "\x1b[19;6~": Keys.ControlF20,
    # "\x1b[20;6~": Keys.ControlF21,
    # "\x1b[21;6~": Keys.ControlF22,
    # "\x1b[23;6~": Keys.ControlF23,
    # "\x1b[24;6~": Keys.ControlF24,
    # # --
    # # Tmux (Win32 subsystem) sends the following scroll events.
    # "\x1b[62~": Keys.ScrollUp,
    # "\x1b[63~": Keys.ScrollDown,
    # "\x1b[200~": Keys.BracketedPaste,  # Start of bracketed paste.
    # # --
    # # Sequences generated by numpad 5. Not sure what it means. (It doesn't
    # # appear in 'infocmp'. Just ignore.
    # "\x1b[E": Keys.Ignore,  # Xterm.
    # "\x1b[G": Keys.Ignore,  # Linux console.
    # # --
    # # Meta/control/escape + pageup/pagedown/insert/delete.
    # "\x1b[3;2~": Keys.ShiftDelete,  # xterm, gnome-terminal.
    # "\x1b[5;2~": Keys.ShiftPageUp,
    # "\x1b[6;2~": Keys.ShiftPageDown,
    # "\x1b[2;3~": (Keys.Escape, Keys.Insert),
    # "\x1b[3;3~": (Keys.Escape, Keys.Delete),
    # "\x1b[5;3~": (Keys.Escape, Keys.PageUp),
    # "\x1b[6;3~": (Keys.Escape, Keys.PageDown),
    # "\x1b[2;4~": (Keys.Escape, Keys.ShiftInsert),
    # "\x1b[3;4~": (Keys.Escape, Keys.ShiftDelete),
    # "\x1b[5;4~": (Keys.Escape, Keys.ShiftPageUp),
    # "\x1b[6;4~": (Keys.Escape, Keys.ShiftPageDown),
    # "\x1b[3;5~": Keys.ControlDelete,  # xterm, gnome-terminal.
    # "\x1b[5;5~": Keys.ControlPageUp,
    # "\x1b[6;5~": Keys.ControlPageDown,
    # "\x1b[3;6~": Keys.ControlShiftDelete,
    # "\x1b[5;6~": Keys.ControlShiftPageUp,
    # "\x1b[6;6~": Keys.ControlShiftPageDown,
    # "\x1b[2;7~": (Keys.Escape, Keys.ControlInsert),
    # "\x1b[5;7~": (Keys.Escape, Keys.ControlPageDown),
    # "\x1b[6;7~": (Keys.Escape, Keys.ControlPageDown),
    # "\x1b[2;8~": (Keys.Escape, Keys.ControlShiftInsert),
    # "\x1b[5;8~": (Keys.Escape, Keys.ControlShiftPageDown),
    # "\x1b[6;8~": (Keys.Escape, Keys.ControlShiftPageDown),
    # # --
    # # Arrows.
    # # (Normal cursor mode).
    # "\x1b[A": Keys.Up,
    # "\x1b[B": Keys.Down,
    # "\x1b[C": Keys.Right,
    # "\x1b[D": Keys.Left,
    # "\x1b[H": Keys.Home,
    # "\x1b[F": Keys.End,
    # # Tmux sends following keystrokes when control+arrow is pressed, but for
    # # Emacs ansi-term sends the same sequences for normal arrow keys. Consider
    # # it a normal arrow press, because that's more important.
    # # (Application cursor mode).
    # "\x1bOA": Keys.Up,
    # "\x1bOB": Keys.Down,
    # "\x1bOC": Keys.Right,
    # "\x1bOD": Keys.Left,
    # "\x1bOF": Keys.End,
    # "\x1bOH": Keys.Home,
    # # Shift + arrows.
    # "\x1b[1;2A": Keys.ShiftUp,
    # "\x1b[1;2B": Keys.ShiftDown,
    # "\x1b[1;2C": Keys.ShiftRight,
    # "\x1b[1;2D": Keys.ShiftLeft,
    # "\x1b[1;2F": Keys.ShiftEnd,
    # "\x1b[1;2H": Keys.ShiftHome,
    # # Meta + arrow keys. Several terminals handle this differently.
    # # The following sequences are for xterm and gnome-terminal.
    # #     (Iterm sends ESC followed by the normal arrow_up/down/left/right
    # #     sequences, and the OSX Terminal sends ESCb and ESCf for "alt
    # #     arrow_left" and "alt arrow_right." We don't handle these
    # #     explicitly, in here, because would could not distinguish between
    # #     pressing ESC (to go to Vi navigation mode), followed by just the
    # #     'b' or 'f' key. These combinations are handled in
    # #     the input processor.)
    # "\x1b[1;3A": (Keys.Escape, Keys.Up),
    # "\x1b[1;3B": (Keys.Escape, Keys.Down),
    # "\x1b[1;3C": (Keys.Escape, Keys.Right),
    # "\x1b[1;3D": (Keys.Escape, Keys.Left),
    # "\x1b[1;3F": (Keys.Escape, Keys.End),
    # "\x1b[1;3H": (Keys.Escape, Keys.Home),
    # # Alt+shift+number.
    # "\x1b[1;4A": (Keys.Escape, Keys.ShiftDown),
    # "\x1b[1;4B": (Keys.Escape, Keys.ShiftUp),
    # "\x1b[1;4C": (Keys.Escape, Keys.ShiftRight),
    # "\x1b[1;4D": (Keys.Escape, Keys.ShiftLeft),
    # "\x1b[1;4F": (Keys.Escape, Keys.ShiftEnd),
    # "\x1b[1;4H": (Keys.Escape, Keys.ShiftHome),
    # # Control + arrows.
    # "\x1b[1;5A": Keys.ControlUp,  # Cursor Mode
    # "\x1b[1;5B": Keys.ControlDown,  # Cursor Mode
    # "\x1b[1;5C": Keys.ControlRight,  # Cursor Mode
    # "\x1b[1;5D": Keys.ControlLeft,  # Cursor Mode
    # "\x1b[1;5F": Keys.ControlEnd,
    # "\x1b[1;5H": Keys.ControlHome,
    # # Tmux sends following keystrokes when control+arrow is pressed, but for
    # # Emacs ansi-term sends the same sequences for normal arrow keys. Consider
    # # it a normal arrow press, because that's more important.
    # "\x1b[5A": Keys.ControlUp,
    # "\x1b[5B": Keys.ControlDown,
    # "\x1b[5C": Keys.ControlRight,
    # "\x1b[5D": Keys.ControlLeft,
    # "\x1bOc": Keys.ControlRight,  # rxvt
    # "\x1bOd": Keys.ControlLeft,  # rxvt
    # # Control + shift + arrows.
    # "\x1b[1;6A": Keys.ControlShiftDown,
    # "\x1b[1;6B": Keys.ControlShiftUp,
    # "\x1b[1;6C": Keys.ControlShiftRight,
    # "\x1b[1;6D": Keys.ControlShiftLeft,
    # "\x1b[1;6F": Keys.ControlShiftEnd,
    # "\x1b[1;6H": Keys.ControlShiftHome,
    # # Control + Meta + arrows.
    # "\x1b[1;7A": (Keys.Escape, Keys.ControlDown),
    # "\x1b[1;7B": (Keys.Escape, Keys.ControlUp),
    # "\x1b[1;7C": (Keys.Escape, Keys.ControlRight),
    # "\x1b[1;7D": (Keys.Escape, Keys.ControlLeft),
    # "\x1b[1;7F": (Keys.Escape, Keys.ControlEnd),
    # "\x1b[1;7H": (Keys.Escape, Keys.ControlHome),
    # # Meta + Shift + arrows.
    # "\x1b[1;8A": (Keys.Escape, Keys.ControlShiftDown),
    # "\x1b[1;8B": (Keys.Escape, Keys.ControlShiftUp),
    # "\x1b[1;8C": (Keys.Escape, Keys.ControlShiftRight),
    # "\x1b[1;8D": (Keys.Escape, Keys.ControlShiftLeft),
    # "\x1b[1;8F": (Keys.Escape, Keys.ControlShiftEnd),
    # "\x1b[1;8H": (Keys.Escape, Keys.ControlShiftHome),
    # # Meta + arrow on (some?) Macs when using iTerm defaults (see issue #483).
    # "\x1b[1;9A": (Keys.Escape, Keys.Up),
    # "\x1b[1;9B": (Keys.Escape, Keys.Down),
    # "\x1b[1;9C": (Keys.Escape, Keys.Right),
    # "\x1b[1;9D": (Keys.Escape, Keys.Left),
    # # --
    # # Control/shift/meta + number in mintty.
    # # (c-2 will actually send c-@ and c-6 will send c-^.)
    # "\x1b[1;5p": Keys.Control0,
    # "\x1b[1;5q": Keys.Control1,
    # "\x1b[1;5r": Keys.Control2,
    # "\x1b[1;5s": Keys.Control3,
    # "\x1b[1;5t": Keys.Control4,
    # "\x1b[1;5u": Keys.Control5,
    # "\x1b[1;5v": Keys.Control6,
    # "\x1b[1;5w": Keys.Control7,
    # "\x1b[1;5x": Keys.Control8,
    # "\x1b[1;5y": Keys.Control9,
    # "\x1b[1;6p": Keys.ControlShift0,
    # "\x1b[1;6q": Keys.ControlShift1,
    # "\x1b[1;6r": Keys.ControlShift2,
    # "\x1b[1;6s": Keys.ControlShift3,
    # "\x1b[1;6t": Keys.ControlShift4,
    # "\x1b[1;6u": Keys.ControlShift5,
    # "\x1b[1;6v": Keys.ControlShift6,
    # "\x1b[1;6w": Keys.ControlShift7,
    # "\x1b[1;6x": Keys.ControlShift8,
    # "\x1b[1;6y": Keys.ControlShift9,
    # "\x1b[1;7p": (Keys.Escape, Keys.Control0),
    # "\x1b[1;7q": (Keys.Escape, Keys.Control1),
    # "\x1b[1;7r": (Keys.Escape, Keys.Control2),
    # "\x1b[1;7s": (Keys.Escape, Keys.Control3),
    # "\x1b[1;7t": (Keys.Escape, Keys.Control4),
    # "\x1b[1;7u": (Keys.Escape, Keys.Control5),
    # "\x1b[1;7v": (Keys.Escape, Keys.Control6),
    # "\x1b[1;7w": (Keys.Escape, Keys.Control7),
    # "\x1b[1;7x": (Keys.Escape, Keys.Control8),
    # "\x1b[1;7y": (Keys.Escape, Keys.Control9),
    # "\x1b[1;8p": (Keys.Escape, Keys.ControlShift0),
    # "\x1b[1;8q": (Keys.Escape, Keys.ControlShift1),
    # "\x1b[1;8r": (Keys.Escape, Keys.ControlShift2),
    # "\x1b[1;8s": (Keys.Escape, Keys.ControlShift3),
    # "\x1b[1;8t": (Keys.Escape, Keys.ControlShift4),
    # "\x1b[1;8u": (Keys.Escape, Keys.ControlShift5),
    # "\x1b[1;8v": (Keys.Escape, Keys.ControlShift6),
    # "\x1b[1;8w": (Keys.Escape, Keys.ControlShift7),
    # "\x1b[1;8x": (Keys.Escape, Keys.ControlShift8),
    # "\x1b[1;8y": (Keys.Escape, Keys.ControlShift9),
}
