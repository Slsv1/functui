# type Points = tuple[int, int, int, int, int, int, int, int]
from enum import IntFlag, auto
from typing import NamedTuple, Iterable
from dataclasses import dataclass
from functools import partial
from .classes import Pixel, Style, Coordinate, Node, min_size_constant, Result, Rect, Frame, Box
from math import floor

# https://en.wikipedia.org/wiki/Braille_Patterns#Identifying.2C_naming_and_ordering
class Sector(IntFlag):
    TR =  0b0000_0001
    MTR = 0b0000_0010
    MBR = 0b0000_0100
    TL =  0b0000_1000
    MTL = 0b0001_0000
    MBL = 0b0010_0000
    BR =  0b0100_0000
    BL =  0b1000_0000


BRAILLE_EMPTY_CHAR_CODE = 0x2800
def sector_to_braille(sector: Sector) -> str:
    return chr(BRAILLE_EMPTY_CHAR_CODE + sector)

def coord_to_sector_y_down(x: int, y: int) -> Sector:
    if y == 3:
        return Sector(Sector.BR << x)
    else:
        return Sector(Sector.TR << y + 3 * x)

def coord_to_sector_y_up(x: int, y: int) -> Sector:
    y = 3 - y
    if y == 3:
        return Sector(Sector.BR << x)
    else:
        return Sector(Sector.TR << y + 3 * x)

class CanvasItem(NamedTuple):
    sector: Sector
    style: Style


# def get_line_coords(start: Coordinate, end: Coordinate) -> list[Coordinate]:
#     """both ends of the line are included!"""
#     dy = end.y - start.y
#     dx = end.x - start.x
#
#     # if dy < 0 or dx < 0:
#     #     start, end = end, start
#     print("hej")
#
#     if dx != 0 and abs(dy/dx) <= 1: # go along x axis
#         if dx < 0:
#             start, end = end, start
#
#         out = [start]
#
#         m = dy/dx
#         last_y = start.y
#         # for x in range(start.x, end.x, 1 if start.x < end.x else -1):
#         for x in range(abs(dx)):
#             out.append(Coordinate(start.x + x, round(last_y)))
#             last_y = last_y + m
#     else:
#         if dy < 0:
#             start, end = end, start
#         out = [start]
#
#         m = dx/dy
#         last_x = start.x
#         # for y in range(start.y, end.y, 1 if start.y < end.y else -1):
#         for y in range(abs(dy)):
#             out.append(Coordinate(round(last_x), start.y + y))
#             last_x = last_x + m
#     return out

def get_line_coords(start: Coordinate, end: Coordinate) -> list[Coordinate]:
    """both ends of the line are included!"""
    dy = end.y - start.y
    dx = end.x - start.x

    # if dy < 0 or dx < 0:
    #     start, end = end, start
    out = []
    if dx != 0 and abs(dy/dx) <= 1: # go along x axis
        if dx < 0:
            start, end = end, start

        out = [start]

        m = dy/dx
        last_y = start.y
        for x in range(abs(dx) + 1):
            out.append(Coordinate(start.x + x, round(last_y)))
            last_y = last_y + m
    elif dy != 0:
        if dy < 0:
            start, end = end, start
        out = [start]

        m = dx/dy
        last_x = start.x
        for y in range(abs(dy) + 1):
            out.append(Coordinate(round(last_x), start.y + y))
            last_x = last_x + m
    return out


class PlotXY(NamedTuple):
    x: Iterable[float]
    y: Iterable[float]
    style: Style = Style()

class BrailleCanvas:
    def __init__(self, char_width: int, char_height: int) -> None:
        """width and height represent the text chars, not the actuall resolution"""
        self.data =  [[CanvasItem(Sector(0), Style()) for _ in range(char_width)] for _ in range(char_height)]
        self.text_width = char_width
        self.text_height = char_height
        self.width = char_width * 2
        self.height = char_height * 4

    def set(self, pos: Coordinate, style: Style) -> None:
        x_char = pos.x // 2
        y_char = pos.y // 4
        x_remainder = pos.x % 2
        y_remainder = pos.y % 4
        # print("y", y_char, pos.y)
        last = self.data[y_char][x_char]
        self.data[y_char][x_char] = CanvasItem(last.sector | coord_to_sector_y_up(x_remainder, y_remainder), style)

    def draw_line(self, start: Coordinate, end: Coordinate, style: Style):
        for coord in get_line_coords(start, end):
            self.set(coord, style)

    def draw_graph(self, plot: PlotXY, x_scale: float, y_scale: float):
        if len(plot) < 2:
            return
        x_iterator = iter(plot.x)
        y_iterator = iter(plot.y)

        last_x = next(x_iterator)
        last_y = next(y_iterator)


        for x, y in zip(x_iterator, y_iterator):
            new_x = floor(x * x_scale)
            new_y = floor(y * y_scale)
            # print("to:", new_x, new_y)
            from_coordinate = Coordinate(floor(last_x * x_scale), floor(last_y * y_scale))
            to_coordinate = Coordinate(new_x, new_y)
            self.draw_line(
                from_coordinate,
                to_coordinate,
                plot.style
            )
            last_x = x
            last_y = y


def plot(*lines: PlotXY):
    return Node(
        func = plot,
        min_size = min_size_constant(Rect(1, 1)),
        render = partial(_plot_render, lines)
    )

def _plot_render(lines: tuple[PlotXY, ...], frame: Frame, box: Box):
    res = Result()
    canvas = BrailleCanvas(box.width, box.height)
    max_x = max(max(line.x) for line in lines)
    max_y = max(max(line.y) for line in lines)

    x_scale = (box.width * 2 -1) / (max_x)
    y_scale = (box.height * 4 -1) / (max_y)

    for line in lines:
        canvas.draw_graph(line, x_scale, y_scale)

    for y, line in enumerate(reversed(canvas.data)):
        for x, part in enumerate(line):
            res.draw_pixel_with_specific_style(Pixel(
                sector_to_braille(part.sector),
                fg_color=part.style.fg if part.style.fg is not None else frame.default_pixel.fg_color,
                bg_color=part.style.bg if part.style.bg is not None else frame.default_pixel.bg_color,
                style=part.style.char_style | frame.default_pixel.style

            ), box.offset + Coordinate(x, y))
        # res.draw_string_line(
        #     frame,
        #     "".join(sector_to_braille(i.sector) for i in line),
        #     box.offset + Coordinate(0, y)
        # )
    # res.draw_string_line(frame, )
    return res


