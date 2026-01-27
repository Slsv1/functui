from dataclasses import dataclass, field
from typing import Callable, Self, Iterable, Any, Protocol, TypeAlias, NamedTuple
from enum import Enum, Flag, auto, IntEnum
from abc import ABC, abstractmethod
from functools import cached_property, partial, cache
import wcwidth
#
# utilities
#

__all__ = [
    'Box',
    'CharType',
    'Color',
    'Color24',
    'Color4',
    'ComputedStyle',
    'Coordinate',
    'DrawBox',
    'DrawCommand',
    'DrawPixel',
    'DrawStringLine',
    'Frame',
    'InputEvent',
    'LRU_MAX_SIZE',
    'Layout',
    'MeasureTextFunc',
    'MinSize',
    'Pixel',
    'Rect',
    'Result',
    'ResultCreatedWith',
    'ResultData',
    'Screen',
    'StyleAttr',
    'StyleRule',
    'WrapperNode',
    'clamp',
    'even_divide',
    'hex',
    'intersperse',
    'layout_to_result',
    'min_size_constant',
    'min_size_expand',
    'min_size_horizontal',
    'min_size_union',
    'min_size_vertical',
    'rgb',
    'rule_bg',
    'rule_bold',
    'rule_dim',
    'rule_fg',
    'rule_italic',
    'rule_reverse',
    'rule_strike_through',
    'rule_underline',
]

LRU_MAX_SIZE = 128


def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def even_divide(num, denomenator) -> list[int]:
    return [num // denomenator + (1 if x < num % denomenator else 0)  for x in range (denomenator)]

def intersperse[T](iterable: Iterable[T], sep: T) -> Iterable[T]:
    """Yield elements with sep inserted between them.

    Example:
        >>> from functui.classes import intersperse
        >>> list(intersperse([1, 2, 3], 0))
        [1, 0, 2, 0, 3]
    """
    iterator = iter(iterable)
    try:
        first = next(iterator)
    except StopIteration:
        return
    yield first
    for item in iterator:
        yield sep
        yield item


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

class Rect(NamedTuple):
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
        This method is commutative.

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
        This method is commutative.

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
        This method is commutative.

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

        This method is commutative.

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

class StyleAttr(Flag):
    """Flags representing different syles

    Attributes:
        BOLD
        REVERSE
        ITALIC
        UNDERLINE
        STRIKE_THROUGH
        DIM
    """
    BOLD = auto()
    REVERSE = auto()
    ITALIC = auto()
    UNDERLINE = auto()
    STRIKE_THROUGH = auto()
    DIM = auto()

class Color4(IntEnum):
    """ANSI SGR codes for 4 bit colors

    Attributes:
        BLACK:
        RED:
        GREEN:
        YELLOW:
        BLUE:
        MAGENT:
        CYAN:
        WHITE:
        RESET: Dont display any color."""
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7

    BRIGHT_BLACK = 8
    BRIGHT_RED = 9
    BRIGHT_GREEN = 10
    BRIGHT_YELLOW = 11
    BRIGHT_BLUE = 12
    BRIGHT_MAGENTA = 13
    BRIGHT_CYAN = 14
    BRIGHT_WHITE = 15

    RESET = -1


@dataclass(frozen=True, eq=True)
class Color24:
    r: int
    g: int
    b: int

    @property
    @cache
    def hex(self) -> int:
        return (0 | self.r << 16 | self.g << 8 | self.b)

    @property
    @cache
    def hex_str(self) -> str:
        return f"#{self.hex:06x}"


def rgb(r: int, g: int, b: int, /):
    return Color24(r, g, b)


def hex(value: int, /):
    MASK = 0b11111111
    return Color24((value >> 16) & MASK, (value >> 8) & MASK, value & MASK)

Color = int | Color24

# class Color8
@dataclass(frozen=True, eq=True)
class StyleRule:
    """An immutable dataclass for style attributes:

    Attributes:
        fg: Foreground
        bg: Background
        char_style: Styling flags.
    """
    fg: Color | None = None 
    bg: Color | None = None
    add_attrs: StyleAttr = StyleAttr(0)
    remove_attrs: StyleAttr = StyleAttr(0)

    def __or__(self, rule: Self):
        return StyleRule(
            add_attrs=(self.add_attrs | rule.add_attrs),
            remove_attrs=(self.add_attrs | rule.remove_attrs),
            fg=self.fg if rule.fg is None else rule.fg,
            bg=self.bg if rule.bg is None else rule.bg,
        )

@dataclass(frozen=True, eq=True)
class ComputedStyle:
    """An immutable dataclass for style attributes:

    Attributes:
        fg: Foreground
        bg: Background
        char_style: Styling flags.
    """
    fg: Color = Color4.RESET
    bg: Color = Color4.RESET
    attrs: StyleAttr = StyleAttr(0)

    def apply_rule(self, rule: StyleRule):
        return ComputedStyle(
            attrs=(self.attrs | rule.add_attrs) & ~rule.remove_attrs,
            fg=self.fg if rule.fg is None else rule.fg,
            bg=self.bg if rule.bg is None else rule.bg,
        )

rule_bold = StyleRule(add_attrs=StyleAttr.BOLD)
rule_italic = StyleRule(add_attrs=StyleAttr.ITALIC)
rule_strike_through = StyleRule(add_attrs=StyleAttr.STRIKE_THROUGH)
rule_reverse = StyleRule(add_attrs=StyleAttr.REVERSE)
rule_underline = StyleRule(add_attrs=StyleAttr.UNDERLINE)
rule_dim = StyleRule(add_attrs=StyleAttr.DIM)
def rule_fg(color: Color, /):
    return StyleRule(fg=color)
def rule_bg(color: Color, /):
    return StyleRule(bg=color)
# class Style:


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
    style: ComputedStyle = ComputedStyle()

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

    def with_style(self, style: ComputedStyle) -> Self:
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
    """All pixels are assumed to contain the same style"""
    at: Coordinate

DrawCommand: TypeAlias = DrawPixel | DrawBox | DrawStringLine

class MeasureTextFunc(Protocol):
    """A function that measures how long a string is when it is printed.

    Args:
        string (str)
    Returns:
        int: Printed length of the string."""
    def __call__(self, string: str, /) -> int:
        ...

@dataclass(frozen=True, eq=True)
class Frame:
    view_box: Box
    screen_rect: Rect
    default_style: ComputedStyle
    measure_text: MeasureTextFunc = field(hash=False, compare=False)

    def with_style(self, style: ComputedStyle):
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


class MinSize(Protocol):
    """A function that returns a :obj:`Layout`'s minimum size.

    Args:
        measure_text (MeasureTextFunc):
        rect (Rect):
            Available space for the layout. 
            Useful for implementing text wrapping, where the layouts height depends on available width.
    Returns:
        Rect: A Layout's minium size.
    """
    def __call__(self, measure_text: MeasureTextFunc, rect: Rect, /) -> Rect:
        ...



# minsize util functions
def _get_widths_and_heights(children_sizes: Iterable[MinSize], measure_text: MeasureTextFunc, from_size: Rect):
    widths = []
    heights = []
    for min_size in children_sizes:
        result = min_size(measure_text, from_size)
        widths.append(result.width)
        heights.append(result.height)
    return (widths, heights)

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
        widths, heights = _get_widths_and_heights(children_sizes, measure_text, from_size)
        return Rect(
            max(widths),
            sum(heights),
        ) if children_sizes else Rect(0, 0)
    return out

def min_size_horizontal(
    children_sizes: list[MinSize],
) -> MinSize:
    def out(measure_text: MeasureTextFunc, from_size: Rect):
        widths, heights = _get_widths_and_heights(children_sizes, measure_text, from_size)
        return Rect(
            sum(widths),
            max(heights),
        ) if children_sizes else Rect(0, 0)
    return out

def min_size_union(
    children_sizes: list[MinSize],
) -> MinSize:
    def _min_size_union(measure_text: MeasureTextFunc, from_size: Rect):
        widths, heights = _get_widths_and_heights(children_sizes, measure_text, from_size)
        return Rect(
            max(widths),
            max(heights),
        ) if children_sizes else Rect(0, 0)
    return _min_size_union
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


@dataclass(frozen=True)
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
    def __hash__(self) -> int:
        # print("hej", self.func.__module__)
        h = hash((self.func, *self.render.args))
        # print(h)
        return h
    def __eq__(self, value: object, /) -> bool:
        return hash(self) == hash(value)

class WrapperNode(Protocol):
    """A function that creates a layout based on a child layout.

    Args:
        child_layout (Layout):
    Returns:
        Layout: New layout based on child."""
    def __call__(self, child_layout: Layout, /) -> Layout:
        ...

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
            default_style=ComputedStyle(fg=Color4.RESET, bg=Color4.RESET),
            measure_text=measure_text
        ),
        Box(width=dimensions.width, height=dimensions.height),
    )
    result.set_data(ResultCreatedWith(measure_text, screen_size=dimensions))
    return result

def _get_default_data(width: int, height: int):
    return [[Pixel() for _ in range(width)] for _ in range(height)]

class Screen:
    """Represents the text grid of a screen."""
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
                for x in range(box.position.x, box.position.x + box.width):
                    for y in range(box.position.y, box.position.y + box.height):
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

class InputEvent(NamedTuple):
    key_event: str | None = None
    mouse_button_event: str | None = None
    mouse_position_event: Coordinate | None = None
