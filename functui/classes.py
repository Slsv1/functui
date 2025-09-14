from dataclasses import dataclass, field
from typing import Callable, Self, Iterable, Any
from enum import Enum, Flag, auto
from abc import ABC, abstractmethod
from functools import partial
import wcwidth
#
# utilities
#


@dataclass(frozen=True)
class Applicable[T, U]:
    func: Callable[[T], U]
    def __pow__(self, other: T) -> U:
        return self.func(other)
    def __call__(self, arg: T) -> U:
        return self.func(arg)

def applicable[T, U](func: Callable[[T], U]) -> Applicable[T, U]:
    """ Allows functions that take in a signle argument to be called with the following
    syntax 
    ```
    foo ** bar ** baz
    # same as
    foo(bar(baz))
    ```"""
    return Applicable(func)

#
# General Data Structures
#

@dataclass(frozen=True, eq=True)
class Coordinate:
    x: int
    y: int
    def __add__(self, other):
        return Coordinate(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Coordinate(self.x - other.x, self.y - other.y)

@dataclass(frozen=True, eq=True)
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
        """if box width or hight is bigger than other, then scale down"""
        return self.__class__(
            width = self.width if other.width > self.width else other.width,
            height = self.height if other.height > self.height else other.height,
        )
    def limit_width(self, width: int) -> Self:
        return self.__class__(
            width = self.width if width > self.width else width,
            height = self.height
        )
    def limit_height(self, height: int) -> Self:
        return self.__class__(
            width = self.width,
            height = self.height if height > self.height else height,
        )

@dataclass(frozen=True, eq=True)
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

    def using_rect(self, rect: Rect):
        return self.__class__(
            height=rect.height,
            width=rect.width,
            offset=self.offset
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

class CharStyle(Flag):
    BOLD = auto()
    REVERSED = auto()
    ITALIC = auto()
    UNDERLINED = auto()
    STRIKE_THROUGH = auto()

class Color(Enum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    RESET = 39

@dataclass(frozen=True)
class Style:
    char_style: CharStyle | None = None
    fg: Color | None = None 
    bg: Color | None = None

#
# Ui specific datastructures
#

# @dataclass(frozen=True, eq=True)
# class WideCharTail:
#     overwriting: str
#
class CharType(Enum):
    NORMAL = auto()
    WIDE_HEAD = auto()
    WIDE_TAIL = auto()

@dataclass(frozen=True, eq=True)
class Pixel:
    char: str = " "
    char_type: CharType = CharType.NORMAL
    fg_color: Any = Color.RESET
    bg_color: Any = Color.RESET
    style: CharStyle = CharStyle(0)

    def with_char(self, char: str) -> Self:
        return self.__class__(
            char,
            self.char_type,
            self.fg_color,
            self.bg_color,
            self.style,
        )
    def with_char_type(self, char_type):
        return self.__class__(
            self.char,
            char_type,
            self.fg_color,
            self.bg_color,
            self.style,
        )

    def with_style(self, style: CharStyle) -> Self:
        return self.__class__(
            self.char,
            self.char_type,
            self.fg_color,
            self.bg_color,
            style,
        )

@dataclass(frozen=True, eq=True)
class DrawPixel:
    pixel: Pixel
    at: Coordinate = Coordinate(0, 0)

@dataclass(frozen=True, eq=True)
class DrawBox:
    fill: Pixel
    box: Box

@dataclass(frozen=True, eq=True)
class DrawStringLine:
    string: tuple[Pixel]
    at: Coordinate

type DrawCommand = DrawPixel | DrawBox | DrawStringLine

type MeasureTextFunc = Callable[[str], int]

@dataclass(frozen=True, eq=True)
class Frame:
    """a view on to the canvas"""
    view_box: Box
    screen_rect: Rect
    default_pixel: Pixel
    measure_text: MeasureTextFunc

    def with_pixel(self, pixel: Pixel):
        return self.__class__(
            view_box=self.view_box,
            screen_rect=self.screen_rect,
            default_pixel=pixel,
            measure_text=self.measure_text,
        )

    def shrink_to(self, other_box):
        return Frame(
            view_box=self.view_box.intersect(other_box),
            screen_rect=self.screen_rect,
            default_pixel=self.default_pixel,
            measure_text=self.measure_text,
        )




type MinSize = Callable[[MeasureTextFunc, Rect], Rect]
type ElementConstructor = Applicable[Node, Node]

# minsize util functions

def min_size_expand(
    child_size: MinSize,
    width_change: int,
    height_change: int
) -> MinSize:
    def out(measure_text: MeasureTextFunc, from_size: Rect):
        return child_size(measure_text, from_size.expand(-width_change, -height_change)).expand(width_change, height_change)
    return out

def min_size_vertical(
    children_sizes: list[MinSize],
) -> MinSize:
    def out(measure_text: MeasureTextFunc, from_size: Rect):
        return Rect(
            max(i(measure_text, from_size).width for i in children_sizes),
            sum(i(measure_text, from_size).height for i in children_sizes),
        ) if children_sizes else Rect(0, 0)
    return out

def min_size_horizontal(
    children_sizes: list[MinSize],
) -> MinSize:
    def out(measure_text: MeasureTextFunc, from_size: Rect):
        return Rect(
            sum(i(measure_text, from_size).width for i in children_sizes),
            max(i(measure_text, from_size).height for i in children_sizes),
        ) if children_sizes else Rect(0, 0)
    return out
def min_size_union(
    children_sizes: list[MinSize],
) -> MinSize:
    def out(measure_text: MeasureTextFunc, from_size: Rect):
        return Rect(
            max(i(measure_text, from_size).width for i in children_sizes),
            max(i(measure_text, from_size).height for i in children_sizes),
        ) if children_sizes else Rect(0, 0)
    return out
def min_size_constant(return_value: Rect) -> MinSize:
    return lambda measure_text, available: return_value

class ResultData(ABC):
    @classmethod
    @abstractmethod
    def create_dummy(cls) -> Self:
        ...

    @abstractmethod
    def merge_children(self, child_data: Self) -> Self:
        ...


@dataclass(unsafe_hash=True)
class Result:
    _draw_commands: list[DrawCommand] = field(default_factory=list)
    _data: dict[type[ResultData], ResultData] = field(default_factory=dict)

    def add_children_after(self, child_results: list[Self]):
        for child in child_results:
            self._draw_commands.extend(child._draw_commands)
            # if some node does not provide data of a type but child does, then create a dummy
            for k, child_data in child._data.items():
                if k in self._data:
                    self._data[k] = self._data[k].merge_children(child_data)
                else:
                    self._data[k] = k.create_dummy().merge_children(child_data)

    def try_data[T: (ResultData)](self, key: type[T]) -> T | None:
        if key in self._data:
            return self._data[key]
        return None

    def set_data(self, data: ResultData):
        self._data[data.__class__] = data


    def draw_pixel(self, frame: Frame, fill: str, at: Coordinate):
        if not frame.view_box.is_point_inside(at):
            return 
        self._draw_commands.append(
            DrawPixel(frame.default_pixel.with_char(fill), at)
        )
    def draw_box(
        self,
        frame: Frame,
        fill: str,
        box: Box,
    ):
        self._draw_commands.append(DrawBox(
            frame.default_pixel.with_char(fill),
            frame.view_box.intersect(box)
        ))
    def draw_string_line(
        self,
        frame: Frame,
        content: str,
        at: Coordinate = Coordinate(0, 0)
    ):
        bounds = frame.view_box
        #       content
        #         #---#
        #         |   |
        #         #---#
        #       content
        if at.y < bounds.offset.y or at.y >= bounds.offset.y + bounds.height:
            return

        content_len = frame.measure_text(content)
        outer_x_bound = bounds.offset.x + bounds.width
        #         #---#
        # content |   | content
        #         #---#
        if at.x +content_len < bounds.offset.x or at.x >= outer_x_bound:
            return

        # find initial x offset
        #         #---#
        #    content  |
        #    ^^^^^#---#
        required_offset = bounds.offset.x - at.x
        x_content_offset = 0
        char_offset = 0
        if required_offset > 0:
            for char in content:
                x_content_offset += frame.measure_text(char)
                char_offset += 0
                if x_content_offset >= required_offset:
                    break

        # generate output string
        out = []
        for char in content[char_offset:]:
            char_width = frame.measure_text(char)
            x_content_offset += char_width
            if x_content_offset + at.x > outer_x_bound:
                break
            if char_width == 1:
                out.append(frame.default_pixel.with_char(char))
            else:
                out.append(frame.default_pixel.with_char(char).with_char_type(CharType.WIDE_HEAD))
                out.append(frame.default_pixel.with_char("").with_char_type(CharType.WIDE_TAIL))
        self._draw_commands.append(DrawStringLine(
            tuple(out), at
        ))
    def get_commands(self): return tuple(self._draw_commands)


# I have concidered individual classes for this
# like for example a border being its own class that inherits form node
# instead of a function border that returns a node
#
# That may make things a little bit cleaner in a sence
# (for example we can have methods like: setup, set_size, render
# that would split up the responsibility of the current render function)
# And this approach would maybe more understandable for those who know oop.
# (which is most of the python community)
# However, this approcah would introduce invalid states to the program in the case
# of those methods being called out of order.
# And the biggest negative would be that that approach would be harder to optimise
# through the use of caching. Now that methods dont return anything
# we cant really cache them because you cant cache side effects
# And even if those methods return new version of the object
# it beign split between multiple methods would 


@dataclass(eq=True, frozen=True)
class Node:
    func: Callable
    min_size: MinSize
    render: partial[Result]
    """chould take in frame and box as first two args"""
    # def __hash__(self) -> int:
    #     return hash((self.func, self.render.args)) 
    # def __eq__(self, value: object, /) -> bool:
    #     return self.__hash__ == (value.func, value.hash) # type: ignore

@dataclass(frozen=True, eq=True)
class ResultCreatedWith(ResultData):
    """this is added to a result by the get_result function so that this data can later be used by any rendering function"""
    measure_text_func: MeasureTextFunc
    screen_size: Rect
    def merge_children(self, child_data):
        raise RuntimeError("Result should not be merged with with this data")
    @classmethod
    def create_dummy(cls):
        raise RuntimeError("Result should not be merged with with this data")

def layout_to_result(dimensions: Rect, layout: Node, measure_text: MeasureTextFunc = lambda t: wcwidth.wcswidth(t)) -> Result:
    result = layout.render(
        Frame(
            screen_rect=dimensions,
            view_box=Box(dimensions.width, dimensions.height),
            default_pixel=Pixel(),
            measure_text=measure_text
        ),
        Box(width=dimensions.width, height=dimensions.height),
    )
    result.set_data(ResultCreatedWith(measure_text, screen_size=dimensions))
    return result
