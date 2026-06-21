from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Callable, Hashable, Self, Iterable, Any, Protocol, Sequence, TypeAlias, NamedTuple
from enum import Enum, Flag, auto, IntEnum
from abc import ABC, abstractmethod
from functools import cached_property, partial, cache
from .geometry import Box, Rect, Coordinate

from .color_data import HEX_TO_XTERM256_DEFINED_COLORS
import wcwidth
import colorsys
#
# utilities
#

__all__ = [
    'Box',
    'BoxData',
    'Color',
    'Color24',
    'Color4',
    'ComputedStyle',
    'Coordinate',
    'Frame',
    'Strip',
    'Layout',
    'MeasureTextFunc',
    'MinSize',
    'NodeId',
    'Rect',
    'ResultData',
    'Screen',
    'StyleAttr',
    'StyleRule',
    'WrapperNode',
    'clamp',
    'even_divide',
    'hex',
    'hsl',
    'intersperse',
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
    'compose_strips',
]



def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def even_divide(num, denomenator) -> list[int]:
    return [num // denomenator + (1 if x < num % denomenator else 0) for x in range(denomenator)]

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


type NodeId = Hashable


class BoxData(NamedTuple):
    view_box: Box
    box: Box

    @property
    @cache
    def visible_box(self):
        return self.view_box.intersect(self.box)

class StyleAttr(Flag):
    """Flags representing different syles.

    Attributes:
        BOLD
        BLINK
        REVERSE
        ITALIC
        UNDERLINE
        STRIKE_THROUGH: Is not suported by the curses renderer.
        DIM: Will be interpreted as thinner font weight by the html renderer.
    """
    BOLD = auto()
    BLINK = auto()
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
        MAGENTA:
        CYAN:
        WHITE:
        RESET: Use terminal's default foreground or background color.
        BRIGHT_BLACK:
        BRIGHT_RED:
        BRIGHT_GREEN:
        BRIGHT_YELLOW:
        BRIGGT_BLUE:
        BRIGHT_MAGENTA:
        BRIGHT_CYAN:
        BRIGHT_WHITE:
    """
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


# Some functuionality of this class has been copied over from the textual project.
# https://github.com/Textualize/textual/blob/main/src/textual/color.py
class Color24(NamedTuple):
    """Represent a 24 bit color.

    Attributes:
        r: Red value, an integer from 0 to 255 inclusive.
        g: Green value, an integer from 0 to 255 inclusive.
        b: Blue value, an integer from 0 to 255 inclusive.
        a: Alpha value, a float from 0 to 1.0 inclusive.
    """
    r: int
    g: int
    b: int
    a: float = 1.0

    @property
    @cache
    def hex(self) -> int:
        """Convert to an integer represeting this colors hexadecimal value."""
        return (0 | self.r << 16 | self.g << 8 | self.b)

    @cache
    def to_nearest_8bit(self) -> int:
        distance_to_color = {_color_distance_fast(hex(k), self): v for k, v in HEX_TO_XTERM256_DEFINED_COLORS.items()}
        return distance_to_color[min(distance_to_color.keys())]

    @property
    @cache
    def hex_str(self) -> str:
        return f"#{self.hex:06x}"

    @property
    def normalized(self) -> tuple[float, float, float]:
        return (self.r / 255, self.g / 255, self.b / 255)

    @cache
    def overlay(self, other: Self):
        r1, g1, b1, a1 = self
        r2, g2, b2, a2 = other

        return Color24(
            int(r1 + (r2 - r1) * a2),
            int(g1 + (g2 - g1) * a2),
            int(b1 + (b2 - b1) * a2),
            a1,
        )
    @property
    def brightness(self) -> float:
        """The human perceptual brightness.

        A value of 1 is returned for pure white, and 0 for pure black.
        Other colors lie on a gradient between the two extremes.
        """

        r, g, b = self.normalized
        brightness = (299 * r + 587 * g + 114 * b) / 1000
        return brightness


def _color_distance_fast(a: Color24, b: Color24) -> int:
    return (a.r - b.r)**2 + (a.g - b.g)**2 + (a.b - b.b)**2


def rgb(r: int, g: int, b: int, /):
    """Create a new :obj:`Color24` from rgb parameters."""
    return Color24(r, g, b)

def hsl(h: float, s: float, l: float, /):
    """Create a new :obj:`Color24` from hsl parameters."""
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return Color24(int(r*255), int(g*255), int(b*255))

def hex(value: int, /):
    """Create a new :obj:`Color24` from a hexodecimal integer."""
    MASK = 0b11111111
    return Color24((value >> 16) & MASK, (value >> 8) & MASK, value & MASK)

type Color = int | Color24


class StyleRule(NamedTuple):
    """An immutable dataclass for style attributes.

    Attributes:
        fg: Foreground color.
        bg: Background color.
        add_attrs: Add styling flags.
        remove_attrs: Remove styling flags.
    """
    fg: Color | None = None 
    bg: Color | None = None
    add_attrs: StyleAttr = StyleAttr(0)
    remove_attrs: StyleAttr = StyleAttr(0)

    def __or__(self, rule: Self):
        return StyleRule(
            add_attrs=(self.add_attrs | rule.add_attrs) & ~rule.remove_attrs,
            remove_attrs=(self.remove_attrs),
            fg=self.fg if rule.fg is None else rule.fg,
            bg=self.bg if rule.bg is None else rule.bg,
        )

class ComputedStyle(NamedTuple):
    """An immutable dataclass for style attributes that can be rendered.

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
rule_blink = StyleRule(add_attrs=StyleAttr.BLINK)
rule_italic = StyleRule(add_attrs=StyleAttr.ITALIC)
rule_strike_through = StyleRule(add_attrs=StyleAttr.STRIKE_THROUGH)
rule_reverse = StyleRule(add_attrs=StyleAttr.REVERSE)
rule_underline = StyleRule(add_attrs=StyleAttr.UNDERLINE)
rule_dim = StyleRule(add_attrs=StyleAttr.DIM)
def rule_fg(color: Color, /):
    return StyleRule(fg=color)
def rule_bg(color: Color, /):
    return StyleRule(bg=color)


#
# Ui specific datastructures
#


class MeasureTextFunc(Protocol):
    """A function that measures how long a string is when it is printed.

    Args:
        string (str)
    Returns:
        int: Printed length of the string."""
    def __call__(self, string: str, /) -> int:
        ...

@dataclass(frozen=True)
class Strip:
    start: int
    content: str
    style: ComputedStyle
    length: int


    @classmethod
    def from_widechar_string(cls, start: int, content: str, style: ComputedStyle, len: int):
        new_content = []
        for i in content:
            new_content.append(i)
            if wcwidth.wcwidth(i) == 2:
                new_content.append(" ")

        return cls(
            start=start,
            content="".join(new_content),
            style=style,
            length=len
        )

@dataclass
class IntermediateData():
    _type_to_data: dict[Any, list[Any]] = field(default_factory=dict)

    def try_data[T](self, t: type[T]) -> Iterable[T] | None:
        return self._type_to_data.get(t, None)

    def expect_data[T](self, t: type[T]) -> Iterable[T]:
        return self._type_to_data[t]

    def delete_data(self ,t: type[Any]):
        del self._type_to_data[t]

    def set_data(self, data):
        key = type(data)
        if key in self._type_to_data:
            self._type_to_data[key].append(data)
        else:
            self._type_to_data[key] = [data]

@dataclass
class Frame:
    view_box: Box
    screen_rect: Rect
    default_style: ComputedStyle
    measure_text: MeasureTextFunc = field(hash=False, compare=False)
    _boxes_by_id: dict[NodeId, BoxData]
    _strips: list[list[Strip]]
    intermediate_data: IntermediateData = field(default_factory=IntermediateData)


    def set_box_data(self, node_id: NodeId, box: Box, view_box: Box):
        """
        Note:
            May ovveride exisiting entries in this result.
        """
        self._boxes_by_id[node_id] = BoxData(view_box=view_box, box=box)

    def try_box_data(self, node_id: NodeId) -> None | BoxData:
        return self._boxes_by_id.get(node_id, None)

    def expect_box_data(self, node_id: NodeId) -> BoxData:
        return self._boxes_by_id[node_id]


    def with_style(self, style: ComputedStyle):
        return self.__class__(
            view_box=self.view_box,
            screen_rect=self.screen_rect,
            default_style=style,
            measure_text=self.measure_text,
            _strips=self._strips,
            _boxes_by_id=self._boxes_by_id,
            intermediate_data=self.intermediate_data,
        )

    def shrink_to(self, other_box):
        return Frame(
            view_box=self.view_box.intersect(other_box),
            screen_rect=self.screen_rect,
            default_style=self.default_style,
            measure_text=self.measure_text,
            _strips=self._strips,
            _boxes_by_id=self._boxes_by_id,
            intermediate_data=self.intermediate_data,
        )

    def shrink_to_mutate(self, other_box):
        self.view_box = self.view_box.intersect(other_box)

    def draw_pixel(self, fill: str, at: Coordinate):
        if not self.view_box.is_point_inside(at):
            return 

        self._strips[at.y].append(Strip(at.x, fill, self.default_style, 1))

    def draw_box(
        self,
        fill: str,
        box: Box,
    ):
        box = box.intersect(self.view_box)
        for y in range(box.position.y, box.position.y + box.height):
            self._strips[y].append(
                Strip(box.position.x, fill*box.width, self.default_style, box.width)
            )

    def draw_line_h(
        self,
        fill: str,
        at: Coordinate,
        len: int,
    ):
        self.draw_box(fill, Box(width=len, height=1, position=at).intersect(self.view_box))
        # if not self.view_box.position.y <= at.y < (self.view_box.position.y + self.view_box.height):
        #     return
        #
        # actuall_len = clamp(at.x + len, self.view_box.position.x, self.view_box.position.x + self.view_box.width)
        # self._strips[at.y].append(
        #     Strip(at.x, fill*actuall_len, self.default_style)
        # )

    def draw_line_v(
        self,
        fill: str,
        at: Coordinate,
        len: int,
    ):
        self.draw_box(fill, Box(width=1, height=len, position=at).intersect(self.view_box))

    # def draw_monospace_string_line(
    #     self,
    #     content: str,
    #     at: Coordinate
    # ):
    #     bounds = self.view_box
    #     visible_box = bounds.intersect(Box(len(content), 1, at))
    #
    #     content = content[visible_box.position.y - at.y:v]
    #
    #     relevant_str = []
    #
    #     self._strips
    #

    def draw_string_line(
        self,
        content: str,
        at: Coordinate = Coordinate(0, 0)
    ):
        bounds = self.view_box

        # discard if outside vertically
        #       content
        #         #---#
        #         |   |
        #         #---#
        #       content
        if (at.y < bounds.position.y) or (at.y >= bounds.position.y + bounds.height):
            return

        visual_len = self.measure_text(content)
        outer_x_bound = bounds.position.x + bounds.width

        # discard if outside horizontally
        #         #---#
        # content |   | content
        #         #---#
        if (at.x + visual_len < bounds.position.x) or (at.x >= outer_x_bound):
            return

        # find initial x offset
        #         #---#
        #    content  |
        #    ^^^^^#---#
        required_visual_offset = bounds.position.x - at.x
        x_visual_offset = 0
        index_offset = 0

        if required_visual_offset > 0:
            for char in content:
                x_visual_offset += self.measure_text(char)
                index_offset += 1
                if x_visual_offset >= required_visual_offset:
                    break

        end_at_index = index_offset

        # cut of extra
        #         #---#
        #         |  content
        #         #---#^^^^^

        if at.x + visual_len >= outer_x_bound:
            end_visual_offset_global = at.x + x_visual_offset
            for char in content[index_offset:]:
                if end_visual_offset_global >= outer_x_bound:
                    break

                end_visual_offset_global += self.measure_text(char)
                end_at_index += 1
            string = content[index_offset:end_at_index]
        else:
            string = content[index_offset:]


        # generate output string
        at_final = at + Coordinate(x_visual_offset, 0)

        self._strips[at.y].append(
            Strip.from_widechar_string(
                at_final.x,
                string,
                self.default_style,
                wcwidth.wcswidth(string)
            )
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


class Layout(NamedTuple):
    """An immutable layout that can be rendered as a string

    Attributes:
        func: The function that returned this layout. Used to give this layout a name.
        min_size: Function that returns

    """
    func: Callable
    min_size: MinSize
    render: partial

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

class ResultData(NamedTuple):
    measure_text: MeasureTextFunc
    dimensions: Rect
    box_data: MappingProxyType[NodeId, BoxData]


@dataclass
class Screen:
    _dimensions: Rect = Rect(-1, -1)
    strips: list[list[Strip]] = field(default_factory=list)

    @property
    def dimensions(self):
        return self._dimensions

    def set_dimensions(self, new_dimensions: Rect):
        """Will clear screen if dimensions do not match"""
        if self.dimensions != new_dimensions or not len(self.strips):
            background_strip = Strip(
                start=0,
                content=" "*new_dimensions.width,
                style=ComputedStyle(),
                length=new_dimensions.width
            )
            self.strips = [[background_strip] for _ in range(new_dimensions.height)]
            self._dimensions = new_dimensions

    def clear(self):
        for i, line in enumerate(self.strips):
            self.strips[i] = line[:1]

    def overlay_layout(
        self,
        layout: Layout,
        measure_text: MeasureTextFunc = lambda t: wcwidth.wcswidth(t)
    ) -> ResultData:

        frame = Frame(
            screen_rect=self.dimensions,
            view_box=Box(self.dimensions.width, self.dimensions.height),
            default_style=ComputedStyle(fg=Color4.RESET, bg=Color4.RESET),
            measure_text=measure_text,
            _strips = self.strips,
            _boxes_by_id = {},
        )
        layout.render(
            frame, Box(width=self.dimensions.width, height=self.dimensions.height),
        )

        return ResultData(
            dimensions=self.dimensions,
            measure_text=measure_text,
            box_data=MappingProxyType(frame._boxes_by_id)
        )



# def layout_to_result(
#         layout: Layout,
#         dimensions: Rect,
#         measure_text: MeasureTextFunc = lambda t: wcwidth.wcswidth(t)
# ) -> ComputedResult:
#     """Converts a layout to a result that can be converted to desired output type.
#
#     See Also:
#         To see what to do with the result, read :doc:`../user_guide/io`.
#     """
#     background_strip = Strip(
#         start=0,
#         content=" "*dimensions.width,
#         style=ComputedStyle(),
#         length=dimensions.width
#     )
#     frame = Frame(
#         screen_rect=dimensions,
#         view_box=Box(dimensions.width, dimensions.height),
#         default_style=ComputedStyle(fg=Color4.RESET, bg=Color4.RESET),
#         measure_text=measure_text,
#         _strips = [[background_strip] for _ in range(dimensions.height)],
#         _boxes_by_id = {},
#     )
#     layout.render(
#         frame, Box(width=dimensions.width, height=dimensions.height),
#     )
#     return ComputedResult(frame._strips, ResultData(
#         dimensions=dimensions,
#         measure_text=measure_text,
#         box_data=MappingProxyType(frame._boxes_by_id)
#     ))




#
#          yyy    -- z-index 3
#            jjj  -- z-index 2
#   iii           -- z-index 1 
# xxxxxxxxxxxxxxx -- z-index 0
# | |      | |
# | |      | start at 3
# | |      |
# | |      start at 2
# | |
# | start at 1
# |
# start at 0


def compose_strips(strips: Sequence[Strip]):
    # strips is sorted by z-index (0 at beginning of list)
    if len(strips) == 0:
        return

    strip_index_sorted_by_start = list(range(len(strips)))
    strip_index_sorted_by_start.sort(key=lambda x: strips[x].start)

    # refers to the strips list
    strip_index = strip_index_sorted_by_start[0]

    # refers to the strip_index_sorted_by_start list
    curr_start_index = 0

    # at defined in visual space
    at_visual = 0

    strip = strips[strip_index]
    while True:
        if curr_start_index == len(strip_index_sorted_by_start) - 1:
            next_strip = None
        else:
            next_strip = strips[strip_index_sorted_by_start[curr_start_index+1]]

        # look for next
        if next_strip is not None and next_strip.start <= at_visual:

            # advance to next strip, and upate strip_index to point to the new strip
            curr_start_index += 1
            maybe_strip_index = strip_index_sorted_by_start[curr_start_index]

            if maybe_strip_index < strip_index:
                continue # if next strip is at a lower depth then don't switch yet

            strip_index = maybe_strip_index
            strip = strips[strip_index]

            continue

        # if current is too little (outside of strip range)
        if not (strip.start <= at_visual < (strip.start + strip.length)):

            # go back one in depth
            if strip_index == 0:
                return
            strip_index -= 1
            strip = strips[strip_index]

            continue

        # if not strip switching, then just yield elements
        at_string_index = (at_visual - strip.start)
        segment = strip.content[at_string_index]

        at_visual += wcwidth.wcwidth(segment)
        yield (strip.style, segment)


