"""Functions to convert layouts to styled strings that can be rendered in a terminal."""
from ._color import Color, Color4, TerminalColor
from ._classes import StyleAttr, Strip, compose_strips, ComputedStyle, Screen, Layout, Frame, ResultData
from ._geometry import Rect
from typing import TYPE_CHECKING, Sequence
from dataclasses import dataclass

if TYPE_CHECKING:
    from ._xterm import TerminalIO




from functools import cache

@cache
def _default_color_to_fg_ansi(color: TerminalColor):
    if isinstance(color, int):
        if color == -1:
            return f"\033[39m"
        return f"\033[38;5;{color}m"
    else:
        return f"\033[38;2;{color.r};{color.g};{color.b}m"
@cache
def _default_color_to_bg_ansi(color: TerminalColor):
    if isinstance(color, int):
        if color == -1:
            return f"\033[49m"
        return f"\033[48;5;{color}m"
    else:
        return f"\033[48;2;{color.r};{color.g};{color.b}m"

@cache
def _style_to_ansi(style: StyleAttr):
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
def render_ansi(strips: Sequence[Sequence[Strip]]) -> str:
    out = []

    curr_attrs = StyleAttr(0)
    curr_fg = Color4.RESET
    curr_bg = Color4.RESET
    
    # Pre-compute the reset color ANSI strings to avoid function call overhead
    reset_fg_ansi = _default_color_to_fg_ansi(Color4.RESET)
    reset_bg_ansi = _default_color_to_bg_ansi(Color4.RESET)

    for line in strips:
        for (pixel_style, pixel_char) in compose_strips(line):
            pixel_attrs = pixel_style.attrs
            
            # 1. Handle Style Changes
            if curr_attrs != pixel_attrs:
                attr_changes = curr_attrs ^ pixel_attrs
                new_attrs = attr_changes & pixel_attrs
                removed_style = bool(attr_changes & curr_attrs)
                curr_attrs = pixel_attrs
                
                if removed_style:
                    out.append(ANSI_RESET_STYLES)
                    out.append(_style_to_ansi(pixel_attrs))
                    out.append(_default_color_to_fg_ansi(curr_fg))
                    out.append(_default_color_to_bg_ansi(curr_bg))
                else:
                    out.append(_style_to_ansi(new_attrs))

            # 2. Handle Foreground Color Changes
            p_fg = pixel_style.fg
            if curr_fg != p_fg and p_fg is not None:
                curr_fg = p_fg
                out.append(_default_color_to_fg_ansi(curr_fg))

            # 3. Handle Background Color Changes
            p_bg = pixel_style.bg
            if curr_bg != p_bg and p_bg is not None:
                curr_bg = p_bg
                out.append(_default_color_to_bg_ansi(curr_bg))

            # 4. Append the character
            out.append(pixel_char)
        # reset style at the end of each row
        if curr_attrs != StyleAttr(0) or curr_fg != Color4.RESET or curr_bg != Color4.RESET:
            curr_attrs = StyleAttr(0)
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
    screen = Screen()
    screen.set_dimensions(dimensions)
    screen.overlay_layout(layout)
    # print("strips: ----------------")
    # for s in screen.strips:
    #     for ss in s:
    #         print(ss.content)
    # print("end --------------------")
    return render_ansi(screen.strips)


def render_fit_terminal(terminal: TerminalIO, screen: Screen, layout: Layout) -> ResultData:
    terminal_dimensions = terminal.get_terminal_size()

    if screen.dimensions != terminal_dimensions:
        screen.set_dimensions(terminal_dimensions)

    screen.clear()
    res = screen.overlay_layout(layout)
    ansi_str = render_ansi(screen.strips)
    terminal.print("\x1b[H" + ansi_str + "\033[39m\033[49m")
    return res

def render_fit_screen(terminal: TerminalIO, screen: Screen, layout: Layout):
    screen.clear()
    res = screen.overlay_layout(layout)
    ansi_str = render_ansi(screen.strips)
    terminal.print("\x1b[H" + ansi_str + "\033[39m\033[49m")
    return res
