from functools import reduce, partial, lru_cache
from enum import Enum, auto, IntFlag
from types import MappingProxyType
from typing import NamedTuple, Protocol, Any, Iterable
from dataclasses import dataclass, field
import re
import math

from .classes import *

__all__ = [
    'BORDER_DOUBLE',
    'BORDER_REGULAR',
    'BORDER_ROUNDED',
    'BORDER_THICK',
    'BorderStyle',
    'LOREM',

    # util
    'combine',

    # containers
    'hbox',
    'vbox',
    'static_box',

    # size manipulations
    'center',
    'clamp',
    'clamp_height',
    'clamp_width',
    'offset',
    'padding',
    'custom_padding',
    'push_rule',
    'shrink',
    'shrink_x',
    'shrink_y',
    'min_width',
    'min_height',

    # styling
    'underline',
    'italic',
    'dim',
    'bold',
    'strike_through',
    'reverse',

    'styled',

    'fg',
    'bg',
    'bg_char',
    'bg_fill',

    'empty',

    # content
    'h_guage',
    'text',
    'v_scroll_bar',
    'nothing',

    # bars
    'vbar',
    'vbar_custom',
    'vbar_double',
    'vbar_thick',
    'hbar',
    'hbar_custom',
    'hbar_double',
    'hbar_thick',

    # borders
    'border',
    'border_double',
    'border_rounded',
    'border_thick',
    'border_with_title',
    'custom_border',
]



#
# Element Utils
#

def combine(*wrapper_nodes: WrapperNode) -> WrapperNode:
    """Combines multiple wrapper nodes into one.

    Examples:
        >>> from functui.common import *
        >>> border_and_center = combine(border, center)
        >>> text("hi") | border | center == text("hi") | border_and_center
        True
    """
    def out(child: Layout):
        # wrapper_nodesr = reversed(wrapper_nodes)
        return reduce(lambda a, b: b(a), wrapper_nodes, child)
    return out

def nothing():
    """A dummy node for situations where a node is required but not needed."""

    return Layout(
        func=nothing,
        min_size=min_size_constant(Rect(0, 0)),
        render=partial(lambda f, b: Result()),
    )

def empty(node: Layout):
    """A dummy wrapper node for situation when a wrapper node is required but not needed.

    This wrapper node may be usefull if you are for example making a button which gets a border around it if it is selected.

    Examples:
        >>> from functui.common import *
        >>> selected = True
        >>> layout = text("button") | (border if selected else empty)
    """
    return node

#
# Text Elements
#

LOREM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

def text(string: str):
    """A simple text node.

    Args:
        string: A string that may include new line characters.

    Examples:
        >>> from functui import layout_to_str, Rect
        >>> from functui.common import text
        >>> layout = text("foo\\nbar\\nbaz")
        >>> print(layout_to_str(layout, Rect(3, 3)))
        foo
        bar
        baz

    """
    split_string = tuple(string.split('\n'))
    return Layout(
        func=text,
        min_size = lambda measure_text, _: Rect(
            width=max([measure_text(i) for i in split_string]),
            height=len(split_string)
        ),
        render = partial(_text_render, split_string)
    )

@lru_cache(LRU_MAX_SIZE)
def _text_render(text: tuple[str, ...], frame: Frame, box: Box):
    res = Result()
    for y, line in enumerate(text):
        res.draw_string_line(frame, line, box.position + Coordinate(0, y))
    return res


#
# Border Elements
#


class WeightMap(NamedTuple):
    top: int
    bottom: int
    left: int
    right: int


def _overlay_weight_maps(*maps: WeightMap) -> WeightMap:
    return WeightMap(*(max(dir) for dir in zip(*maps))) # pick highest weights along cardinal direction


class _GetIntersection(Protocol):
    def __call__(self, weight_map: WeightMap, /) -> str | None:
        ...
def _get_default_intersection(weight_map: WeightMap, /):
    return INTERSECTION_MAP.get(weight_map, None)

@dataclass(frozen=True, eq=True)
class BorderStyle:
    """Data structure that represents a border, may be used in :obj:`border_custom`."""
    line_v: str
    line_h: str
    corner_tl: str
    corner_tr: str
    corner_br: str
    corner_bl: str

    # weight_map: WeightMap
    # get_intersection: GetIntersection


INTERSECTION_MAP = {
    WeightMap(1, 1, 0, 1): "├",
    WeightMap(2, 1, 0, 1): "┝",
    WeightMap(1, 2, 0, 1): "┞",
    WeightMap(2, 2, 0, 1): "┟",
    WeightMap(1, 1, 0, 2): "┠",
    WeightMap(2, 1, 0, 2): "┡",
    WeightMap(1, 2, 0, 2): "┢",
    WeightMap(2, 2, 0, 2): "┣",
    WeightMap(3, 3, 0, 3): "╠",
    WeightMap(3, 3, 0, 1): "╟",
    WeightMap(1, 1, 0, 3): "╞",

    WeightMap(1, 1, 1, 0): "┤",
    WeightMap(2, 1, 1, 0): "┥",
    WeightMap(1, 2, 1, 0): "┦",
    WeightMap(2, 2, 1, 0): "┧",
    WeightMap(1, 1, 2, 0): "┨",
    WeightMap(2, 1, 2, 0): "┩",
    WeightMap(1, 2, 2, 0): "┪",
    WeightMap(2, 2, 2, 0): "┫",
    WeightMap(3, 3, 3, 0): "╣",
    WeightMap(3, 3, 1, 0): "╢",
    WeightMap(1, 1, 3, 0): "╡",

    WeightMap(0, 1, 1, 1): "┬",
    WeightMap(0, 1, 2, 1): "┭",
    WeightMap(0, 1, 1, 2): "┮",
    WeightMap(0, 1, 2, 2): "┯",
    WeightMap(0, 2, 1, 1): "┰",
    WeightMap(0, 2, 2, 1): "┱",
    WeightMap(0, 2, 1, 2): "┲",
    WeightMap(0, 2, 2, 2): "┳",
    WeightMap(0, 3, 3, 3): "╦",
    WeightMap(0, 1, 3, 3): "╤",
    WeightMap(0, 3, 1, 1): "╥",

    WeightMap(1, 0, 1, 1): "┴",
    WeightMap(1, 0, 2, 1): "┵",
    WeightMap(1, 0, 1, 2): "┶",
    WeightMap(1, 0, 2, 2): "┷",
    WeightMap(2, 0, 1, 1): "┸",
    WeightMap(2, 0, 2, 1): "┹",
    WeightMap(2, 0, 1, 2): "┺",
    WeightMap(2, 0, 2, 2): "┻",
    WeightMap(3, 0, 3, 3): "╩",
    WeightMap(3, 0, 1, 1): "╨",
    WeightMap(1, 0, 3, 3): "╧",

    WeightMap(1, 1, 1, 1): "┼",
    WeightMap(2, 1, 1, 1): "┽",
    WeightMap(1, 2, 1, 1): "┾",
    WeightMap(2, 2, 1, 1): "┿",
    WeightMap(1, 1, 2, 1): "╀",
    WeightMap(2, 1, 2, 1): "╁",
    WeightMap(1, 2, 2, 1): "╂",
    WeightMap(2, 2, 2, 1): "╃",
    WeightMap(1, 1, 1, 2): "╄",
    WeightMap(2, 1, 1, 2): "╅",
    WeightMap(1, 2, 1, 2): "╆",
    WeightMap(2, 2, 1, 2): "╇",
    WeightMap(1, 1, 2, 2): "╈",
    WeightMap(2, 1, 2, 2): "╉",
    WeightMap(1, 2, 2, 2): "╊",
    WeightMap(2, 2, 2, 2): "╋",
    WeightMap(3, 3, 3, 3): "╬",
    WeightMap(3, 3, 1, 1): "╫",
    WeightMap(1, 1, 3, 3): "╪",
}

BORDER_ROUNDED = BorderStyle(
    line_v="│",
    line_h="─",
    corner_tl="╭",
    corner_tr="╮",
    corner_bl="╰",
    corner_br="╯",
)
BORDER_REGULAR = BorderStyle(
    line_v="│",
    line_h="─",
    corner_tl="┌",
    corner_tr="┐",
    corner_bl="└",
    corner_br="┘",
)

BORDER_THICK = BorderStyle(
    line_v="┃",
    line_h="━",
    corner_tl="┏",
    corner_tr="┓",
    corner_bl="┗",
    corner_br="┛",
)

BORDER_DOUBLE = BorderStyle(
    line_v="║",
    line_h="═",
    corner_tl="╔",
    corner_tr="╗",
    corner_bl="╚",
    corner_br="╝",
)

def vbar_custom(char: str = "|"):
    """Vertical bar build with a custom character."""
    return Layout(
        func=vbar_custom,
        min_size=min_size_constant(Rect(1, 1)),
        render=partial(_vbar_render, char)
    )
@lru_cache(LRU_MAX_SIZE)
def _vbar_render(char: str, frame: Frame, box: Box):
    res = Result()
    res.draw_box(frame, char, Box(1, box.height, box.position))
    return res
def hbar_custom(char: str="-"):
    """Horizonatal bar build with a custom character."""
    return Layout(
        func=hbar_custom,
        min_size=min_size_constant(Rect(1, 1)),
        render=partial(_hbar_render, char)
    )
@lru_cache(LRU_MAX_SIZE)
def _hbar_render(char: str, frame: Frame, box: Box):
    res = Result()
    res.draw_box(frame, char, Box(box.width, 1, box.position))
    return res

vbar = vbar_custom(BORDER_REGULAR.line_v)
"""Vertical bar."""
vbar_thick = vbar_custom(BORDER_THICK.line_v)
"""A thick vertical bar."""
vbar_double = vbar_custom(BORDER_DOUBLE.line_v)
"""A double vertical bar."""
hbar = hbar_custom(BORDER_REGULAR.line_h)
"""Horizontal bar."""
hbar_thick = hbar_custom(BORDER_THICK.line_h)
"""A thick horizontal bar."""
hbar_double = hbar_custom(BORDER_DOUBLE.line_h)
"""A double horizontal bar."""

def custom_border(style: BorderStyle) -> WrapperNode:
    """Puts a border around a layout in a custom style."""
    def _custom_border(child: Layout):
        return Layout(
            func=custom_border,
            min_size=min_size_expand(child.min_size, 2, 2),
            render=partial(_border_render, style, child),
        )
    return _custom_border


border = custom_border(style=BORDER_REGULAR)
"""Puts a border around a layout."""
border_rounded = custom_border(style=BORDER_ROUNDED)
"""Puts a rounded border around a layout."""
border_thick = custom_border(style=BORDER_THICK)
"""Puts a thick border around a layout."""
border_double = custom_border(style=BORDER_DOUBLE)
"""Puts a double border around a layout."""

@lru_cache(LRU_MAX_SIZE)
def _border_render(style: BorderStyle, child: Layout, frame: Frame, box: Box):
    res = Result()
    res.draw_box(frame, fill=style.line_v, box=Box(1, box.height, box.position))
    res.draw_box(frame, fill=style.line_h, box=Box(box.width, 1, box.position))
    res.draw_box(frame, fill=style.line_v, box=Box(1, box.height, box.position + Coordinate(box.width-1, 0)))
    res.draw_box(frame, fill=style.line_h, box=Box(box.width, 1, box.position + Coordinate(0, box.height-1)))
    res.draw_pixel(frame, fill=style.corner_tl, at=box.position + Coordinate(0, 0))
    res.draw_pixel(frame, fill=style.corner_tr, at=box.position + Coordinate(box.width-1, 0))
    res.draw_pixel(frame, fill=style.corner_br, at=box.position + Coordinate(box.width-1, box.height-1))
    res.draw_pixel(frame, fill=style.corner_bl, at=box.position + Coordinate(0, box.height-1))
    res.add_children_after([child.render(frame, box.resize(-1, -1, -1, -1))])
    return res

@dataclass
class BorderConnection:
    position: Coordinate
    weight_map: WeightMap

# def _connecting_border_render(
#     weight_map: WeightMap,
#     style: BorderStyle,
#     child: Layout,
#     frame: Frame,
#     box: Box
# ):
#     child_res = child.render(frame, box.resize(-1, -1, -1, -1))
#     res = Result()
#     res.draw_box(frame, fill=style.line_v, box=Box(1, box.height, box.position))
#     res.draw_box(frame, fill=style.line_h, box=Box(box.width, 1, box.position))
#     res.draw_box(frame, fill=style.line_v, box=Box(1, box.height, box.position + Coordinate(box.width-1, 0)))
#     res.draw_box(frame, fill=style.line_h, box=Box(box.width, 1, box.position + Coordinate(0, box.height-1)))
#     res.draw_pixel(frame, fill=style.corner_tl, at=box.position + Coordinate(0, 0))
#     res.draw_pixel(frame, fill=style.corner_tr, at=box.position + Coordinate(box.width-1, 0))
#     res.draw_pixel(frame, fill=style.corner_br, at=box.position + Coordinate(box.width-1, box.height-1))
#     res.draw_pixel(frame, fill=style.corner_bl, at=box.position + Coordinate(0, box.height-1))
#
#     if connections := child_res.try_data():
#         for connection in connections:
#             # top
#             if connection.position.y == box.position.y:
#                 if intersection := style.get_intersection(overlay_weight_maps(connection.weight_map, keep_weight_direction(weight_map, Direction.UP))):
#                     res.draw_pixel(frame, fill=intersection)
#
#                 # if intersection := style.get_intersection(connection.weight_map | (weight_map & MASK_WEIGHT_TOP)):
#                 #     res.draw_pixel(frame, fill=intersection)
#
#             elif connection.position.y == box.position.y + box.height - 1:
#                 if intersection := style.get_intersection(overlay_weight_maps(connection.weight_map, keep_weight_direction(weight_map, Direction.DOWN))):
#                     res.draw_pixel(frame, fill=intersection)
#             ...
#
#
#
#
#
#     res.add_children_after([child_res])
#     return res


#
# Styling Elements
#
# def styled(elem: Applicable[Node, Node], child: fg:Color|None=None, bg:Color|None=None, style: CharStyle):
#     return Node(
#         func=styled,
#         hash=(elem, fg, bg, style),
#         min_size=child.min_size,
#         render=lambda f, b: elem()
#     )

# def _set_pixel_style(child, fg, bg, style):
#     return Node(
#         func=_set_pixel_style,
#         min_size=child.min_size,
#         render=partial()
#     )

# def _set_pixel_style_render()


def _push_rule(rule: StyleRule, child: Layout):
    return Layout(
        func=_push_rule,
        min_size=child.min_size,
        render=partial(_push_rule_render, child, rule)
    )
def _push_rule_render(child: Layout, rule: StyleRule, frame: Frame, box: Box):
    return child.render(
        frame.with_style(frame.default_style.apply_rule(rule)),
        box
    )
def push_rule(rule: StyleRule) -> WrapperNode:
    """Use style rule for this wrapper node's descendants unless overriden."""
    return partial(_push_rule, rule)

def _force_style(style: ComputedStyle, child: Layout):
    return Layout(
        func=_force_style,
        min_size=child.min_size,
        render=partial(_force_style_render, child, style)
    )
def _force_style_render(child: Layout, style: ComputedStyle, frame: Frame, box: Box):
    return child.render(
        frame.with_style(style),
        box
    )

def bold(node: Layout):
    """Style all descendants as bold.

    See Also:
        If you want to style only certain wrapper nodes concider using :obj:`styled`
    """
    return _push_rule(rule_bold, node)

def reverse(node: Layout):
    """Style all descendants as reverse.

    See Also:
        If you want to style only certain wrapper nodes concider using :obj:`styled`
    """
    return _push_rule(rule_reverse, node)

def underline(node: Layout):
    """Style all descendants as underlined.

    See Also:
        If you want to style only certain wrapper nodes concider using :obj:`styled`
    """
    return _push_rule(rule_underline, node)

def italic(node: Layout):
    """Style all descendants as italic.

    See Also:
        If you want to style only certain wrapper nodes concider using :obj:`styled`
    """
    return _push_rule(rule_italic, node)

def strike_through(node: Layout):
    """Style all descendants as strike_through.

    See Also:
        If you want to style only certain wrapper nodes concider using :obj:`styled`
    """
    return _push_rule(rule_strike_through, node)
def dim(node: Layout):
    """Style all descendants as dim.

    See Also:
        If you want to style only certain wrapper nodes concider using :obj:`styled`
    """
    return _push_rule(rule_dim, node)


# def _fg_render(color: Any, child: Node, frame: Frame, box: Box) -> Result:
#         return child.render(
#             frame.with_style(Style(
#                 fg_color=color,
#                 bg_color=frame.default_pixel.bg_color,
#                 style=frame.default_pixel.style
#             )),
#             box
#         )
def fg(color: Color) -> WrapperNode:
    """Style all descendants with specified foreground.

    Styling may be ovverriden with another styling node.

    See Also:
        If you want to style only certain wrapper nodes concider using :obj:`styled`
    """
    return partial(_push_rule, rule_fg(color))
def bg(color: Color) -> WrapperNode:
    """Style all descendants with specified background.

    Styling may be ovverriden with another styling node.

    See Also:
        If you want to style only certain wrapper nodes concider using :obj:`styled`
    """
    return partial(_push_rule, rule_bg(color))

def styled(node: WrapperNode, rule: StyleRule) -> WrapperNode:
    """Style a wrapper node with specified rule

    As with all other styling nodes,
    styles assigned with previous nodes will be kept unless overridden.

    Tip:
        If you want to style multiple wrapper nodes with same style concider using :obj:`combine`.

    Args:
        node: Wrapper node to be styled.
        style: Style to assign to the wrapper node

    """
    def _styled(child: Layout):
        composed_child = node(child)
        return Layout(
            func=styled,
            min_size=composed_child.min_size,
            render=partial(_styled_render, child, node, rule)
        )
    return _styled

def _styled_render(child: Layout, node: WrapperNode, rule: StyleRule, frame, box):
    return _push_rule(rule, node(
            _force_style(frame.default_style, child)
        )
    ).render(frame, box)
#
# Containers
#

def static_box(children: Iterable[Layout]) -> Layout:
    """A container node that does not arrange its children in any way
    
    Usefull if you want to draw nodes on top of each other.

    Args:
        children:
            Children will be rendered in order.
            (First child rendered first)
    Examples:
        >>> from functui import Rect, layout_to_str
        >>> from functui.common import *
        >>> layout = static_box([
        ...     text("first") | border | shrink,
        ...     text("second") | border | shrink | offset(1, 2)
        ... ]) | border
        >>> print(layout_to_str(layout, Rect(10, 8)))
        ┌────────┐
        │┌─────┐ │
        ││first│ │
        │└┌──────│
        │ │second│
        │ └──────│
        │        │
        └────────┘
    """
    children = tuple(children)
    return Layout(
        func=static_box,
        min_size=min_size_union([i.min_size for i in children]),
        render=partial(_static_box_render, children),
    )
def _static_box_render(children: tuple[Layout, ...], frame: Frame, box: Box):
    res = Result()
    for child in children:
        res.add_children_after([child.render(frame.shrink_to(box), box)])
    return res

def vbox(children: Iterable[Layout], at_y: int=0):
    """A container node that arranges its chilren verticaly.

    Children will be shrunk to their minimum size along the y axis.

    Args:
        children:
        at_y:
            Y coordinate to start rendering children at.
            Usefull for implementing scrolling.
    """
    children = tuple(children)
    return Layout(
        func=vbox,
        min_size=min_size_vertical([i.min_size for i in children]),
        render=partial(_vbox_render, children, at_y)
    )

@lru_cache(LRU_MAX_SIZE)
def _vbox_render(children: Iterable[Layout], at_y: int, frame: Frame, box: Box):
    res=Result()
    for node in children:
        child_min_size = node.min_size(frame.measure_text, Rect(box.width, 9999))
        child_box = Box(box.width, child_min_size.height).offset_by(box.position + Coordinate(0, at_y))

        at_y += child_box.height
        
        # # dont do commands for boxes out of bounds who are above
        # if at_y < 0:
        #     continue
        res.add_children_after([
                node.render(frame.shrink_to(child_box.intersect(box)), child_box)
        ])
        # if at_y > box.height:
        #     break

    return res

def hbox(children: Iterable[Layout], at_x: int=0):
    """A container node that arranges its chilren Horizontaly.

    Children will be shrunk to their minimum size along the x axis.

    Args:
        children:
        at_x:
            X coordinate to start rendering children at.
            Usefull for implementing scrolling.
    """
    children = tuple(children)
    return Layout(
        func=hbox,
        min_size=min_size_horizontal([i.min_size for i in children]),
        render=partial(_hbox_render, children, at_x)
    )
@lru_cache(LRU_MAX_SIZE)
def _hbox_render(children: Iterable[Layout], at_x: int, frame: Frame, box: Box):
    res=Result()
    for node in children:
        child_min_size = node.min_size(frame.measure_text, box.rect)
        child_box = Box(child_min_size.width, box.height).offset_by(box.position + Coordinate(at_x, 0))
        res.add_children_after([
            node.render(frame.shrink_to(child_box.intersect(box)), child_box)
        ])
        at_x += child_box.width
    return res

def center(child: Layout):
    """Shrink and center child layout in remaining space"""
    return Layout(
        func=center,
        min_size=child.min_size,
        render=partial(_center_render, child)
    )

def _center_render(child: Layout, frame: Frame, box: Box):
    min_size = child.min_size(frame.measure_text, box.rect)
    empty_space_x = even_divide(box.width - min_size.width, 2)
    empty_space_y = even_divide(box.height - min_size.height, 2)
    return child.render(
        frame,
        box.resize(
            top=-empty_space_y[0],
            bottom=-empty_space_y[1],
            left=-empty_space_x[0],
            right=-empty_space_x[1]
        )
    )
#
#
def bg_char(char: str) -> WrapperNode:
    """Fill background with char"""
    def out(child: Layout):
        return Layout(
            func=bg_char,
            min_size=child.min_size,
            render=partial(_bg_char_render, char, child)
        )

    return out
def _bg_char_render(char: str, child: Layout, frame: Frame, box: Box):
    res = Result()
    res.draw_box(frame, char, box)
    res.add_children_after([child.render(frame, box)])
    return res

bg_fill = bg_char(" ")
"""Fill background with whitespace.

Usefull if you want to fill background with a color using :obj:`bg` or :obj:`styled`"""


def border_with_title(title: Layout, border_node=border):
    """Border with a title attached on top.

    Args:
        title: Layout to render on top.
        border_node: WrapperNode to put around child layout."""
    def out(child: Layout):
        return static_box([
            border_node(child),
            shrink_y(custom_padding(0, 0, 1, 1)(title)),
        ])
    return out


#
# sizing manipulations
#

def _shrink_custom(x: bool, y: bool):
    def out(child: Layout):
        return Layout(
            func=_shrink_custom,
            min_size=child.min_size,
            render=partial(_shrink_render, x, y, child),
        )
    return out

def _shrink_render(x: bool, y: bool, child: Layout, frame: Frame, box: Box):
    min_size = child.min_size(frame.measure_text, box.rect)
    child_box = Box(
        min_size.width if x else box.width,
        min_size.height if y else box.height,
        box.position
    )
    return child.render(frame, child_box)

shrink = _shrink_custom(True, True)
"""Shrink child layout to its minimum size"""

shrink_y = _shrink_custom(False, True)
"""Shrink child layout to its minimum size along the y axis"""

shrink_x = _shrink_custom(True, False)
"""Shrink child layout to its minimum size along the x axis"""

def custom_padding(
    top: int = 0,
    bottom: int = 0,
    left: int = 0,
    right: int = 0,
) -> WrapperNode:
    """Add padding / Shrink a layout by differences"""
    def out(child: Layout):
        return Layout(
            func=custom_padding,
            min_size=min_size_expand(child.min_size, left+right, top+bottom),
            render=partial(_custom_padding_render, top, bottom, left, right ,child),
        )
    return out

def _custom_padding_render(top, bottom, left, right, child, frame: Frame, box: Box):
    return child.render(frame, box.resize(-top, -bottom, -left, -right))

padding = custom_padding(left=1, right=1)
"""Add padding to left and right of a child layout.

Eqivelent to :obj:`custom_padding```(left=1, right=1)``."""


def offset(x: int=0, y: int=0) -> WrapperNode:
    """Offset layout by a difference

    Positive values move down and right.
    Negative values of move up and left."""
    coord = Coordinate(x, y)
    def out(child: Layout):
        return Layout(
            func=offset,
            min_size=min_size_expand(child.min_size, x, y),
            render=partial(_offset_render, coord, child),
        )
    return out


@lru_cache(LRU_MAX_SIZE)
def _offset_render(by: Coordinate, node: Layout, frame: Frame, box: Box):
    return node.render(frame, box.offset_by(by).resize(top=-by.y, right=-by.x))


def clamp_width(width: int):
    """Limit width of a child layout."""
    def out(child: Layout):
        return Layout(
            func=clamp_width,
            min_size=lambda mtf, r: child.min_size(mtf, r.clamp_width(width)).clamp_width(width),
            render=partial(_clamp_width_render, width, child),
        )
    return out
def _clamp_width_render(width, child, frame, box):
    return child.render(frame, box.using_rect(box.rect.clamp_width(width)))

def clamp_height(height: int):
    """Limit height of a child layout."""
    def out(child: Layout):
        return Layout(
            func=clamp_height,
            min_size=lambda mtf, r: child.min_size(mtf, r.clamp_height(height)).clamp_height(height),
            render=partial(_clamp_height_render, height, child)
        )
    return out
def _clamp_height_render(height, child, frame, box):
    return child.render(frame, box.using_rect(box.rect.clamp_height(height)))

def min_width(value: int):
    """Set a minimum width."""
    def _min_width(child: Layout):
        return Layout(
            func=min_width,
            min_size=lambda mtf, r: child.min_size(mtf, r).union(Rect(value, 0)),
            render=child.render
        )
    return _min_width
def min_height(value: int):
    """Set a minimum height."""
    def _min_height(child: Layout):
        return Layout(
            func=min_height,
            min_size=lambda mtf, r: child.min_size(mtf, r).union(Rect(0, value)),
            render=child.render
        )
    return _min_height



#
# V_PROGRESS = " ▁▂▃▄▅▆▇█"
#

# # ╵╷│
#
def h_guage(progress: int):
    return Layout(
        func=h_guage,
        min_size=min_size_constant(Rect(1, 1)),
        render=partial(_h_guage_render, "#", progress),
    )

def _h_guage_render(progress_str: str, progress: int, frame: Frame, box: Box) -> Result:
    start_at_pixel = box.width * progress
    start_at_pixel_int = math.floor(start_at_pixel)
    start_at_progress = start_at_pixel - start_at_pixel_int
    res = Result()
    res.draw_box(frame, progress_str[0], Box(start_at_pixel_int, 1 ,box.position))
    res.draw_pixel(frame, progress_str[(len(progress_str)-1) * start_at_progress], box.position + Coordinate(start_at_pixel_int, 0))
    return res



def v_scroll_bar(start: float, showing: float):
    return Layout(
        func=v_scroll_bar,
        min_size=min_size_constant(Rect(1, 1)),
        render=partial(_v_scroll_bar_render, start, showing)

    )
def _v_scroll_bar_render(start: float, showing: float, frame: Frame, box: Box) -> Result:
    start_at_pixel = box.height * start
    start_at_pixel_int = math.floor(start_at_pixel)
    start_at_progress = abs(start_at_pixel - start_at_pixel_int -1)

    end_at_pixel = box.height * start + box.height * showing # should be clampt
    end_at_pixel_int = math.floor(end_at_pixel)
    end_at_progress = end_at_pixel - end_at_pixel_int

    match [start_at_progress > 0.33, start_at_progress > 0.66]:
        case [True, True]:
            start_char = "│"
        case [True, False]:
            start_char = "╷"
        case _:
            start_char = " "

    match [end_at_progress > 0.33, end_at_progress > 0.66]:
        case [True, True]:
            end_char = "│"
        case [True, False]:
            end_char = "╵"
        case _:
            end_char = " "

    res = Result()
    for i in range(box.height):
        if i == start_at_pixel_int:
            res.draw_pixel(frame, start_char, box.position + Coordinate(0, i))
        elif i == end_at_pixel_int:
            res.draw_pixel(frame, end_char, box.position + Coordinate(0, i))
        elif start_at_pixel_int < i < end_at_pixel_int:
            res.draw_pixel(frame, "│", box.position + Coordinate(0, i))
    return res

