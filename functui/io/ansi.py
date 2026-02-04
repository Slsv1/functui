from ..classes import *
from typing import Callable, Iterable
from dataclasses import dataclass


from functools import cache
def default_color_to_fg_ansi(color: Color):
    if isinstance(color, int):
        if color == -1:
            return f"\033[39m"
        return f"\033[38:5:{color}m"
    else:
        return f"\033[38;2;{color.r};{color.g};{color.b}m"

def default_color_to_bg_ansi(color: Color):
    if isinstance(color, int):
        if color == -1:
            return f"\033[49m"
        return f"\033[48:5:{color}m"
    else:
        return f"\033[48;2;{color.r};{color.g};{color.b}m"

@cache
def style_to_ansi(style: StyleAttr):
    out = []
    if StyleAttr.BOLD in style:
        out.append("\033[1m")
    if StyleAttr.ITALIC in style:
        out.append("\033[3m")
    if StyleAttr.UNDERLINE in style:
        out.append("\033[4m")
    if StyleAttr.REVERSE in style:
        out.append("\033[7m")
    if StyleAttr.STRIKE_THROUGH in style:
        out.append("\033[9m")
    if StyleAttr.DIM in style:
        out.append("\033[2m")
    return "".join(out)


ANSI_RESET_STYLES = "\033[0m"

def render_ansi(screen: Screen) -> str:
    out = []
    lines = screen.split_by_lines()
    curr_style = StyleAttr(0)
    curr_fg = Color4.RESET
    curr_bg = Color4.RESET
    for line in lines:
        for pixel in line:
            line_str = []
            if curr_style != pixel.style.attrs:
                style_changes = (curr_style ^ pixel.style.attrs)
                new_style =  style_changes & pixel.style.attrs
                removed_style = bool(style_changes & curr_style)
                curr_style = pixel.style.attrs
                line_str.extend(
                    [ANSI_RESET_STYLES, style_to_ansi(pixel.style.attrs)]\
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

