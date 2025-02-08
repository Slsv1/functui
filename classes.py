from dataclasses import dataclass
from typing import Any, Self, Callable
from enum import IntFlag, auto

__all__ = [
    "Coordinate",
    "Screen",
    "Box",
    "Frame",
    "Node",
    "applicable"
]


@dataclass(frozen=True)
class Applicable[T, U]:
    func: Callable[[T], U]
    def __pow__(self, other: T) -> U:
        return self.func(other)
    def __call__(self, arg: T) -> U:
        return self.func(arg)


def applicable[T, U](func: Callable[[T], U]) -> Applicable[T, U]:
    return Applicable(func)

@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int
    def __add__(self, other):
        return Coordinate(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Coordinate(self.x - other.x, self.y - other.y)

class CharStyle(IntFlag):
    BOLD = auto()
    REVERSED = auto()
    ITALIC = auto()
    UNDERLINED = auto()

@dataclass(frozen=True)
class Pixel:
    char: str = " "
    fg_color: Any = None
    bg_color: Any = None
    style: CharStyle = CharStyle(0)
    def with_char(self, char: str) -> Self:
        return self.__class__(
            char,
            self.fg_color,
            self.bg_color,
            self.style
        )
    def add_styles(self, style: CharStyle) -> Self:
        return self.__class__(
            self.char,
            self.fg_color,
            self.bg_color,
            self.style | style
        )
    
class Screen:
    def __init__(self, width: int, height: int, fill: Pixel=Pixel(" ", None, None)):
        self.width = width
        self.height = height
        self._data: list[Pixel] = [fill for _ in range(width * height)]
        """
        matrix indicies work in this pattern:
        0 1 2 3 4
        5 6 7 8 9
        """

    def get(self, pos: Coordinate) -> Pixel:
        return self._data[pos.x + pos.y * self.width]

    def set(self, pos: Coordinate, data: Pixel) -> None:
        self._data[pos.x + pos.y * self.width] = data
    
    def split_by_lines(self) -> tuple[tuple[Pixel, ...], ...]:
        out: list[tuple[Pixel, ...]] = []
        for h in range(self.height):
            current_row = tuple([self.get(Coordinate(w, h)) for w in range(self.width)])
            out.append(current_row)
        return tuple(out)

@dataclass(frozen=True)
class Box:
    width: int
    height: int
    offset: Coordinate = Coordinate(0, 0)
    def shrink(
        self,
        top: int = 0,
        bottom: int = 0,
        left: int = 0,
        right: int = 0,
    ) -> Self:
        return self.__class__(
            width=self.width - left - right,
            height=self.height - top - bottom,
            offset=self.offset + Coordinate(left, top)
        )

    def expand(
        self,
        top: int = 0,
        bottom: int = 0,
        left: int = 0,
        right: int = 0,
    ) -> Self:
        return self.__class__(
            width=self.width + left + right,
            height=self.height + top + bottom,
            offset=self.offset - Coordinate(left, top)
        )

    def intersect(self, other: Self) -> Self:
        x1 = max(self.offset.x, other.offset.x)
        x2 = min(self.offset.x+self.width, other.offset.x+other.width)
        y1 = max(self.offset.y, other.offset.y)
        y2 = min(self.offset.y+self.height, other.offset.y+other.height)
        return self.__class__(
            height=y2-y1,
            width=x2-x1,
            offset=Coordinate(x1, y1),
        )

    def is_empty(self) -> bool:
        return self.width <= 0 or self.height <= 0

    def offset_by(self, coordinate: Coordinate):
        return Box(
            width=self.width,
            height=self.height,
            offset=self.offset + coordinate
        )

    def union(self, other: Self) -> Self:
        x1 = min(self.offset.x, other.offset.x)
        x2 = max(self.offset.x+self.width, other.offset.x+other.width)
        y1 = min(self.offset.y, other.offset.y)
        y2 = max(self.offset.y+self.height, other.offset.y+other.height)
        return self.__class__(
            height=y2-y1,
            width=x2-x1,
            offset=Coordinate(x1, y1),
        )

    def is_point_inside(self, point: Coordinate):
        return self.offset.x <= point.x < (self.offset.x + self.width)\
            and self.offset.y <= point.y < (self.offset.y + self.height) 

#
# Instructions
#

type DrawInstruction = DrawPixel | DrawBox | DrawString

@dataclass(frozen=True)
class DrawPixel:
    pixel: Pixel
    at: Coordinate = Coordinate(0, 0)

@dataclass(frozen=True)
class DrawBox:
    fill: Pixel
    width: int
    height: int
    at: Coordinate = Coordinate(0, 0)

@dataclass(frozen=True)
class DrawString:
    content: str
    at: Coordinate = Coordinate(0, 0)

def apply_draw_instructions(screen: Screen, instructions: list[DrawInstruction]):
    for instruction in instructions:
        if isinstance(instruction, DrawPixel):
            screen.set(instruction.at, instruction.pixel)
        elif isinstance(instruction, DrawBox):
            for x in range(instruction.at.x, instruction.at.x + instruction.width):
                for y in range(instruction.at.y, instruction.at.y + instruction.height):
                    screen.set(Coordinate(x, y), instruction.fill)
        else:
            for y, line in enumerate(instruction.content.split('\n')):
                for x, char in enumerate(line):
                    at = Coordinate(x+instruction.at.x, y+instruction.at.y)
                    screen.set(at, screen.get(at).with_char(char))



@dataclass(frozen=True)
class View:
    """a sub part of the screen"""
    box: Box
    screen: Screen
    default_pixel: Pixel

    def with_pixel(self, pixel: Pixel):
        return self.__class__(
            box=self.box,
            screen=self.screen,
            default_pixel=pixel
        )

    def draw_pixel(self, fill: str, at: Coordinate) -> DrawPixel:
        if self.box.is_point_inside(at):
            return DrawPixel(self.default_pixel.with_char(fill), at)
            # TODO:
            # this can returen none and if we are adding to list it will get annoying
            # maybe the command list may be stored in view (which is hella wierd, but think about caching also)

    def draw_box(self, fill: str, width: int, height: int, start: Coordinate = Coordinate(0, 0)) -> None:
        for x in range(start.x, start.x + width):
            for y in range(start.y, start.y + height):
                self.draw_pixel(fill, Coordinate(x, y))

    def draw_string(self, content: str, at: Coordinate = Coordinate(0, 0)) -> None:
        for y, line in enumerate(content.split('\n')):
            for x, char in enumerate(line):
                self.draw_pixel(char, Coordinate(x+at.x, y+at.y))

    def shrink_to(self, other_box):
        return View(
            box=self.box.intersect(other_box),
            screen=self.screen,
            default_pixel=self.default_pixel
        )




@dataclass
class Result:
    size: Box
    instructions: list

@dataclass
class Node:
    fixed_width: Callable[[int, bool], Result]
    fixed_height: Callable[[int, bool], Result]

def border(child: Node):
    # return Partial(_border, child)

# cached
def _border_process(child, view, max_box, shrink):
    result = child(view, max_box.shrink(1, 1, 1, 1), shrink)
    box = result.box.expand(1, 1, 1, 1) if shrink else max_box
    return Result(box, view.add_after([
        ...,
        ...,
        ...,
    ]))










# def border(child: Node):
#     instructions = lambda size: [DrawBox(size.origin, ..., ..., ...)]
#     expand = lambda box: box.expand(1, 1, 1, 1)

#     return Node(
#         fixed_width=lambda width, shrink: child.fixed_width(width-2, shrink).add_instructions_after(instructions).expand_by(expand)
#         fixed_height=lambda width, shrink: child.fixed_height(height-2, shrink).add_instructions_after(instructions).expand_by(expand)
#     )
