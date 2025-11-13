from functools import reduce, partial, lru_cache
from enum import Enum, auto
from typing import NamedTuple
import re
import math

from .classes import *

# __all__ = [
#     "combine",
#     "nothing",
#     "empty",
#     "LOREM",
#
#     "text",
#     "Justify",
#     "adaptive_text",
#     "vbar",
#     "hbar",
#
#     "border",
#     "add_style",
#     "no_style",
#     "fg",
#     "bg",
#     "bold",
#     "italic",
#     "underlined",
# ]

def _clamp(n, smallest, largest): return max(smallest, min(n, largest))

def _even_divide(num, denomenator) -> list[int]:
    return [num // denomenator + (1 if x < num % denomenator else 0)  for x in range (denomenator)]

LRU_MAX_SIZE = 128
#
# Element Utils
#

def combine(*node_constructors: ElementConstructor) -> ElementConstructor:
    @applicable
    def out(child: Node):
        rnode_constructors = reversed(node_constructors)
        return reduce(lambda a, b: b(a), rnode_constructors, child)
    return out

def nothing():
    return Node(
        func=nothing,
        min_size=min_size_constant(Rect(0, 0)),
        render=partial(lambda f, b: Result()),
    )

@applicable
def empty(node: Node):
    return node

#
# Text Elements
#

LOREM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

def text(string: str):
    split_string = tuple(string.split('\n'))
    return Node(
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
        res.draw_string_line(frame, line, box.offset + Coordinate(0, y))
    return res


def vbar(char: str = "|"):
    """Vertical Bar"""
    return Node(
        func=vbar,
        min_size=min_size_constant(Rect(1, 1)),
        render=partial(_vbar_render, char)
    )
@lru_cache(LRU_MAX_SIZE)
def _vbar_render(char: str, frame: Frame, box: Box):
    res = Result()
    res.draw_box(frame, char, Box(1, box.height, box.offset))
    return res

def hbar(char: str = "-"):
    return Node(
        func=hbar,
        min_size=min_size_constant(Rect(1, 1)),
        render=partial(_hbar_render, char)
    )
@lru_cache(LRU_MAX_SIZE)
def _hbar_render(char: str, frame: Frame, box: Box):
    res = Result()
    res.draw_box(frame, char, Box(box.width, 1, box.offset))
    return res
#
# Border Elements
#

@dataclass(frozen=True)
class BorderStyle:
    line_v: str
    line_h: str
    corner_tl: str
    corner_tr: str
    corner_br: str
    corner_bl: str

BORDER_ROUNDED = BorderStyle(
    line_v="│",
    line_h="─",
    corner_tl="╭",
    corner_tr="╮",
    corner_bl="╰",
    corner_br="╯",
)

@applicable
def border(child: Node):
    return Node(
        func=border,
        min_size=min_size_expand(child.min_size, 2, 2),
        render=partial(_border_render, child),
    )

@lru_cache(LRU_MAX_SIZE)
def _border_render(child: Node, frame: Frame, box: Box):
    style = BORDER_ROUNDED
    res = Result()
    res.draw_box(frame, fill=style.line_v, box=Box(1, box.height, box.offset))
    res.draw_box(frame, fill=style.line_h, box=Box(box.width, 1, box.offset))
    res.draw_box(frame, fill=style.line_v, box=Box(1, box.height, box.offset + Coordinate(box.width-1, 0)))
    res.draw_box(frame, fill=style.line_h, box=Box(box.width, 1, box.offset + Coordinate(0, box.height-1)))
    res.draw_pixel(frame, fill=style.corner_tl, at=box.offset + Coordinate(0, 0))
    res.draw_pixel(frame, fill=style.corner_tr, at=box.offset + Coordinate(box.width-1, 0))
    res.draw_pixel(frame, fill=style.corner_br, at=box.offset + Coordinate(box.width-1, box.height-1))
    res.draw_pixel(frame, fill=style.corner_bl, at=box.offset + Coordinate(0, box.height-1))
    res.add_children_after([child.render(frame, box.shrink(1, 1, 1, 1))])
    return res


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


def add_style(style: Style, child: Node):
    return Node(
        func=add_style,
        min_size=child.min_size,
        render=partial(_add_style_render, child, style)
    )
def _add_style_render(child: Node, style: Style, frame: Frame, box: Box):
    return child.render(
        frame.with_style(frame.default_style.combine(style)),
        box
    )
def force_style(style: Style, child: Node):
    return Node(
        func=force_style,
        min_size=child.min_size,
        render=partial(_force_style_render, child, style)
    )
def _force_style_render(child: Node, style: Style, frame: Frame, box: Box):
    return child.render(
        frame.with_style(style),
        box
    )

@applicable
def bold(node: Node): return add_style(Style(char_style=CharStyle.BOLD), node)
@applicable
def reverse(node: Node): return add_style(Style(char_style=CharStyle.REVERSED), node)
@applicable
def underlined(node: Node): return add_style(Style(char_style=CharStyle.UNDERLINED), node)
@applicable
def italic(node: Node): return add_style(Style(char_style=CharStyle.ITALIC), node)
@applicable
def strike_through(node: Node): return add_style(Style(char_style=CharStyle.STRIKE_THROUGH), node)

# def _fg_render(color: Any, child: Node, frame: Frame, box: Box) -> Result:
#         return child.render(
#             frame.with_style(Style(
#                 fg_color=color,
#                 bg_color=frame.default_pixel.bg_color,
#                 style=frame.default_pixel.style
#             )),
#             box
#         )
def fg(color: Any):
    return applicable(partial(add_style, Style(fg=color)))
def bg(color: Any):
    return applicable(partial(add_style, Style(bg=color)))

def styled(element: ElementConstructor, style: Style):
    @applicable
    def out(child: Node):
        composed_child = element(child)
        return Node(
            func=styled,
            min_size=composed_child.min_size,
            render=partial(_styled_render, child, element, style)
        )
    return out

def _styled_render(child: Node, element: ElementConstructor, style: Style, frame, box):
    return add_style(style, element(
            force_style(frame.default_style, child)
        )
    ).render(frame, box)
#
# Containers
#

def static_box(children: Iterable[Node]):
    children = tuple(children)
    return Node(
        func=static_box,
        min_size=min_size_union([i.min_size for i in children]),
        render=partial(_static_box_render, children),
    )
def _static_box_render(children: tuple[Node, ...], frame: Frame, box: Box):
    res = Result()
    for child in children:
        res.add_children_after([child.render(frame, box)])
    return res

def vbox(children: Iterable[Node], at_y: int=0):
    children = tuple(children)
    return Node(
        func=vbox,
        min_size=min_size_vertical([i.min_size for i in children]),
        render=partial(_vbox_render, children, at_y)
    )

@lru_cache(LRU_MAX_SIZE)
def _vbox_render(children: Iterable[Node], at_y: int, frame: Frame, box: Box):
    res=Result()
    for node in children:
        child_min_size = node.min_size(frame.measure_text, box.rect)
        child_box = Box(box.width, child_min_size.height).offset_by(box.offset + Coordinate(0, at_y))
        res.add_children_after([
                node.render(frame.shrink_to(child_box.intersect(box)), child_box)
        ])
        at_y += child_box.height
    return res

def hbox(children: Iterable[Node], at_x: int=0):
    children = tuple(children)
    return Node(
        func=hbox,
        min_size=min_size_horizontal([i.min_size for i in children]),
        render=partial(_hbox_render, children, at_x)
    )
@lru_cache(LRU_MAX_SIZE)
def _hbox_render(children: Iterable[Node], at_x: int, frame: Frame, box: Box):
    res=Result()
    for node in children:
        child_min_size = node.min_size(frame.measure_text, box.rect)
        child_box = Box(child_min_size.width, box.height).offset_by(box.offset + Coordinate(at_x, 0))
        res.add_children_after([
            node.render(frame.shrink_to(child_box.intersect(box)), child_box)
        ])
        at_x += child_box.width
    return res

@applicable
def center(child: Node):
    return Node(
        func=center,
        min_size=child.min_size,
        render=partial(_center_render, child)
    )

def _center_render(child: Node, frame: Frame, box: Box):
    min_size = child.min_size(frame.measure_text, box.rect)
    empty_space_x = _even_divide(box.width - min_size.width, 2)
    empty_space_y = _even_divide(box.height - min_size.height, 2)
    return child.render(
        frame,
        box.shrink(
            top=empty_space_y[0],
            bottom=empty_space_y[1],
            left=empty_space_x[0],
            right=empty_space_x[1]
        )
    )
#
#
def bg_fill_char(char: str):
    @applicable
    def out(child: Node):
        return Node(
            func=bg_fill_char,
            min_size=child.min_size,
            render=partial(_bg_fill_char_render, char, child)
        )

    return out
def _bg_fill_char_render(char: str, child: Node, frame: Frame, box: Box):
    res = Result()
    res.draw_box(frame, char, box)
    res.add_children_after([child.render(frame, box)])
    return res

bg_fill = bg_fill_char(" ")
#
#
def border_with_title(title: Node, border_node=border):
    @applicable
    def out(child: Node):
        return static_box([
            border_node(child),
            shrink_y(shrink_by(0, 0, 1, 1)(title)),
        ])
    return out

#
#
# def _padding(top: int, bottom: int, left: int, right: int, node: Node):
#     def render(frame: Frame, box: Box):
#         node.render(frame, box.shrink(top, bottom, left, right))
#     return Node(min_size_expand(node.min_size, left+right, top+bottom), render)
#
# def custom_padding(top=0, bottom=0, left=0, right=0):
#     @applicable
#     def out(node: Node):
#         return _padding(top, bottom, left, right, node)
#     return out
# padding = custom_padding(1, 1, 1, 1)
#
#

@dataclass(frozen=True, eq=True)
class Flex:
    node: Node
    grow: int
    shrink: int
    basis: bool

def flex_custom(grow=1, shrink=1, basis=False):
    @applicable
    def out(node: Node):
        return Flex(node, grow, shrink, basis)
    return out

@applicable
def flex(node: Node):
    return flex_custom(1, 1, False)(node)

@applicable
def no_flex(node: Node):
    return flex_custom(0, 0, True)(node)


def vbox_flex(children: Iterable[Flex]):
    children = tuple(children)
    return Node(
        func=vbox_flex,
        min_size=min_size_vertical([i.node.min_size for i in children]),
        render=partial(_vbox_flex_render, children)
    )


@lru_cache(LRU_MAX_SIZE)
def _vbox_flex_render(children: tuple[Flex, ...], frame: Frame, box: Box):
    reserved_space = sum(i.node.min_size(frame.measure_text, box.rect).height for i in children if i.basis)
    total_grow = sum(i.grow for i in children)
    total_shrink = sum(i.shrink for i in children)

    available_space = box.height - reserved_space
    space_rations = _even_divide(available_space, total_grow if available_space >= 0 else total_shrink)
    at_y = 0
    res = Result()
    for flex in children:
        child_min_height = flex.node.min_size(frame.measure_text, box.rect).height if flex.basis else 0
        child_box = Box(
            width=box.width,
            height=child_min_height + sum(space_rations.pop() for _ in range(flex.grow if available_space >= 0 else flex.shrink))
        )
        child_box = child_box.offset_by(box.offset + Coordinate(0, at_y))
        res.add_children_after([flex.node.render(frame.shrink_to(child_box), child_box)])
        at_y += child_box.height
    return res

def hbox_flex(children: Iterable[Flex]):
    children = tuple(children)
    return Node(
        func=hbox_flex,
        min_size=min_size_horizontal([i.node.min_size for i in children]),
        render=partial(_hbox_flex_render, children)
    )
@lru_cache(LRU_MAX_SIZE)
def _hbox_flex_render(children: Iterable[Flex], frame: Frame, box: Box):
    reserved_space = sum(i.node.min_size(frame.measure_text, box.rect).width for i in children if i.basis)
    total_grow = sum(i.grow for i in children)
    total_shrink = sum(i.shrink for i in children)

    available_space = box.width - reserved_space
    space_rations = _even_divide(available_space, total_grow if available_space >= 0 else total_shrink)
    at_x = 0
    res = Result()
    for flex in children:
        child_min_width = flex.node.min_size(frame.measure_text, box.rect).width if flex.basis else 0
        child_box = Box(
            width=child_min_width + sum(space_rations.pop() for _ in range(flex.grow if available_space >= 0 else flex.shrink)),
            height=box.height,
        )
        child_box = child_box.offset_by(box.offset + Coordinate(at_x, 0))
        res.add_children_after([flex.node.render(frame.shrink_to(child_box), child_box)])
        at_x += child_box.width
    return res

#
# sizing manipulations
#

def _shrink_custom(x: bool, y: bool):
    @applicable
    def out(child: Node):
        return Node(
            func=_shrink_custom,
            min_size=child.min_size,
            render=partial(_shrink_render, x, y, child),
        )
    return out

def _shrink_render(x: bool, y: bool, child: Node, frame: Frame, box: Box):
    min_size = child.min_size(frame.measure_text, box.rect)
    child_box = Box(
        min_size.width if x else box.width,
        min_size.height if y else box.height,
        box.offset
    )
    return child.render(frame, child_box)

shrink = _shrink_custom(True, True)
shrink_y = _shrink_custom(False, True)
shrink_x = _shrink_custom(True, False)

def shrink_by(
    top: int = 0,
    bottom: int = 0,
    left: int = 0,
    right: int = 0,
):
    @applicable
    def out(child: Node):
        return Node(
            func=shrink_by,
            min_size=min_size_expand(child.min_size, left+right, top+bottom),
            render=partial(_shrink_by_render, top, bottom, left, right ,child),
        )
    return out
def _shrink_by_render(top, bottom, left, right, child, frame: Frame, box: Box):
    return child.render(frame, box.shrink(top, bottom, left, right))


def offset(x: int=0, y: int=0):
    coord = Coordinate(x, y)
    @applicable
    def out(child: Node):
        return Node(
            func=offset,
            min_size=min_size_expand(child.min_size, coord.x, coord.y),
            render=partial(_offset_render, coord, child),
        )
    return out
@lru_cache(LRU_MAX_SIZE)
def _offset_render(by: Coordinate, node: Node, frame: Frame, box: Box):
    return node.render(frame, box.offset_by(by))

def limit_width(width: int):
    @applicable
    def out(child: Node):
        return Node(
            func=limit_width,
            min_size=lambda mtf, r: child.min_size(mtf, r.limit_width(width)).limit_width(width),
            # here we have to sadly wrap in a partial
            render=partial(lambda frame, box: child.render(frame, box.using_rect(box.rect.limit_width(width))))
        )
    return out

def limit_height(height: int):
    @applicable
    def out(child: Node):
        return Node(
            func=limit_height,
            min_size=lambda mtf, r: child.min_size(mtf, r.limit_height(height)).limit_height(height),
            render=partial(lambda frame, box: child.render(frame, box.using_rect(box.rect.limit_height(height))))
        )
    return out




#
# V_PROGRESS = " ▁▂▃▄▅▆▇█"
#

# # ╵╷│
#
def h_guage(progress: int):
    return Node(
        func=h_guage,
        min_size=min_size_constant(Rect(1, 1)),
        render=partial(_h_guage_render, "#", progress),
    )

def _h_guage_render(progress_str: str, progress: int, frame: Frame, box: Box) -> Result:
    start_at_pixel = box.width * progress
    start_at_pixel_int = math.floor(start_at_pixel)
    start_at_progress = start_at_pixel - start_at_pixel_int
    res = Result()
    res.draw_box(frame, progress_str[0], Box(start_at_pixel_int, 1 ,box.offset))
    res.draw_pixel(frame, progress_str[(len(progress_str)-1) * start_at_progress], box.offset + Coordinate(start_at_pixel_int, 0))
    return res



def v_scroll_bar(start: float, showing: float):
    return Node(
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
            res.draw_pixel(frame, start_char, box.offset + Coordinate(0, i))
        elif i == end_at_pixel_int:
            res.draw_pixel(frame, end_char, box.offset + Coordinate(0, i))
        elif start_at_pixel_int < i < end_at_pixel_int:
            res.draw_pixel(frame, "│", box.offset + Coordinate(0, i))
    return res
