"""Functions to convert layouts to styled strings that can be rendered in a terminal."""
from ..classes import *
from typing import Callable, Iterable
from dataclasses import dataclass


from functools import cache

from ..classes import stored_to_color

@cache
def default_color_to_fg_ansi(color: Color):
    if isinstance(color, int):
        if color == 256:
            return f"\033[39m"
        return f"\033[38;5;{color}m"
    else:
        return f"\033[38;2;{color.r};{color.g};{color.b}m"
@cache
def default_color_to_bg_ansi(color: Color):
    if isinstance(color, int):
        if color == 256:
            return f"\033[49m"
        return f"\033[48;5;{color}m"
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
    if StyleAttr.BLINK in style:
        out.append("\033[5m")
    if StyleAttr.REVERSE in style:
        out.append("\033[7m")
    if StyleAttr.STRIKE_THROUGH in style:
        out.append("\033[9m")
    if StyleAttr.DIM in style:
        out.append("\033[2m")
    return "".join(out)


ANSI_RESET_STYLES = "\033[0m"

# def _render_ansi_old(screen: Screen) -> str:
#     out = []
#     lines = screen.split_by_lines()
#
#     for line in lines:
#         line.append(Pixel("", style=ComputedStyle(fg=Color4.RESET, bg=Color4.RESET)))
#
#     curr_style = StyleAttr(0)
#     curr_fg = Color4.RESET
#     curr_bg = Color4.RESET
#     for line in lines:
#         for pixel in line:
#             line_str = []
#             if curr_style != pixel.style.attrs:
#                 style_changes = (curr_style ^ pixel.style.attrs)
#                 new_style =  style_changes & pixel.style.attrs
#                 removed_style = bool(style_changes & curr_style)
#                 curr_style = pixel.style.attrs
#                 # apparantly ANSI_RESET_STYLES also resets color, so we need to set it back.
#                 line_str = \
#                     [ANSI_RESET_STYLES, style_to_ansi(pixel.style.attrs), default_color_to_fg_ansi(curr_fg), default_color_to_bg_ansi(curr_bg)]\
#                     if removed_style\
#                     else [style_to_ansi(new_style)]
#             if curr_fg != pixel.style.fg and pixel.style.fg is not None:
#                 curr_fg = pixel.style.fg
#                 line_str.append(default_color_to_fg_ansi(curr_fg))
#             if curr_bg != pixel.style.bg and pixel.style.bg is not None:
#                 curr_bg = pixel.style.bg
#                 line_str.append(default_color_to_bg_ansi(curr_bg))
#             if len(line_str):
#                 out.extend(line_str)
#             out.append(pixel.char)
#         out.append("\n")
#     return "".join(out[:-1]) # -1 to remove the \n on the end
def _render_ansi(screen: Screen) -> str:
    out = []

    curr_style = StyleAttr(0)
    curr_fg = Color4.RESET
    curr_bg = Color4.RESET
    
    # Pre-compute the reset color ANSI strings to avoid function call overhead
    reset_fg_ansi = default_color_to_fg_ansi(Color4.RESET)
    reset_bg_ansi = default_color_to_bg_ansi(Color4.RESET)

    for y in range(screen.height):
        for x in range(screen.width):
            index = screen._pos_to_index(Coordinate(x, y))
            pixel_style = StyleAttr(screen._style_data[index])
            pixel_char = screen._char_data[index]
            
            # 1. Handle Style Changes
            if curr_style != pixel_style:
                style_changes = curr_style ^ pixel_style
                new_style = style_changes & pixel_style
                removed_style = bool(style_changes & curr_style)
                curr_style = pixel_style
                
                if removed_style:
                    out.append(ANSI_RESET_STYLES)
                    out.append(style_to_ansi(pixel_style))
                    out.append(default_color_to_fg_ansi(curr_fg))
                    out.append(default_color_to_bg_ansi(curr_bg))
                else:
                    out.append(style_to_ansi(new_style))

            # 2. Handle Foreground Color Changes
            p_fg = stored_to_color(screen._fg_data[index])
            if curr_fg != p_fg and p_fg is not None:
                curr_fg = p_fg
                out.append(default_color_to_fg_ansi(curr_fg))

            # 3. Handle Background Color Changes
            p_bg = stored_to_color(screen._bg_data[index])
            if curr_bg != p_bg and p_bg is not None:
                curr_bg = p_bg
                out.append(default_color_to_bg_ansi(curr_bg))

            # 4. Append the character
            out.append(pixel_char)
            
        # reset style at the end of each row
        if curr_style != StyleAttr(0) or curr_fg != Color4.RESET or curr_bg != Color4.RESET:
            curr_style = StyleAttr(0)
            curr_fg = Color4.RESET
            curr_bg = Color4.RESET
            out.append(ANSI_RESET_STYLES)
            out.append(reset_fg_ansi)
            out.append(reset_bg_ansi)
            
        out.append("\n")

    return "".join(out[:-1]) if out else ""


def layout_to_str(layout: Layout, dimensions: Rect) -> str:
    """Convert a layout to a string with ansi escapecodes that can be displayed in a terminal.

    This is a shorthand for ``result_to_str(layout_to_result(...)))``.
    """
    screen = Screen(*dimensions)
    screen.draw_layout(layout)
    return _render_ansi(screen)

