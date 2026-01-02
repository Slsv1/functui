import curses
import sys
from typing import NamedTuple, Any, Callable
from ..classes import *
from functools import cache

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
    curses.KEY_NPAGE: "page down",
    curses.KEY_PPAGE: "page up",

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


def key_code_to_str(key: int | str):
    if isinstance(key, str):
        try:
            ret = _curses_int_to_standard_key_name[ord(key)]
            return ret
        except KeyError:
            return key
    try:
        return _curses_int_to_standard_key_name[key]
    except:
        return "unknown"

def mouse_button_to_str(mouse_button: int) -> str:
    out = []
    if mouse_button & curses.BUTTON_CTRL:
        out.append("ctrl")
    if mouse_button & curses.BUTTON_ALT:
        out.append("alt")
    if mouse_button & curses.BUTTON_SHIFT:
        out.append("shift")

    if mouse_button & curses.BUTTON1_PRESSED:
        out.append("left mouse")
    elif mouse_button & curses.BUTTON1_RELEASED:
        out.append("left mouse released")
    elif mouse_button & curses.BUTTON2_PRESSED:
        out.append("middle mouse")
    elif mouse_button & curses.BUTTON2_RELEASED:
        out.append("middle mouse released")
    elif mouse_button & curses.BUTTON3_PRESSED:
        out.append("right mouse")
    elif mouse_button & curses.BUTTON3_RELEASED:
        out.append("right mouse released")
    elif mouse_button & curses.BUTTON4_PRESSED:
        out.append("mouse wheel up")
    elif mouse_button & curses.BUTTON5_PRESSED:
        out.append("mouse wheel down")
    else:
        out.append("unknown")
    return "+".join(out)

def wrapper(func: Callable[[curses.window], Any]):
    def wrapped_func(stdscr):
        curses.curs_set(0)
        curses.raw()
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        curses.mouseinterval(0)
        print('\033[?1003h') # xterm enable reporting of all mouse events
        func(stdscr)
    curses.wrapper(wrapped_func)


def get_input_event(stdscr: curses.window) -> InputEvent:
    key = stdscr.get_wch()
    if key == 27: # esc, maybe alt
        try:
            stdscr.nodelay(True)
            second_key = stdscr.get_wch()
            return InputEvent(key_event="+".join(["alt", key_code_to_str(second_key)]))
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

@cache
def char_style_to_attr(style: CharStyle) -> int:
    out = 0
    if style & CharStyle.BOLD:
        out |= curses.A_BOLD
    if style & CharStyle.ITALIC:
        out |= curses.A_ITALIC
    if style & CharStyle.REVERSED:
        out |= curses.A_REVERSE
    if style & CharStyle.STRIKE_THROUGH:
        out |= curses.A_HORIZONTAL
    if style & CharStyle.UNDERLINED:
        out |= curses.A_UNDERLINE
    return out

def color_to_curses(clr: Color):
    out = clr.value - 30 # Ansi assignd index 30 for black (1st color) while curses assigns 0
    # match clr:
    #
    #     case Color.BLACK:
    #         return curses.COLOR_BLACK
    #     case Color.RED:
    #         return curses.COLOR_RED
    #     case Color.GREEN:
    #         return curses.COLOR_GREEN
    #     case Color.YELLOW:
    #         return curses.COLOR_YELLOW
    #     case Color.WHITE:
    #         return curses.COLOR_WHITE
    #     case Color.BLACK:
    #         return curses.COLOR_BLACK
        # BLUE = 34
        # MAGENTA = 35
        # CYAN = 36
        # WHITE = 37
        # RESET = 39
    if out > 7: # don't do anything with reset
        return 0
    return out

pair_cache: dict[tuple[int, int], int] = {}
def init_pair_from_style(i: int, style: Style):
    curr_fg, curr_bg = curses.pair_content(i)
    new_fg = color_to_curses(style.fg) if style.fg else curr_fg
    new_bg = color_to_curses(style.bg) if style.bg else curr_bg
    try:
        return pair_cache[(new_fg, new_bg)]
    except KeyError:
        new_pair_number = len(pair_cache) + 1
        curses.init_pair(new_pair_number, new_fg, new_bg)
        pair_cache[(new_fg, new_bg)] = new_pair_number
        return new_pair_number
    return i


def draw_result(result: Result, stdscr: curses.window):
    data = result.try_data(ResultCreatedWith)
    if data is None:
        raise AssertionError("bahh")
    pair_number = 1
    for command in result.get_commands():
        if isinstance(command, DrawPixel):
            pair_number = init_pair_from_style(pair_number, command.pixel.style)
            stdscr.addch(
                command.at.y,
                command.at.x,
                command.pixel.char,
                char_style_to_attr(command.pixel.style.char_style) | curses.color_pair(pair_number)
            )
        elif isinstance(command, DrawStringLine):
            pair_number = init_pair_from_style(pair_number, command.string[0].style)
            stdscr.addstr(
                command.at.y,
                command.at.x,
                "".join([i.char for i in command.string if i.char_type != CharType.WIDE_TAIL]),
                char_style_to_attr(command.string[0].style.char_style) | curses.color_pair(pair_number)
            )
        elif isinstance(command, DrawBox):
            pair_number = init_pair_from_style(pair_number, command.fill.style)
            s = [command.box.width * command.fill.char for _ in range(command.box.height)]
            for dy, line in enumerate(s):
                stdscr.addstr(
                    command.box.position.y + dy,
                    command.box.position.x,
                    line,
                    char_style_to_attr(command.fill.style.char_style) | curses.color_pair(pair_number)
                )



    # screen = Screen(data.screen_size.width, data.screen_size.height)
    # screen.apply_draw_commands(data.measure_text_func, result.get_commands())
    # lines = screen.split_by_lines()
    #
    # curr_style = CharStyle(0)
    # curr_fg = Color.RESET
    # curr_bg = Color.RESET
    # # curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    # for y, line in enumerate(lines):
    #     line_str = []
    #     for x, pixel in enumerate(line):
    #         if pixel.char_type == CharType.WIDE_TAIL:
    #             continue
    #         if curr_style != pixel.style.char_style:
    #             if line_str:
    #                 stdscr.addstr(
    #                     y,
    #                     x - data.measure_text_func("".join(line_str)),
    #                     "".join(line_str),
    #                     char_style_to_attr(curr_style) | pair_number
    #                 )
    #                 line_str.clear()
    #             curr_style = pixel.style.char_style
    #         if (curr_fg, curr_bg) != (pixel.style.fg, pixel.style.bg):
    #             if line_str:
    #                 stdscr.addstr(
    #                     y,
    #                     x - data.measure_text_func("".join(line_str)),
    #                     "".join(line_str),
    #                     char_style_to_attr(curr_style) | pair_number
    #                 )
    #                 line_str.clear()
    #             pair_number = init_pair_from_style(pair_number, pixel.style)
    #             curr_fg = pixel.style.fg
    #             curr_bg = pixel.style.bg
    #         line_str.append(pixel.char)
    #     if line_str:
    #         stdscr.addstr(
    #             y,
    #             len(line) - len(line_str),
    #             "".join(line_str),
    #             char_style_to_attr(curr_style) | pair_number
    #         )







