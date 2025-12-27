import curses
from typing import NamedTuple
from ..classes import Coordinate

_curses_int_to_standard_key_name = {
    1: "ctrl+a",
    2: "ctrl+b",
    3: "ctrl+c",
    4: "ctrl+d",
    5: "ctrl+e",
    6: "ctrl+f",
    7: "ctrl+g",
    8: "ctrl+h",
    9: "tab", # same as ctrl i
    10: "enter", # same as ctrl j
    11: "ctrl+k",
    12: "ctrl+l",
    13: "enter", # same as ctrl m 
    14: "ctrl+n",
    15: "ctrl+o",
    16: "ctrl+p",
    17: "ctrl+q",
    18: "ctrl+r",
    19: "ctrl+s",
    20: "ctrl+t",
    21: "ctrl+u",
    22: "ctrl+v",
    23: "ctrl+w",
    24: "ctrl+x",
    25: "ctrl+y",
    26: "ctrl+z",
    27: "escape",
    28: "ctrl+\\",
    29: "ctrl+]",
    30: "ctrl+^",
    31: "ctrl+_",

    curses.KEY_BACKSPACE: "backspace",
    curses.KEY_ENTER: "enter",

    curses.KEY_UP: "up",
    curses.KEY_DOWN: "down",
    curses.KEY_LEFT: "left",
    curses.KEY_RIGHT: "right",

    curses.KEY_HOME: "home",
    curses.KEY_END: "end",
    curses.KEY_NPAGE: "pgdown",
    curses.KEY_PPAGE: "pgup",

    curses.KEY_DC: "delete",
    curses.KEY_IC: "insert",

    curses.KEY_F1: "f1",
    curses.KEY_F2: "f2",
    curses.KEY_F3: "f3",
    curses.KEY_F4: "f4",
    curses.KEY_F5: "f5",
    curses.KEY_F6: "f6",
    curses.KEY_F7: "f7",
    curses.KEY_F8: "f8",
    curses.KEY_F9: "f9",
    curses.KEY_F10: "f10",
    curses.KEY_F11: "f11",
    curses.KEY_F12: "f12",
    curses.KEY_F13: "f13",
    curses.KEY_F14: "f14",
    curses.KEY_F15: "f15",
    curses.KEY_F16: "f16",
    curses.KEY_F17: "f17",
    curses.KEY_F18: "f18",
    curses.KEY_F19: "f19",
    curses.KEY_F20: "f20",
}

class InputEvent(NamedTuple):
    key_event: str | None = None
    mouse_button_event: str | None = None
    mouse_position_event: Coordinate | None = None

def key_code_to_str(key: int | str):
    if isinstance(key, str):
        try:
            print(ord(key))
            ret = _curses_int_to_standard_key_name[ord(key)]
            return ret
        except KeyError:
            return key
    return _curses_int_to_standard_key_name[key]

def mouse_button_to_str(mouse_button: int) -> str:
    out = []
    print(bin(mouse_button))
    if mouse_button & curses.BUTTON_CTRL:
        out.append("ctrl")
    if mouse_button & curses.BUTTON_ALT:
        out.append("alt")
    if mouse_button & curses.BUTTON_SHIFT:
        out.append("shift")
        
    if mouse_button & curses.BUTTON1_PRESSED:
        out.append("left")
    elif mouse_button & curses.BUTTON1_RELEASED:
        out.append("left released")
    elif mouse_button & curses.BUTTON2_PRESSED:
        out.append("middle")
    elif mouse_button & curses.BUTTON2_RELEASED:
        out.append("middle released")
    elif mouse_button & curses.BUTTON3_PRESSED:
        out.append("right")
    elif mouse_button & curses.BUTTON3_RELEASED:
        out.append("right released")
    elif mouse_button & curses.BUTTON4_PRESSED:
        out.append("wheel up")
    elif mouse_button & curses.BUTTON5_PRESSED:
        out.append("wheel down")
    else:
        out.append("unknown")
    return "+".join(out)

def get_input_event(stdscr: curses.window) -> InputEvent:
    key = stdscr.get_wch()
    if key == 27: # esc, maybe alt
        try:
            stdscr.nodelay(True)
            second_key = stdscr.get_wch()
            return InputEvent(key_event="+".join(("alt", key_code_to_str(second_key))))
        except curses.error:
            return InputEvent(key_event="escape")
        finally:
            stdscr.nodelay(False)
    elif key == curses.KEY_MOUSE:
        try:
            _, x, y, _, state = curses.getmouse()
            return InputEvent(
                mouse_button_event=mouse_button_to_str(state),
                mouse_position_event=Coordinate(x, y),
            )
        except curses.error:
            pass
    return InputEvent(key_event=key_code_to_str(key))

