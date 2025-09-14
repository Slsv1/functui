# type Points = tuple[int, int, int, int, int, int, int, int]
from enum import IntFlag, auto
from typing import NamedTuple
from dataclasses import dataclass
from .classes import Style, Coordinate

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

def coord_to_sector(x: int, y: int) -> Sector:
    if y == 3:
        return Sector(Sector.BR << x)
    else:
        return Sector(Sector.TR << y + 3 * x)


# okay so here i have two options
# either 1:
# store the canvas as just as a big ass integer with each bit representing
# if that segment is fild in or not
# or 2:
# store the canvas as an array of sectors

# option 1 pros:
# easy to draw lines

# option 2 pros:
# easy to convert to text
# easy when it comes to color

class CanvasItem(NamedTuple):
    sector: Sector
    style: Style

def get_line_coords(start: Coordinate, end: Coordinate) -> list[Coordinate]:
    dy = end.y - start.y
    dx = end.x - start.x
    m = dy/dx
    out = [start]
    if m <= 1:
        last_y = start.y
        for x in range(dx):
            out.append(Coordinate(start.x + x, round(last_y)))
            last_y = last_y + m
    else:
        m = dx/dy
        last_x = start.x
        for y in range(dy):
            out.append(Coordinate(round(last_x), start.y + y))
            last_x = last_x + m
    return out



class BrailleCanvas:
    def __init__(self, width: int, height: int) -> None:
        """width and height represent the text chars, not the actuall resolution"""
        self._data =  [[CanvasItem(Sector(0), Style()) for _ in range(width)] for _ in range(height)]
        self.text_width = width
        self.text_height = height
        self.width = width * 2
        self.height = height * 4
    def set(self, pos: Coordinate) -> None:
        x_char = pos.x // 2
        y_char = pos.y // 4
        x_remainder = pos.x % 2
        y_remainder = pos.y % 4
        last = self._data[y_char][x_char]
        self._data[y_char][x_char] = CanvasItem(last.sector | coord_to_sector(x_remainder, y_remainder), last.style)
    def draw_line(self, start: Coordinate, end: Coordinate, style: Style | None = None):
        for coord in  get_line_coords(start, end):
            self.set(coord)
