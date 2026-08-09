"""Usefull nodes."""
from functools import reduce, partial, lru_cache
from enum import Enum, auto, IntFlag
from types import MappingProxyType
from typing import TYPE_CHECKING, NamedTuple, Protocol, Any, Iterable
from dataclasses import dataclass, field
import re
import math

from ._classes import *



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
    def _combine(child: Layout):
        # wrapper_nodesr = reversed(wrapper_nodes)
        return reduce(lambda a, b: b(a), wrapper_nodes, child)
    return _combine

def nothing(size: Rect=Rect(0, 0)):
    """A dummy node for situations where a node is required but not needed."""

    return Layout(
        func=nothing,
        min_size=min_size_constant(size),
        render=partial(lambda f, b: None),
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

def _text_render(text: tuple[str, ...], frame: Frame, box: Box):
    frame.shrink_to_mutate(box)
    for y, line in enumerate(text):
        frame.draw_string_line(line, box.position + Coordinate(0, y))



#
# Border Elements
#








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


def _push_rule(rule: StyleRule, child: Layout):
    return Layout(
        func=_push_rule,
        min_size=child.min_size,
        render=partial(_push_rule_render, child, rule)
    )
def _push_rule_render(child: Layout, rule: StyleRule, frame: Frame, box: Box):
    frame.default_style = frame.default_style.apply_rule(rule)
    return child.render(
        frame,
        box
    )
def style(rule: StyleRule) -> WrapperNode:
    """Use style rule for this wrapper node's descendants unless overriden."""
    return partial(_push_rule, rule)

def _force_style(style: ComputedStyle, child: Layout):
    return Layout(
        func=_force_style,
        min_size=child.min_size,
        render=partial(_force_style_render, child, style)
    )
def _force_style_render(child: Layout, style: ComputedStyle, frame: Frame, box: Box):
    frame.default_style = style
    return child.render(
        frame,
        box
    )

def bold(node: Layout):
    """Style all descendants as bold.

    See Also:
        If you want to style only certain wrapper nodes concider using :obj:`styled`
    """
    return _push_rule(StyleRule(add_attrs=StyleAttr.BOLD), node)

def reverse(node: Layout):
    """Style all descendants as reverse.

    See Also:
        If you want to style only certain wrapper nodes concider using :obj:`styled`
    """
    return _push_rule(StyleRule(add_attrs=StyleAttr.REVERSE), node)

def underline(node: Layout):
    """Style all descendants as underlined.

    See Also:
        If you want to style only certain wrapper nodes concider using :obj:`styled`
    """
    return _push_rule(StyleRule(add_attrs=StyleAttr.UNDERLINE), node)

def italic(node: Layout):
    """Style all descendants as italic.

    See Also:
        If you want to style only certain wrapper nodes concider using :obj:`styled`
    """
    return _push_rule(StyleRule(add_attrs=StyleAttr.ITALIC), node)

def strike_through(node: Layout):
    """Style all descendants as strike_through.

    See Also:
        If you want to style only certain wrapper nodes concider using :obj:`styled`
    """
    return _push_rule(StyleRule(add_attrs=StyleAttr.STRIKE_THROUGH), node)
def dim(node: Layout):
    """Style all descendants as dim.

    See Also:
        If you want to style only certain wrapper nodes concider using :obj:`styled`
    """
    return _push_rule(StyleRule(add_attrs=StyleAttr.DIM), node)

def blink(node: Layout):
    """Style all descendants as blink.

    Use this sparingly.

    See Also:
        If you want to style only certain wrapper nodes concider using :obj:`styled`
    """
    return _push_rule(StyleRule(add_attrs=StyleAttr.BLINK), node)

def fg(color: TerminalColor) -> WrapperNode:
    """Style all descendants with specified foreground.

    Styling may be ovverriden with another styling node.

    See Also:
        If you want to style only certain wrapper nodes concider using :obj:`styled`
    """
    return partial(_push_rule, StyleRule(fg=color))
def bg(color: TerminalColor) -> WrapperNode:
    """Style all descendants with specified background.

    Styling may be ovverriden with another styling node.

    See Also:
        If you want to style only certain wrapper nodes concider using :obj:`styled`
    """
    return partial(_push_rule, StyleRule(bg=color))

def styled(node: WrapperNode, rule: StyleRule) -> WrapperNode:
    """Style a wrapper node with specified rule"""
    def _styled(child: Layout):
        composed_child = node(child)
        return Layout(
            func=styled,
            min_size=composed_child.min_size,
            render=partial(_styled_render, child, node, rule)
        )
    return _styled

def styled_bg(node: WrapperNode, color: TerminalColor) -> WrapperNode:
    """Style a wrapper node with specified background"""
    def _styled(child: Layout):
        composed_child = node(child)
        return Layout(
            func=styled,
            min_size=composed_child.min_size,
            render=partial(_styled_render, child, node, StyleRule(bg=color))
        )
    return _styled

def styled_fg(node: WrapperNode, color: TerminalColor) -> WrapperNode:
    """Style a wrapper node with specified foreground"""
    def _styled(child: Layout):
        composed_child = node(child)
        return Layout(
            func=styled,
            min_size=composed_child.min_size,
            render=partial(_styled_render, child, node, StyleRule(fg=color))
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
    for child in children:
        child.render(frame.shrink_to(box), box)

CONTAINER_MARGIN_BEFORE_INVISIBLE = 2

def vbox(children: Iterable[Layout], at_y: int=0):
    """A container node that arranges its chilren verticaly.

    Children will be shrunk to their minimum size along the y axis.

    Args:
        children:
        at_y:
            Y coordinate to start rendering children at.
            Usefull for implementing scrolling.
    """
    return Layout(
        func=vbox,
        min_size=min_size_vertical([i.min_size for i in children]),
        render=partial(_vbox_render, children, at_y)
    )

def _vbox_render(children: Iterable[Layout], at_y: int, frame: Frame, box: Box):
    visible_box = frame.view_box.intersect(box)

    start = visible_box.position.y
    end = start + visible_box.height

    at_y += box.position.y

    for node in children:
        child_min_size = node.min_size(frame.measure_text, Rect(box.width, 9999))

        child_box = Box(
            box.width,
            child_min_size.height,
            Coordinate(box.position.x, at_y)
        )

        # out = 0
        if (at_y + child_box.height) <= (start-CONTAINER_MARGIN_BEFORE_INVISIBLE):
            # out = 1
            at_y += child_box.height
            continue

        elif at_y >= (end + CONTAINER_MARGIN_BEFORE_INVISIBLE):
            # out = 1
            break

        node.render(frame.shrink_to(child_box.intersect(visible_box)), child_box)
        # (node | fg(Color4.RED) if out else node).render(frame.shrink_to(frame.view_box), child_box)


        at_y += child_box.height


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

def _hbox_render(children: Iterable[Layout], at_x: int, frame: Frame, box: Box):
    for node in children:
        child_min_size = node.min_size(frame.measure_text, box.rect)
        child_box = Box(child_min_size.width, box.height).offset_by(box.position + Coordinate(at_x, 0))

        if at_x < -CONTAINER_MARGIN_BEFORE_INVISIBLE:
            continue

        node.render(frame.shrink_to(child_box.intersect(box)), child_box)

        if at_x > box.width + CONTAINER_MARGIN_BEFORE_INVISIBLE:
            break

        at_x += child_box.width

def center(child: Layout):
    """Shrink and center child layout in remaining space."""
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
def vcenter(child: Layout):
    """Shrink and center child layout along the y axis."""
    return Layout(
        func=vcenter,
        min_size=child.min_size,
        render=partial(_vcenter_render, child)
    )
def _vcenter_render(child: Layout, frame: Frame, box: Box):
    min_size = child.min_size(frame.measure_text, box.rect)
    empty_space_y = even_divide(box.height - min_size.height, 2)
    return child.render(
        frame,
        box.resize(
            top=-empty_space_y[0],
            bottom=-empty_space_y[1],
        )
    )
def hcenter(child: Layout):
    """Shrink and center child layout along the x axis."""
    return Layout(
        func=hcenter,
        min_size=child.min_size,
        render=partial(_hcenter_render, child)
    )

def _hcenter_render(child: Layout, frame: Frame, box: Box):
    min_size = child.min_size(frame.measure_text, box.rect)
    empty_space_x = even_divide(box.width - min_size.width, 2)
    return child.render(
        frame,
        box.resize(
            left=-empty_space_x[0],
            right=-empty_space_x[1]
        )
    )
#
#
def bg_char(char: str) -> WrapperNode:
    """Fill background with char"""
    def _bg_char(child: Layout):
        return Layout(
            func=bg_char,
            min_size=child.min_size,
            render=partial(_bg_char_render, char, child)
        )

    return _bg_char
def _bg_char_render(char: str, child: Layout, frame: Frame, box: Box):
    frame.draw_box(char, box)
    child.render(frame, box)

bg_fill = bg_char(" ")
"""Fill background with whitespace.

Usefull if you want to fill background with a color using :obj:`bg` or :obj:`styled`"""




#
# sizing manipulations
#

def _shrink_custom(x: bool, y: bool):
    def _curried_shrink_custom(child: Layout):
        return Layout(
            func=_shrink_custom,
            min_size=child.min_size,
            render=partial(_shrink_render, x, y, child),
        )
    return _curried_shrink_custom

def _shrink_render(x: bool, y: bool, child: Layout, frame: Frame, box: Box):
    min_size = child.min_size(frame.measure_text, box.rect)
    child_box = Box(
        min(min_size.width, box.width)if x else box.width,
        min(min_size.height, box.height) if y else box.height,
        box.position
    )
    return child.render(frame, child_box)

shrink = _shrink_custom(True, True)
"""Shrink child layout to its minimum size"""

vshrink = _shrink_custom(False, True)
"""Shrink child layout to its minimum size along the y axis"""

hshrink = _shrink_custom(True, False)
"""Shrink child layout to its minimum size along the x axis"""

def padding(
    left: int = 0,
    top: int = 0,

    right: int = 0,
    bottom: int = 0,
) -> WrapperNode:
    """Add padding / Shrink a layout by differences"""
    def _custom_padding(child: Layout):
        return Layout(
            func=padding,
            min_size=min_size_expand(child.min_size, left+right, top+bottom),
            render=partial(_custom_padding_render, top, bottom, left, right ,child),
        )
    return _custom_padding

def _custom_padding_render(top, bottom, left, right, child, frame: Frame, box: Box):
    return child.render(frame, box.resize(-top, -bottom, -left, -right))

hpadding = padding(left=1, right=1)
"""Add padding to left and right of a child layout.

Eqivelent to :obj:`custom_padding```(left=1, right=1)``."""


offset = padding

def constrain(
    hmin: int = 0, 
    vmin: int = 0, 
    hmax: int = 9999,
    vmax: int = 9999,
):
    def _constrain(child: Layout):
        min_rect = Rect(hmin, vmin)
        max_rect = Rect(hmax, vmax)
        return Layout(
            func=constrain,
            min_size=lambda mtf, r: child.min_size(
                mtf,
                r.clamp(Rect(hmax, hmin)),
            ).union(min_rect).clamp(max_rect),
            render=partial(_constrain_render,hmax, vmax, child)
        )
    return _constrain

def _constrain_render(hmax: int, vmax: int, child: Layout, frame: Frame, box: Box):
    return child.render(frame, box.using_rect(box.rect.clamp(Rect(hmax, vmax))))

#
# V_PROGRESS = " ▁▂▃▄▅▆▇█"
#

# # ╵╷│
#
def hguage(progress: int):
    return Layout(
        func=hguage,
        min_size=min_size_constant(Rect(1, 1)),
        render=partial(_hguage_render, "#", progress),
    )

def _hguage_render(progress_str: str, progress: int, frame: Frame, box: Box):
    start_at_pixel = box.width * progress
    start_at_pixel_int = math.floor(start_at_pixel)
    start_at_progress = start_at_pixel - start_at_pixel_int
    frame.draw_box(progress_str[0], Box(start_at_pixel_int, 1 ,box.position))
    frame.draw_pixel(progress_str[(len(progress_str)-1) * start_at_progress], box.position + Coordinate(start_at_pixel_int, 0))


def debug_overlay(**values):
    def _debug_overlay(child):
        return static_box([
            child,
            vbox([
                hbox([
                    text(f"{k}: ") | fg(Color4.RED),
                    text(str(v)) | fg(Color4.GREEN)
                ]) for (k, v) in values.items()
            ]) | shrink,
        ])
    return _debug_overlay

def hoverable(node_id: NodeID):
    """A wrapper node that marks its child layout as interactive."""
    def _out(child: Layout):
        return Layout(
            func=hoverable,
            min_size=child.min_size,
            render=partial(_render_hoverable, node_id, child)
        )
    return _out


def _render_hoverable(
    node_id: NodeID,
    child: Layout,
    frame: Frame,
    box: Box
):
    frame.set_box_data(node_id, view_box=frame.view_box, box=box)
    child.render(frame, box)

def floating(parent: Layout, child: Layout):
    return Layout(
        func=floating,
        min_size=parent.min_size,
        render=partial(_floating_render, parent, child)
    )

def _floating_render(parent: Layout, child: Layout, frame: Frame, box: Box):

    child_box = Box.from_rect(frame.screen_rect, Coordinate(0, 0))
    child_frame = frame.with_view_box(child_box)

    parent.render(frame, box)

    child_box = child_box.resize(
        top=-(box.position.y+box.height),
        left=-(box.position.x)
    )
    frame.render_later(child, child_frame, child_box)

