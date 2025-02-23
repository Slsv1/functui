from dataclasses import dataclass
from typing import Any, Self, Callable
from enum import IntFlag, auto

__all__ = [
    "Coordinate",
    "Screen",
    "Box",
    "Frame",
    "Node",
    "Rect",
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
    STRIKE_THROUGH = auto()

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
    @property
    def rect(self) -> Rect:
        return Rect(self.width, self.height)
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


@dataclass(frozen=True)
class Frame:
    """a sub part of the screen"""
    view_box: Box
    screen: Screen
    default_pixel: Pixel

    def with_pixel(self, pixel: Pixel):
        return self.__class__(
            view_box=self.view_box,
            screen=self.screen,
            default_pixel=pixel
        )

    def draw_pixel(self, fill: str, at: Coordinate) -> None:
        if not self.view_box.is_point_inside(at):
            return
        self.screen.set(at, self.default_pixel.with_char(fill))

    def draw_box(self, fill: str, width: int, height: int, start: Coordinate = Coordinate(0, 0)) -> None:
        for x in range(start.x, start.x + width):
            for y in range(start.y, start.y + height):
                self.draw_pixel(fill, Coordinate(x, y))

    def draw_string(self, content: str, at: Coordinate = Coordinate(0, 0)) -> None:
        for y, line in enumerate(content.split('\n')):
            for x, char in enumerate(line):
                self.draw_pixel(char, Coordinate(x+at.x, y+at.y))
    
    # def get_and_set_pixel(self, func: Callable[[Pixel], Pixel], at: Coordinate) -> None:
    #     """i use get and set because then this all can be converted into commands in the future.
    #     If i have get functions then it cant be really implemented as commands because immidiate feedback would be needed"""
    #     return self.screen.set(at, func(self.screen.get(at)))
    
    # def get_and_set_box(self, func: Callable[[Pixel], Pixel], width: int, height: int, start: Coordinate = Coordinate(0, 0)) -> None:
    #     for x in range(start.x, start.x + width):
    #         for y in range(start.y, start.y + height):
    #             self.get_and_set_pixel(func, Coordinate(x, y))

    def shrink_to(self, other_box):
        return Frame(
            view_box=self.view_box.intersect(other_box),
            screen=self.screen,
            default_pixel=self.default_pixel
        )

type MinSize = Callable[[Rect], Rect]

@dataclass(frozen=True)
class Node:
    min_size: MinSize
    render: Callable[[Frame, Box], None]
    # Frame is the view to the screen
    # Box is the dimensions for the node

# minsize util functions

def min_size_expand(
    child_size: MinSize,
    width_change: int,
    height_change: int
) -> MinSize:
    def out(from_size: Rect):
        return child_size(from_size.expand(-width_change, -height_change)).expand(width_change, height_change)
    return out

def min_size_vertical(
    children_sizes: list[MinSize],
) -> MinSize:
    def out(from_size):
        return Rect(
            max(i(from_size).width for i in children_sizes),
            sum(i(from_size).height for i in children_sizes),
        ) if children_sizes else Rect(0, 0)
    return out

def min_size_horizontal(
    children_sizes: list[MinSize],
) -> MinSize:
    def out(from_size):
        return Rect(
            sum(i(from_size).width for i in children_sizes),
            max(i(from_size).height for i in children_sizes),
        ) if children_sizes else Rect(0, 0)
    return out
