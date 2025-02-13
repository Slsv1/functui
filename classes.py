from dataclasses import dataclass, field
from typing import Any, Self, Callable, Protocol
from enum import IntFlag, auto

__all__ = [
    "Coordinate",
    "Screen",
    "Box",
    "View",
    "Node",
    "Rect",
    "DrawInstruction",
    "applicable",
    "ClassDict",
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

class ClassDict:
    def __init__(self) -> None:
        self._data = {}
    def set(self, item):
        self._data[item.__class__] = item
    def try_get[T](self, item_type: type[T]) -> T | None:
        return self._data.get(item_type, None)

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
class Rect:
    width: int
    height: int
    def expand(self, width: int=0, height: int=0) -> Self:
        return self.__class__(
            width = self.width + width,
            height = self.height + height,
        )
    def union(self, other: Self) -> Self:
        return self.__class__(
            width = self.width if other.width < self.width else other.width,
            height = self.height if other.height < self.height else other.height,
        )
    def limit(self, other: Self) -> Self:
        return self.__class__(
            width = self.width if other.width > self.width else other.width,
            height = self.height if other.height > self.height else other.height,
        )

@dataclass(frozen=True)
class Box:
    width: int
    height: int
    offset: Coordinate = Coordinate(0, 0)
    @property
    def rect(self) -> Rect:
        return Rect(self.width, self.height)
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

    def offset_by(self, coordinate: Coordinate) -> Self:
        return self.__class__(
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


@dataclass
class InstructionConstructor():
    box: Box
    default_pixel: Pixel
    instruction_list: list[DrawInstruction] = field(default_factory=list)

    def draw_pixel(self, fill: str, at: Coordinate):
        if self.box.is_point_inside(at):
            self.instruction_list.append(DrawPixel(self.default_pixel.with_char(fill), at))
            # TODO:
            # this can returen none and if we are adding to list it will get annoying
            # maybe the command list may be stored in view (which is hella wierd, but think about caching also)
        return self

    def draw_box(self, fill: str, width: int, height: int, start: Coordinate = Coordinate(0, 0)):
        for x in range(start.x, start.x + width):
            for y in range(start.y, start.y + height):
                self.draw_pixel(fill, Coordinate(x, y))
        return self

    def draw_string(self, content: str, at: Coordinate = Coordinate(0, 0)):
        for y, line in enumerate(content.split('\n')):
            for x, char in enumerate(line):
                self.draw_pixel(char, Coordinate(x+at.x, y+at.y))
        return self
    def finish_drawing(self):
        return self.instruction_list


@dataclass(frozen=True)
class View:
    """a sub part of the screen"""
    box: Box
    default_pixel: Pixel

    def with_pixel(self, pixel: Pixel):
        return self.__class__(
            box=self.box,
            default_pixel=pixel
        )
    def start_drawing(self):
        return InstructionConstructor(
            self.box,
            self.default_pixel
        )
    def shrink_to(self, other_box):
        return View(
            box=self.box.intersect(other_box),
            default_pixel=self.default_pixel
        )

@dataclass
class Result:
    size: Rect
    instructions: list

# type Node = Callable[[View, Box, bool], Result]


class Node(Protocol):
    def __call__(self, view: View, box: Box, shrink: bool, class_dict: ClassDict) -> Result:
        ...











# def border(child: Node):
#     instructions = lambda size: [DrawBox(size.origin, ..., ..., ...)]
#     expand = lambda box: box.expand(1, 1, 1, 1)

#     return Node(
#         fixed_width=lambda width, shrink: child.fixed_width(width-2, shrink).add_instructions_after(instructions).expand_by(expand)
#         fixed_height=lambda width, shrink: child.fixed_height(height-2, shrink).add_instructions_after(instructions).expand_by(expand)
#     )
