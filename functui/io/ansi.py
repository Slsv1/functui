from ..classes import *
from typing import Callable, Iterable
from dataclasses import dataclass


from functools import cache
def default_color_to_fg_ansi(color: Color):
    return f"\033[{color.value}m"

def default_color_to_bg_ansi(color: Color):
    return f"\033[{color.value + 10}m"

@cache
def style_to_ansi(style: CharStyle):
    out = []
    if CharStyle.BOLD in style:
        out.append("\033[1m")
    if CharStyle.ITALIC in style:
        out.append("\033[3m")
    if CharStyle.UNDERLINED in style:
        out.append("\033[4m")
    if CharStyle.REVERSED in style:
        out.append("\033[7m")
    if CharStyle.STRIKE_THROUGH in style:
        out.append("\033[9m")
    return "".join(out)

ANSI_RESET_STYLES = "\033[0m"

def render_ansi(screen: Screen) -> str:
    out = []
    lines = screen.split_by_lines()
    curr_style = CharStyle(0)
    curr_fg = Color.RESET
    curr_bg = Color.RESET
    for line in lines:
        for pixel in line:
            line_str = []
            if curr_style != pixel.style.char_style:
                style_changes = (curr_style ^ pixel.style.char_style)
                new_style =  style_changes & pixel.style.char_style
                removed_style = bool(style_changes & curr_style)
                curr_style = pixel.style.char_style
                line_str.extend(
                    [ANSI_RESET_STYLES, style_to_ansi(pixel.style.char_style)]\
                    if removed_style\
                    else [style_to_ansi(new_style)]
                )
            if curr_fg != pixel.style.fg and pixel.style.fg is not None:
                curr_fg = pixel.style.fg
                line_str.append(default_color_to_fg_ansi(curr_fg))
            if curr_bg != pixel.style.bg and pixel.style.bg is not None:
                curr_bg = pixel.style.bg
                line_str.append(default_color_to_bg_ansi(curr_bg))
            line_str.append(pixel.char)
            out.append("".join(line_str))
        out.append("\n")
    return "".join(out[:-1]) # -1 to remove the \n on the end


def _ansi_go_up(y):
    return f"\033[{y}A"

def result_to_str(result: Result) -> str:
    data = result.try_data(ResultCreatedWith)
    if data is None:
        raise AssertionError("Result has no ResultCreatedWith data. If possible please use get_result() function to get a result.")
    screen = Screen(data.screen_size.width, data.screen_size.height)
    screen.apply_draw_commands(data.measure_text_func, result.get_commands()) # 20 %
    return render_ansi(screen) # 30 %

def layout_to_str(layout: Layout, dimensions: Rect) -> str:
    return result_to_str(layout_to_result(dimensions=dimensions, layout=layout))

