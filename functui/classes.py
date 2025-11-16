from dataclasses import dataclass, field
from typing import Callable, Self, Iterable, Any
from enum import Enum, Flag, auto
from abc import ABC, abstractmethod
from functools import partial
import wcwidth
#
# utilities
#
def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def even_divide(num, denomenator) -> list[int]:
    return [num // denomenator + (1 if x < num % denomenator else 0)  for x in range (denomenator)]

@dataclass(frozen=True)
class Applicable[T, U]:
    func: Callable[[T], U]
    def __or__(self, other: T) -> U:
        return self.func(other)
    def __call__(self, arg: T) -> U:
        return self.func(arg)

def applicable[T, U](func: Callable[[T], U]) -> Applicable[T, U]:
    return func
    # return Applicable(func)

#
# General Data Structures
#

@dataclass(frozen=True, eq=True)
class Coordinate:
    """An immutable coordinate in 2d space

    Attributes: 
        x:
        y:
    """
    x: int
    y: int
    def __add__(self, other):
        return Coordinate(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Coordinate(self.x - other.x, self.y - other.y)

@dataclass(frozen=True, eq=True)
class Rect:
    """A simple immutable rectangle defined by width and height.

    Attributes:
        width:
        height:
    """

    width: int
    height: int

    def resize(self, width: int = 0, height: int = 0) -> Self:
        """Returns a new Rect resized by expanding or shrinking.

        Positive values expand; negative values shrink.

        Args:
            width: Amount to expand (or shrink) on the x axis.
            height: Amount to expand (or shrink) on the y axis.

        Returns: A new rectangle with altered size.
        """
        return self.__class__(
            width=self.width + width,
            height=self.height + height,
        )

    def union(self, other: Self) -> Self:
        """Returns a rectangle representing the maximum dimensions of this and another.

        Effectively selects the largest width and height between the two rectangles.

        Args:
            other: The rectangle to compare against.

        Returns:
            Rect: A new rectangle whose dimensions are the max of the two.
        """
        return self.__class__(
            width=self.width if other.width < self.width else other.width,
            height=self.height if other.height < self.height else other.height,
        )

    def clamp(self, other: Self) -> Self:
        """Returns a rectangle clamped so its dimensions do not exceed another rectangle.

        Effectively selects the minimum width and height between the two rectangles.

        Args:
            other: The rectangle whose dimensions act as an upper bound.

        Returns:
            Rect: A new rectangle whose dimensions are the min of the two.
        """
        return self.__class__(
            width=self.width if other.width > self.width else other.width,
            height=self.height if other.height > self.height else other.height,
        )

    def clamp_width(self, width: int) -> Self:
        """Returns a rectangle with its width limited to a maximum value.

        Args:
            width: The maximum allowed width.

        Returns:
            Rect: A new rectangle with width clamped to at most the given value.
        """
        return self.__class__(
            width=self.width if width > self.width else width,
            height=self.height,
        )

    def clamp_height(self, height: int) -> Self:
        """Returns a rectangle with its height limited to a maximum value.

        Args:
            height: The maximum allowed height.

        Returns:
            Rect: A new rectangle with height clamped to at most the given value.
        """
        return self.__class__(
            width=self.width,
            height=self.height if height > self.height else height,
        )
@dataclass(frozen=True, eq=True)
class Box:
    """An immutable rectangle defined by width, height and position.

    Attributes:
        width: The rectangle's width.
        height: The rectangle's height.
        position: The rectangle's position.
    """
    width: int
    height: int
    position: Coordinate = Coordinate(0, 0)
    def resize(
        self,
        top: int = 0,
        bottom: int = 0,
        left: int = 0,
        right: int = 0,
    ) -> Self:
        """Returns a new box resized by expanding or shrinking each side.

        Positive values expand outward; negative values shrink inward.

        Args:
            top: Amount to expand (or shrink) upward. Defaults to 0.
            bottom: Amount to expand downward. Defaults to 0.
            left: Amount to expand leftward. Defaults to 0.
            right: Amount to expand rightward. Defaults to 0.

        Returns:
            A new box with adjusted width, height, and shifted position.
        """
        return self.__class__(
            width=self.width + left + right,
            height=self.height + top + bottom,
            position=self.position - Coordinate(left, top)
        )
    @property
    def rect(self) -> Rect:
        """Returns a Rect representing only this box's size.

        Returns:
            A rectangle with the same width and height as the box.
        """
        return Rect(self.width, self.height)

    def using_rect(self, rect: Rect):
        """Returns a copy of this box but with dimensions replaced by a Rect.

        Args:
            rect: The rectangle whose width and height should be applied.

        Returns:
            A new box with updated width and height, unchanged position.
        """
        return self.__class__(
            height=rect.height,
            width=rect.width,
            position=self.position
        )

    def intersect(self, other: Self) -> Self:
        """Returns the intersection region between this box and another.

        If the boxes do not overlap, the resulting width or height may be zero
        or negative, depending on the input.

        Args:
            other: The box to intersect with.

        Returns:
            A new box representing the overlap region.
        """
        x1 = max(self.position.x, other.position.x)
        x2 = min(self.position.x+self.width, other.position.x+other.width)
        y1 = max(self.position.y, other.position.y)
        y2 = min(self.position.y+self.height, other.position.y+other.height)
        return self.__class__(
            height=y2-y1,
            width=x2-x1,
            position=Coordinate(x1, y1),
        )

    def offset_by(self, coordinate: Coordinate) -> Self:
        """Returns a new box moved by the given coordinate offset.

        Args:
            coordinate: The (dx, dy) offset to apply.

        Returns:
            A new box shifted by the provided coordinate.
        """
        return self.__class__(
            width=self.width,
            height=self.height,
            position=self.position + coordinate
        )

    def union(self, other: Self) -> Self:
        """Returns the smallest box that fully contains both this box and another.

        Args:
            other: The box to union with.

        Returns:
            A new box representing the bounding rectangle of both boxes.
        """
        x1 = min(self.position.x, other.position.x)
        x2 = max(self.position.x+self.width, other.position.x+other.width)
        y1 = min(self.position.y, other.position.y)
        y2 = max(self.position.y+self.height, other.position.y+other.height)
        return self.__class__(
            height=y2-y1,
            width=x2-x1,
            position=Coordinate(x1, y1),
        )

    def is_point_inside(self, point: Coordinate):
        """Determines whether a point lies within the box's boundaries.

        The check uses half-open bounds: inclusive of the top/left edges,
        exclusive of the bottom/right edges.

        Args:
            point: The point to test.

        Returns:
            True if the point lies inside the box, else False.
        """
        return self.position.x <= point.x < (self.position.x + self.width)\
            and self.position.y <= point.y < (self.position.y + self.height) 

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
    fg: Color | None = None 
    bg: Color | None = None
    char_style: CharStyle = CharStyle(0)
    def __iter__(self):
        return iter((self.fg, self.bg, self.char_style))
    def combine(self, other: Self):
        return Style(
            char_style=self.char_style | other.char_style,
            fg=self.fg if other.fg is None else other.fg,
            bg=self.bg if other.bg is None else other.bg,
        )


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
    style: Style = Style()

    def with_char(self, char: str) -> Self:
        return self.__class__(
            char,
            self.char_type,
            self.style,
        )
    def with_char_type(self, char_type):
        return self.__class__(
            self.char,
            char_type,
            self.style,
        )

    def with_style(self, style: Style) -> Self:
        return self.__class__(
            self.char,
            self.char_type,
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
    view_box: Box
    screen_rect: Rect
    default_style: Style
    measure_text: MeasureTextFunc

    def with_style(self, style: Style):
        return self.__class__(
            view_box=self.view_box,
            screen_rect=self.screen_rect,
            default_style=style,
            measure_text=self.measure_text,
        )

    def shrink_to(self, other_box):
        return Frame(
            view_box=self.view_box.intersect(other_box),
            screen_rect=self.screen_rect,
            default_style=self.default_style,
            measure_text=self.measure_text,
        )

type MinSize = Callable[[MeasureTextFunc, Rect], Rect]
"""A Function that returns a [functui.clases.Layout][]s minimum size."""
type ElementConstructor = Applicable[Layout, Layout]

# minsize util functions

def min_size_expand(
    child_size: MinSize,
    width_change: int,
    height_change: int
) -> MinSize:
    def out(measure_text: MeasureTextFunc, from_size: Rect):
        return child_size(measure_text, from_size.resize(-width_change, -height_change)).resize(width_change, height_change)
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
            DrawPixel(Pixel(char=fill, style=frame.default_style), at)
        )
    def draw_custom_pixel(self, pixel: Pixel, at: Coordinate):
        self._draw_commands.append(
            DrawPixel(pixel, at)
        )
    def draw_box(
        self,
        frame: Frame,
        fill: str,
        box: Box,
    ):
        self._draw_commands.append(DrawBox(
            Pixel(char=fill, style=frame.default_style),
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
        if at.y < bounds.position.y or at.y >= bounds.position.y + bounds.height:
            return

        content_len = frame.measure_text(content)
        outer_x_bound = bounds.position.x + bounds.width
        #         #---#
        # content |   | content
        #         #---#
        if at.x +content_len < bounds.position.x or at.x >= outer_x_bound:
            return

        # find initial x offset
        #         #---#
        #    content  |
        #    ^^^^^#---#
        required_offset = bounds.position.x - at.x
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
                out.append(Pixel(char=char, style=frame.default_style))
            else:
                out.append(Pixel(
                    char=char,
                    char_type=CharType.WIDE_HEAD,
                    style=frame.default_style
                ))
                out.append(Pixel(
                    char="",
                    char_type=CharType.WIDE_TAIL,
                    style=frame.default_style
                ))
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
class Layout:
    """An immutable layout that can be rendered as a string

    Attributes:
        func: The function that returned this layout. Used to give this layout a name.
        min_size: Function that returns

    """
    func: Callable
    min_size: MinSize
    render: partial[Result]

    def __or__(self, other):
        return other(self)
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

def layout_to_result(dimensions: Rect, layout: Layout, measure_text: MeasureTextFunc = lambda t: wcwidth.wcswidth(t)) -> Result:
    result = layout.render(
        Frame(
            screen_rect=dimensions,
            view_box=Box(dimensions.width, dimensions.height),
            default_style=Style(fg=Color.RESET, bg=Color.RESET),
            measure_text=measure_text
        ),
        Box(width=dimensions.width, height=dimensions.height),
    )
    result.set_data(ResultCreatedWith(measure_text, screen_size=dimensions))
    return result
