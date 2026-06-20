# type Points = tuple[int, int, int, int, int, int, int, int]
from enum import IntFlag, auto
from typing import NamedTuple, Iterable
from dataclasses import dataclass
from functools import partial
from .classes import StyleRule, Coordinate, Layout, min_size_constant, Rect, Frame, Box
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


_BITS = (
    (Sector.BR, Sector.MBR, Sector.MTR, Sector.TR),
    (Sector.BL, Sector.MBL, Sector.MTL, Sector.TL),
)

def coord_to_sector_y_up(x: int, y: int) -> Sector:
    return _BITS[x][y]

class CanvasItem(NamedTuple):
    sector: Sector
    style: StyleRule

def get_line_coords(start: Coordinate, end: Coordinate) -> list[Coordinate]:
    """both ends of the line are included!"""
    dy = end.y - start.y
    dx = end.x - start.x

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
    style: StyleRule = StyleRule()

class BrailleCanvas:
    def __init__(self, char_width: int, char_height: int) -> None:
        self.bytes = bytearray(char_width * char_height)
        """row major"""
        self.text_width = char_width
        self.text_height = char_height
        self.width = char_width * 2
        self.height = char_height * 4

    def clear(self):
        self.bytes.clear()

    def set(self, pos: Coordinate) -> None:
        x, y = pos
        x_char = x // 2
        y_char = y // 4
        x_remainder = x % 2
        y_remainder = y % 4
        self.bytes[
            x_char + y_char * self.text_width
        ] |= coord_to_sector_y_up(x_remainder, y_remainder)

    def draw_line(self, start: Coordinate, end: Coordinate, style: StyleRule):
        for coord in get_line_coords(start, end):
            self.set(coord)

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

            from_coordinate = Coordinate(floor(last_x * x_scale), floor(last_y * y_scale))
            to_coordinate = Coordinate(new_x, new_y)
            self.draw_line(
                from_coordinate,
                to_coordinate,
                plot.style
            )
            last_x = x
            last_y = y

    def get_strings(self):
        for i in range(self.text_height):
            y =  self.text_height - i - 1
            slice = self.bytes[y * self.text_width: (y+1) * self.text_width]
            yield "".join(chr(BRAILLE_EMPTY_CHAR_CODE + b) for b in slice)

def braille_canvas(canvas: BrailleCanvas):
    strings_gen = canvas.get_strings()
    return Layout(
        func = braille_canvas,
        min_size = min_size_constant(Rect(canvas.text_width, canvas.text_height)),
        render = partial(_plot_render, strings_gen)
    )

def _plot_render(strings: Iterable[str], frame: Frame, box: Box):
    for i, string in enumerate(strings):
        frame.draw_string_line(string, box.position.down(i))

# canvas = BrailleCanvas(box.width, box.height)
# max_x = max(max(line.x) for line in lines)
# max_y = max(max(line.y) for line in lines)
#
# x_scale = (box.width * 2 -1) / (max_x)
# y_scale = (box.height * 4 -1) / (max_y)
#
# for line in lines:
#     canvas.draw_graph(line, x_scale, y_scale)



