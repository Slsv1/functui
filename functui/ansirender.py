from .classes import Color, CharStyle, CharType, MeasureTextFunc, Pixel, Coordinate, ResultData, Rect,\
    MeasureTextFunc, DrawBox, DrawPixel, DrawCommand, ResultCreatedWith, Result, Node,\
    layout_to_result
from typing import Callable, Iterable
from dataclasses import dataclass


def _get_default_data(width: int, height: int):
    return [[Pixel() for _ in range(width)] for _ in range(height)]

class Screen:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.wide_char_cutoff = "#"
        self._data: list[list[Pixel]] = _get_default_data(width, height)

    def get(self, pos: Coordinate) -> Pixel:
        return self._data[pos.y][pos.x]

    def set(self, pos: Coordinate, data: Pixel) -> None:
        """may error if out of range!!!"""
        self._data[pos.y][pos.x] = data
    def split_by_lines(self) -> list[list[Pixel]]:
        # BUG
        # right now wide chars wont be frickign yeah
        return self._data
        #     # current_row = tuple(i for i in current_row if i.char_type != CharType.WIDE_TAIL)
        #     out.append(current_row)
        # return out

    def apply_draw_commands(self, measure_text_func: Callable[[str], int],  draw_commands: Iterable[DrawCommand]):
        for command in draw_commands:
            if isinstance(command, DrawPixel):
                self.set(command.at, command.pixel)

            elif isinstance(command, DrawBox):
                box = command.box
                for x in range(box.offset.x, box.offset.x + box.width):
                    for y in range(box.offset.y, box.offset.y + box.height):
                        self.set(Coordinate(x, y), command.fill)
            else: #DrawStringLine
                for delta_x, pixel in enumerate(command.string):

                    at = Coordinate(command.at.x + delta_x, command.at.y)
                    self.set(at, pixel)
        self._clean_up_wide_chars()

    def _clean_up_wide_chars(self):
        # print("".join(str(i.char_type) for i in self._data))
        for line in self._data:
            for i, pixel in enumerate(line):
                if ((i+1) % self.width) == 0: # if on last char of line
                    continue
                next_pixel = line[i+1]
                # print("comparing", pixel.char_type, next_pixel.char_type)
                match (pixel.char_type, next_pixel.char_type):
                    case (CharType.NORMAL, CharType.NORMAL)\
                        | (CharType.WIDE_TAIL, CharType.NORMAL)\
                        | (CharType.WIDE_HEAD, CharType.WIDE_TAIL)\
                        | (CharType.NORMAL, CharType.WIDE_HEAD)\
                        | (CharType.WIDE_TAIL, CharType.WIDE_HEAD):
                        continue
                    case (CharType.WIDE_HEAD, CharType.WIDE_HEAD)\
                        | (CharType.WIDE_HEAD, CharType.NORMAL):
                        line[i] = pixel.with_char_type(CharType.NORMAL)\
                            .with_char(self.wide_char_cutoff)
                    case _: # [NORMAL, WIDE_TAIL] | [WIDE_TAIL, WIDE_TAIL]
                        line[i+1] = next_pixel.with_char_type(CharType.NORMAL)\
                            .with_char(self.wide_char_cutoff)
        # print("".join(str(i.char_type) for i in self._data))



# if last char is wide_head, meake it normal

# N N -> N N
# T N -> T N
# H T -> H T
# N H -> N H
# T H -> T H

# convert next to normal
# N T -> N N
# T T -> T N

# convert current to normal (notice it is only head that can be converted)
# H H -> N H
# H N -> N N
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
            pixel_str = []
            if curr_style != pixel.style:
                style_changes = (curr_style ^ pixel.style)
                new_style =  style_changes & pixel.style
                removed_style = bool(style_changes & curr_style)
                curr_style = pixel.style
                pixel_str.extend(
                    [ANSI_RESET_STYLES, style_to_ansi(pixel.style)]\
                    if removed_style\
                    else [style_to_ansi(new_style)]
                )
            if curr_fg != pixel.fg_color:
                curr_fg = pixel.fg_color
                pixel_str.append(default_color_to_fg_ansi(curr_fg))
            if curr_bg != pixel.bg_color:
                curr_bg = pixel.bg_color
                pixel_str.append(default_color_to_bg_ansi(curr_bg))
            pixel_str.append(pixel.char)
            out.append("".join(pixel_str))
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

def layout_to_str(layout: Node, dimensions: Rect) -> str:
    return result_to_str(layout_to_result(dimensions=dimensions, layout=layout))
