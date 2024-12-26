from dataclasses import dataclass
from typing import Self, Any
from classes import Frame, Box, Node, Screen, Coordinate, applicable, Pixel, CharStyle
from math import floor, ceil
from enum import Enum, auto

import os

__all__ = [
    "render",

    # debug decorators
    "print_debug",

    # style decorators
    "border",
    "add_style",
    "bold",
    "italic",
    "underlined",
    "reverse",
    "shrink",
    "no_style",
    "foreground",
    "background",
    "fill",
    "fill_custom",

    # sizing decorators
    "flex",
    "no_flex",
    "min_size",

    # data
    "hbar",
    "vbar",
    "text",

    # containers
    "vbox",
    "hbox",
    "vbox_flex",
    "hbox_flex",
]

@dataclass(frozen=True)
class BorderStyle:
    line_v: str
    line_h: str
    corner_tl: str
    corner_tr: str
    corner_br: str
    corner_bl: str

# BORDER_ROUNDED = BorderStyle(
#     line_v="│",
#     line_h="─",
#     corner_tl="┌",
#     corner_tr="┐",
#     corner_bl="└",
#     corner_br="┘",
# )
BORDER_ROUNDED = BorderStyle(
    line_v="│",
    line_h="─",
    corner_tl="╭",
    corner_tr="╮",
    corner_bl="╰",
    corner_br="╯",
)


# type Node = Callable[[Frame], Result]
def render_to_fit_terminal(root_node: Node) -> str:
    terminal_size = os.get_terminal_size()
    width = terminal_size.columns
    height = terminal_size.lines - 1
    return render(width, height, root_node)

class Color(Enum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37

# class BrightColor(Enum):
#     BLACK = auto()
#     RED = auto()
#     GREEN = auto()
#     YELLOW = auto()
#     BLUE = auto()
#     MAGENTA = auto()
#     CYAN = auto()
#     WHITE = auto()



def default_color_to_fg_ansi(color: Color):
    return f"\033[{color.value}m"

def default_color_to_bg_ansi(color: Color):
    return f"\033[{color.value + 10}m"

def style_to_ansi(style: CharStyle):
    out = []
    if CharStyle.BOLD in style:
        out.append("\033[1m")
    if CharStyle.ITALIC in style:
        out.append("\033[3m")
    if CharStyle.UNDERLINED in style:
        out.append("\033[4m")
    if CharStyle.REVERSED in style:
        out.append("\033[7m")
    return "".join(out)

def default_color_to_ansi_driver(pixel: Pixel):
    out = []
    if isinstance(pixel.fg_color, Color):
        out.append(default_color_to_fg_ansi(pixel.fg_color)) 
    
    if isinstance(pixel.bg_color, Color):
        out.append(default_color_to_bg_ansi(pixel.bg_color)) 
    
    out.append(style_to_ansi(pixel.style))
    out.append(pixel.char)
    out.append("\033[39m\033[49m\033[0m") # reset fg, bg and styles
    return "".join(out)


def render(width: int, height: int, root_node: Node):
    screen = Screen(width, height)
    root_node.render(Frame(Box(width, height), screen, Pixel()), Box(width, height))
    return "\n".join("".join(default_color_to_ansi_driver(pixel) for pixel in line) for line in screen.split_by_lines())


@applicable
def print_debug(node: Node):
    print("child minsize:", node.min_size)
    def render(frame: Frame, box: Box):
        node.render(frame, box)
    return Node(node.min_size, render)


def text(string: str):
    split_string = string.split('\n')
    min_size = Box(
        width=max([len(i) for i in split_string]),
        height=len(split_string)
    )
    def render(frame: Frame, box: Box):
        frame.draw_string(string, box.offset)
    return Node(min_size, render)

@applicable
def empty(node: Node):
    return node

def add_style(style: CharStyle, node: Node):
    def render(frame: Frame, box: Box):
        node.render(
            frame.with_pixel(frame.default_pixel.add_styles(style)),
            box
        )
    return Node(node.min_size, render)
@applicable
def no_style(node: Node):
    def render(frame: Frame, box: Box):
        node.render(
            frame.with_pixel(Pixel(style=CharStyle(0))),
            box
        )
    return Node(node.min_size, render)
@applicable
def bold(node: Node):
    return add_style(CharStyle.BOLD, node)
@applicable
def reverse(node: Node):
    return add_style(CharStyle.REVERSED, node)
@applicable
def underlined(node: Node):
    return add_style(CharStyle.UNDERLINED, node)
@applicable
def italic(node: Node):
    return add_style(CharStyle.ITALIC, node)

def _foreground(color: Any, node: Node):
    def render(frame: Frame, box: Box):
        node.render(
            frame.with_pixel(Pixel(
                fg_color=color,
                bg_color=frame.default_pixel.bg_color,
                style=frame.default_pixel.style
            )),
            box
        )
    return Node(node.min_size, render)

def _background(color: Any, node: Node):
    def render(frame: Frame, box: Box):
        node.render(
            frame.with_pixel(Pixel(
                fg_color=frame.default_pixel.fg_color,
                bg_color=color,
                style=frame.default_pixel.style
            )),
            box
        )
    return Node(node.min_size, render)

@applicable
def foreground(color: Any):
    @applicable
    def out(node: Node):
        return _foreground(color, node)
    return out

@applicable
def background(color: Any):
    @applicable
    def out(node: Node):
        return _background(color, node)
    return out

@applicable
def border(node: Node):
    min_size = Box(
        node.min_size.width + 2,
        node.min_size.height + 2,
    )
    style = BORDER_ROUNDED
    def render(frame: Frame, box: Box):
        node.render(frame, box.shrink(1, 1, 1, 1))
        frame.draw_box(fill=style.line_v, width=1, height=box.height, start=box.offset )
        frame.draw_box(fill=style.line_h, width=box.width, height=1, start=box.offset )
        frame.draw_box(fill=style.line_v, width=1, height=box.height, start=box.offset + Coordinate(box.width-1, 0))
        frame.draw_box(fill=style.line_h, width=box.width, height=1, start=box.offset + Coordinate(0, box.height-1))
        frame.draw_pixel(fill=style.corner_tl, at=box.offset + Coordinate(0, 0))
        frame.draw_pixel(fill=style.corner_tr, at=box.offset + Coordinate(box.width-1, 0))
        frame.draw_pixel(fill=style.corner_br, at=box.offset + Coordinate(box.width-1, box.height-1))
        frame.draw_pixel(fill=style.corner_bl, at=box.offset + Coordinate(0, box.height-1))
    return Node(min_size, render)

def vbox(nodes: list[Node]):
    min_size = Box(
        max(i.min_size.width for i in nodes),
        sum(i.min_size.height for i in nodes)
    ) if nodes else Box(0, 0)
    def render(frame: Frame, box: Box):
        at_y = 0
        for node in nodes:
            child_box = Box(box.width, node.min_size.height).offset_by(box.offset + Coordinate(0, at_y))
            node.render(frame.shrink_to(child_box), child_box)
            at_y += child_box.height
    return Node(min_size, render)

def hbox(nodes: list[Node]):
    min_size = Box(
        sum(i.min_size.width for i in nodes),
        max(i.min_size.height for i in nodes)
    ) if nodes else Box(0, 0)
    def render(frame: Frame, box: Box):
        at_x = 0
        for node in nodes:
            child_box = Box(node.min_size.width, box.height).offset_by(box.offset + Coordinate(at_x, 0))
            node.render(frame.shrink_to(child_box), child_box)
            at_x += child_box.width
    return Node(min_size, render)

def _fill_custom(char: str, node: Node):
    def render(frame: Frame, box: Box):
        frame.draw_box(char, box.width, box.height, box.offset)
        node.render(frame, box)
    return Node(node.min_size, render)

def fill_custom(char: str):
    @applicable
    def out(node: Node):
        return _fill_custom(char, node)
    return out

@applicable
def fill(node: Node):
    return _fill_custom(" ", node)


@applicable
def shrink(node: Node):
    def render(frame: Frame, box: Box):
        child_box = Box(
            node.min_size.width,
            node.min_size.height,
            box.offset
        )
        node.render(frame.shrink_to(child_box), child_box)
    return Node(node.min_size, render)

def _min_size(width: int, height: int, node: Node):
    def render(frame: Frame, box: Box):
        node.render(frame, box)
    return Node(Box(width, height, node.min_size.offset), render)

def min_size(width: int, height: int):
    @applicable
    def out(node: Node):
        return _min_size(width, height, node)
    return out




@dataclass
class Flex:
    node: Node
    grow: int
    shrink: int

def flex(grow=1, shrink=1):
    @applicable
    def out(node: Node):
        return Flex(node, grow, shrink)
    return out

@applicable
def no_flex(node: Node):
    return flex(0, 0) ** node

def even_divide(num, denomenator) -> list[int]:
    return [num // denomenator + (1 if x < num % denomenator else 0)  for x in range (denomenator)]

def vbox_flex(nodes: list[Flex]):
    min_size = Box(
        max(i.node.min_size.width for i in nodes),
        sum(i.node.min_size.height for i in nodes)
    ) if nodes else Box(0, 0)

    reserved_space = sum(i.node.min_size.height for i in nodes)
    print(reserved_space)
    total_grow = sum(i.grow for i in nodes)
    total_shrink = sum(i.shrink for i in nodes)

    def render(frame: Frame, box: Box):
        available_space = box.height - reserved_space
        space_rations = even_divide(available_space, total_grow if available_space >= 0 else total_shrink)
        at_y = 0
        for flex in nodes:
            child_box = Box(
                width=box.width,
                height=flex.node.min_size.height + sum(space_rations.pop() for _ in range(flex.grow if available_space >= 0 else flex.shrink))
            )
            child_box = child_box.offset_by(box.offset + Coordinate(0, at_y))
            flex.node.render(frame.shrink_to(child_box), child_box)
            at_y += child_box.height
    return Node(min_size, render)

def hbox_flex(nodes: list[Flex]):
    min_size = Box(
        sum(i.node.min_size.width for i in nodes),
        max(i.node.min_size.height for i in nodes)
    ) if nodes else Box(0, 0)

    reserved_space = sum(i.node.min_size.width for i in nodes)
    total_grow = sum(i.grow for i in nodes)
    total_shrink = sum(i.shrink for i in nodes)

    def render(frame: Frame, box: Box):
        available_space = box.width - reserved_space
        space_rations = even_divide(available_space, total_grow if available_space >= 0 else total_shrink)
        at_x = 0
        for flex in nodes:
            child_box = Box(
                width=flex.node.min_size.width + sum(space_rations.pop() for _ in range(flex.grow if available_space >= 0 else flex.shrink)),
                height=box.height,
            )
            child_box = child_box.offset_by(box.offset + Coordinate(at_x, 0))
            flex.node.render(frame.shrink_to(child_box), child_box)
            at_x += child_box.width
    return Node(min_size, render)


def vbar():
    min_size = Box(1, 0)
    def render(frame: Frame, box: Box):
        frame.draw_box("|", 1, box.height, box.offset)
    return Node(min_size, render)

def hbar():
    min_size = Box(0, 1)
    def render(frame: Frame, box: Box):
        frame.draw_box("-", box.width, 1, box.offset)
    return Node(min_size, render)

V_PROGRESS = " ▁▂▃▄▅▆▇█"

def v_scroll_bar(start: float, end: float, progress_gradient: str = V_PROGRESS):
    min_size = Box(1, 0)
    def render(frame: Frame, box: Box):
        start_at = box.height * start
        start_at_int = floor(start_at)
        start_at_progress = abs(start_at - start_at_int - 1)

        end_at = box.height * end
        end_at_int = floor(end_at)
        end_at_progress = end_at - end_at_int
        # print("start: ", start_at, "end: ", end_at)
        # print("starti: ", start_at_int, "endi: ", end_at_int)
        # print("startp: ", start_at_progress, "endp: ", end_at_progress)

        for i in range(box.height):
            if i == start_at_int:
                pixel = progress_gradient[int(start_at_progress * (len(progress_gradient)-1))]
            elif i == end_at_int:
                pixel = progress_gradient[int(end_at_progress * (len(progress_gradient)-1))]
                frame = frame.with_pixel(frame.default_pixel.add_styles(CharStyle.REVERSED))
            elif start_at_int < i < end_at_int:
                pixel = progress_gradient[-1]
            else:
                pixel = progress_gradient[0]

            frame.draw_pixel(pixel, Coordinate(0, i) + box.offset)

    return Node(min_size, render)
