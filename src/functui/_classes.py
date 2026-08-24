from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Callable, Hashable, Self, Iterable, Any, Protocol, Sequence, TypeAlias, NamedTuple
from enum import Enum, Flag, auto, IntEnum
from abc import ABC, abstractmethod
from functools import cached_property, partial, cache
from ._geometry import Box, Rect, Coordinate
from ._color import Color, Color4, TerminalColor, HEX_TO_XTERM256_DEFINED_COLORS
import wcwidth
import colorsys
#
# utilities
#


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

def measure_char(chr: str, /):
    return wcwidth.wcwidth(chr)
def measure_text(txt: str, /):
    return wcwidth.wcswidth(txt)

#
# General Data Structures
#


type NodeID = Hashable

class StyleAttr(Flag):
    """Flags representing different syles.

    Attributes:
        BOLD
        BLINK
        REVERSE
        ITALIC: Sometimes not supported.
        UNDERLINE
        STRIKE_THROUGH: Sometimes not supported.
        DIM
    """
    BOLD = auto()
    BLINK = auto()
    REVERSE = auto()
    ITALIC = auto()
    UNDERLINE = auto()
    STRIKE_THROUGH = auto()
    DIM = auto()

class BoxData(NamedTuple):
    view_box: Box
    box: Box

    @property
    @cache
    def visible_box(self):
        return self.view_box.intersect(self.box)


class StyleRule(NamedTuple):
    """An immutable dataclass for style attributes.

    Attributes:
        fg: Foreground color.
        bg: Background color.
        add_attrs: Add styling flags.
        remove_attrs: Remove styling flags.
    """
    fg: TerminalColor | None = None 
    bg: TerminalColor | None = None
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
    fg: TerminalColor = Color4.RESET
    bg: TerminalColor = Color4.RESET
    attrs: StyleAttr = StyleAttr(0)

    def apply_rule(self, rule: StyleRule):
        return ComputedStyle(
            attrs=(self.attrs | rule.add_attrs) & ~rule.remove_attrs,
            fg=self.fg if rule.fg is None else rule.fg,
            bg=self.bg if rule.bg is None else rule.bg,
        )



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
    _boxes_by_id: dict[NodeID, BoxData]
    _strips: list[list[Strip]]
    _render_later: list[Callable]
    intermediate_data: IntermediateData = field(default_factory=IntermediateData)


    def set_box_data(self, node_id: NodeID, box: Box, view_box: Box):
        """
        Note:
            May ovveride exisiting entries in this result.
        """
        self._boxes_by_id[node_id] = BoxData(view_box=view_box, box=box)

    def try_box_data(self, node_id: NodeID) -> None | BoxData:
        return self._boxes_by_id.get(node_id, None)

    def expect_box_data(self, node_id: NodeID) -> BoxData:
        return self._boxes_by_id[node_id]

    def with_style(self, style: ComputedStyle):
        return self.__class__(
            view_box=self.view_box,
            screen_rect=self.screen_rect,
            default_style=style,
            measure_text=self.measure_text,
            _strips=self._strips,
            _boxes_by_id=self._boxes_by_id,
            _render_later=self._render_later,
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
            _render_later=self._render_later,
            intermediate_data=self.intermediate_data,
        )
    def with_view_box(self, other_box):
        return Frame(
            view_box=other_box,
            screen_rect=self.screen_rect,
            default_style=self.default_style,
            measure_text=self.measure_text,
            _strips=self._strips,
            _boxes_by_id=self._boxes_by_id,
            _render_later=self._render_later,
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
    def render_later(self, child: Layout, frame: Frame, box: Box):
        self._render_later.append(partial(child.render, frame, box))


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
    """An immutable layout that can be rendered as a string.

    Attributes:
        func: The function that returned this layout. Used to give this layout a name.
        min_size: A function that returns the layouts minimum size based on the size that is available
        render: Render function.

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
    """Information and metadata gathers during layout rendering.

    Attributes:
        dimensions: The screen dimensions the layout was rendered with.
        box_data:
            Dimensions and positions of nodes marked with :func:`functui.nodes.hoverable`
    """
    measure_text: MeasureTextFunc
    dimensions: Rect
    box_data: MappingProxyType[NodeID, BoxData]


@dataclass
class Screen:
    """An intermediate buffer to render layouts to.

    Keeps data between render frames for optimisation purposes.
    Is usefull for overlaying multiple layouts on top of each other."""
    _dimensions: Rect = Rect(-1, -1)
    _strips: list[list[Strip]] = field(default_factory=list)

    @property
    def dimensions(self):
        return self._dimensions

    def set_dimensions(self, new_dimensions: Rect):
        """Will clear screen if dimensions do not match"""
        if self.dimensions != new_dimensions or not len(self._strips):
            background_strip = Strip(
                start=0,
                content=" "*new_dimensions.width,
                style=ComputedStyle(),
                length=new_dimensions.width
            )
            self._strips = [[background_strip] for _ in range(new_dimensions.height)]
            self._dimensions = new_dimensions

    def clear(self):
        for i, line in enumerate(self._strips):
            self._strips[i] = line[:1]

    def overlay_layout(
        self,
        layout: Layout,
        measure_text: MeasureTextFunc = lambda t: wcwidth.wcswidth(t)
    ) -> ResultData:

        render_later = []

        frame = Frame(
            screen_rect=self.dimensions,
            view_box=Box(self.dimensions.width, self.dimensions.height),
            default_style=ComputedStyle(fg=Color4.RESET, bg=Color4.RESET),
            measure_text=measure_text,
            _strips = self._strips,
            _render_later=render_later,
            _boxes_by_id = {},
        )
        layout.render(
            frame, Box(width=self.dimensions.width, height=self.dimensions.height),
        )
        for render in render_later:
            render()

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


