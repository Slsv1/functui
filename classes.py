from dataclasses import dataclass
from typing import Self, Callable

__all__ = [
    "Coordinate",
    "Screen",
    "Box",
    "Frame",
    "Node",
]

@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int
    def __add__(self, other):
        return Coordinate(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Coordinate(self.x - other.x, self.y - other.y)
    
class Screen:
    def __init__(self, width: int, height: int, fill: str):
        self.width = width
        self.height = height
        self._data: list[str] = [fill for _ in range(width * height)]
        """
        matrix indicies work in this pattern:
        0 1 2 3 4
        5 6 7 8 9
        """

    def get(self, pos: Coordinate) -> str:
        return self._data[pos.x + pos.y * self.width]

    def set(self, pos: Coordinate, data: str) -> None:
        self._data[pos.x + pos.y * self.width] = data

    def split_by_lines(self) -> tuple[str, ...]:
            out: list[str] = []
            for h in range(self.height):
                current_row = [self.get(Coordinate(w, h)) for w in range(self.width)]
                out.append("".join(current_row))
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

    def draw_pixel(self, fill: str, at: Coordinate) -> None:
        if not self.view_box.is_point_inside(at):
            return
        self.screen.set(at, fill)

    def draw_box(self, fill: str, width: int, height: int, start: Coordinate = Coordinate(0, 0)) -> None:
        for x in range(start.x, start.x + width):
            for y in range(start.y, start.y + height):
                self.draw_pixel(fill, Coordinate(x, y))

    def draw_string(self, content: str, at: Coordinate = Coordinate(0, 0)) -> None:
        for y, line in enumerate(content.split('\n')):
            for x, char in enumerate(line):
                self.draw_pixel(char, Coordinate(x+at.x, y+at.y))

    def shrink_to(self, other_box):
        return Frame(
            view_box=self.view_box.intersect(other_box),
            screen=self.screen
        )

@dataclass(frozen=True)
class Node:
    min_size: Box
    render: Callable[[Frame, Box], None]
    # Frame is the view to the screen
    # Box is the dimensions for the node
