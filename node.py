from dataclasses import dataclass
from typing import Self, Any
from classes import Frame, Box, Node, Screen, Coordinate, applicable, Pixel, CharStyle, Rect, min_size_expand, min_size_vertical, min_size_horizontal
from math import floor, ceil
from enum import Enum, auto
from functools import reduce

import os

__all__ = [
    "Justify",
    "render",
    "render_to_fit_terminal",

    # debug decorators
    "print_debug",

    # style decorators
    "Color",
    "add_style",
    "bold",
    "italic",
    "underlined",
    "reverse",
    "no_style",
    "foreground",
    "background",
    "strike_through",

    # misc decorators
    "border",
    "fill",
    "fill_custom",
    "empty",

    # sizing decorators
    "flex",
    "no_flex",
    "min_size",
    "shrink",
    "offset",
    "custom_padding",
    "padding",
    "center",

    # data
    "hbar",
    "vbar",
    "text",
    "adaptive_text",
    "v_scroll_bar",

    # containers
    "vbox",
    "hbox",
    "vbox_flex",
    "hbox_flex",
    "static_box",
]

LOREM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

@dataclass(frozen=True)
class BorderStyle:
    line_v: str
    line_h: str
    corner_tl: str
    corner_tr: str
    corner_br: str
    corner_bl: str

# BORDER_SHARP = BorderStyle(
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
    if CharStyle.STRIKE_THROUGH in style:
        out.append("\033[9m")
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
    min_size = lambda _: Rect(
        width=max([len(i) for i in split_string]),
        height=len(split_string)
    )
    def render(frame: Frame, box: Box):
        frame.draw_string(string, box.offset)
    return Node(min_size, render)

class Justify(Enum):
    LEFT = auto()
    CENTER = auto()
    RIGHT = auto()

class Expand(Enum):
    VERTICAL = auto()
    HORIZONTAL = auto()

def _line_len(line: list[str]) -> int:
    return sum(len(i) for i in line) + len(line) - 1

def _split_by_lines(max_width: int, words: list[str]) -> list[str]:
    lines: list[list[str]] = []
    curr_line: list[str] = []
    for word in words:
        if _line_len(curr_line) + 1 + len(word)<= max_width: # +1 because space between existing line and new word
            curr_line.append(word)
        else:
            lines.append(curr_line)
            curr_line = [word]
    if curr_line != "":
        lines.append(curr_line)
    return [" ".join(i) for i in lines]

def adaptive_text(string: str=LOREM, justify=Justify.LEFT, overflow=Expand.VERTICAL):
    # min_size = Box(width=len(string), height=1)
    words = string.split()
    def render(frame: Frame, box: Box):
        lines = _split_by_lines(box.width, words)
        print(lines)
        match justify:
            case Justify.LEFT:
                for index, line in enumerate(lines):
                    frame.draw_string(line, box.offset + Coordinate(0, index))
            case Justify.CENTER:
                for index, line in enumerate(lines):
                    available_space = box.width - len(line)
                    frame.draw_string(line, box.offset + Coordinate(available_space // 2, index))
            case Justify.RIGHT:
                for index, line in enumerate(lines):
                    available_space = box.width - len(line)
                    frame.draw_string(line, box.offset + Coordinate(available_space, index))
    def min_size(available: Rect):
        lines = _split_by_lines(available.width, words)
        return Rect(
            max(len(i) for i in lines),
            len(lines)
        )
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
@applicable
def strike_through(node: Node):
    return add_style(CharStyle.STRIKE_THROUGH, node)

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
    style = BORDER_ROUNDED
    def render(frame: Frame, box: Box):
        frame.draw_box(fill=style.line_v, width=1, height=box.height, start=box.offset )
        frame.draw_box(fill=style.line_h, width=box.width, height=1, start=box.offset )
        frame.draw_box(fill=style.line_v, width=1, height=box.height, start=box.offset + Coordinate(box.width-1, 0))
        frame.draw_box(fill=style.line_h, width=box.width, height=1, start=box.offset + Coordinate(0, box.height-1))
        frame.draw_pixel(fill=style.corner_tl, at=box.offset + Coordinate(0, 0))
        frame.draw_pixel(fill=style.corner_tr, at=box.offset + Coordinate(box.width-1, 0))
        frame.draw_pixel(fill=style.corner_br, at=box.offset + Coordinate(box.width-1, box.height-1))
        frame.draw_pixel(fill=style.corner_bl, at=box.offset + Coordinate(0, box.height-1))
        node.render(frame, box.shrink(1, 1, 1, 1))
    return Node(min_size_expand(node.min_size, 2, 2), render)

def vbox(nodes: list[Node]):
    def render(frame: Frame, box: Box):
        at_y = 0
        for node in nodes:
            child_min_size = node.min_size(box.rect)
            child_box = Box(box.width, child_min_size.height).offset_by(box.offset + Coordinate(0, at_y))
            node.render(frame.shrink_to(child_box.intersect(box)), child_box)
            at_y += child_box.height
    return Node(min_size_vertical([i.min_size for i in nodes]), render)

def hbox(nodes: list[Node]):
    def render(frame: Frame, box: Box):
        at_x = 0
        for node in nodes:
            child_min_size = node.min_size(box.rect)
            print(at_x, child_min_size)
            child_box = Box(child_min_size.width, box.height).offset_by(box.offset + Coordinate(at_x, 0))
            node.render(frame.shrink_to(child_box.intersect(box)), child_box)
            at_x += child_box.width
    return Node(min_size_horizontal([i.min_size for i in nodes]), render)

@applicable
def center(node: Node):
    def render(frame: Frame, box: Box):
        empty_space_x = even_divide(box.width - node.min_size.width, 2)
        empty_space_y = even_divide(box.height - node.min_size.height, 2)
        node.render(
            frame,
            box.shrink(
                top=empty_space_y[0],
                bottom=empty_space_y[1],
                left=empty_space_x[0],
                right=empty_space_x[1]
            )
        )

    return Node(node.min_size, render)

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

def _offset(x: int, y: int, node: Node):
    min_size = Box(
        width=node.min_size.width + x,
        height=node.min_size.height + y,
        offset=node.min_size.offset
    )
    def render(frame: Frame, box: Box):
        node.render(frame, box.offset_by(Coordinate(x, y)))
    return Node(min_size, render)

def offset(x: int=0, y: int=0):
    @applicable
    def out(node: Node):
        return _offset(x, y, node)
    return out


@applicable
def fill(node: Node):
    return _fill_custom(" ", node)

def _padding(top: int, bottom: int, left: int, right: int, node: Node):
    min_size = Box(
        node.min_size.width + left + right,
        node.min_size.height + top + bottom,
    )
    def render(frame: Frame, box: Box):
        node.render(frame, box.shrink(top, bottom, left, right))
    return Node(min_size, render)

def custom_padding(top=0, bottom=0, left=0, right=0):
    @applicable
    def out(node: Node):
        return _padding(top, bottom, left, right, node)
    return out

def padding(value: int):
    return custom_padding(value, value, value, value)


@applicable
def shrink(node: Node):
    def render(frame: Frame, box: Box):
        child_box = Box(
            node.min_size.width,
            node.min_size.height,
            box.offset
        )
        node.render(frame, child_box)
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
    def render(frame: Frame, box: Box):
        reserved_space = sum(i.node.min_size(box.rect).height for i in nodes)
        total_grow = sum(i.grow for i in nodes)
        total_shrink = sum(i.shrink for i in nodes)

        available_space = box.height - reserved_space
        space_rations = even_divide(available_space, total_grow if available_space >= 0 else total_shrink)
        at_y = 0
        for flex in nodes:
            child_min_size = flex.node.min_size(box.rect)
            child_box = Box(
                width=box.width,
                height=child_min_size.height + sum(space_rations.pop() for _ in range(flex.grow if available_space >= 0 else flex.shrink))
            )
            child_box = child_box.offset_by(box.offset + Coordinate(0, at_y))
            flex.node.render(frame.shrink_to(child_box), child_box)
            at_y += child_box.height
    return Node(min_size_vertical([i.node.min_size for i in nodes]), render)

def hbox_flex(nodes: list[Flex]):
    def render(frame: Frame, box: Box):
        reserved_space = sum(i.node.min_size(box.rect).width for i in nodes)
        total_grow = sum(i.grow for i in nodes)
        total_shrink = sum(i.shrink for i in nodes)

        available_space = box.width - reserved_space
        space_rations = even_divide(available_space, total_grow if available_space >= 0 else total_shrink)
        at_x = 0
        for flex in nodes:
            child_min_size = flex.node.min_size(box.rect)
            child_box = Box(
                width=child_min_size.width + sum(space_rations.pop() for _ in range(flex.grow if available_space >= 0 else flex.shrink)),
                height=box.height,
            )
            child_box = child_box.offset_by(box.offset + Coordinate(at_x, 0))
            flex.node.render(frame.shrink_to(child_box), child_box)
            at_x += child_box.width
    return Node(min_size_horizontal([i.node.min_size for i in nodes]), render)


def vbar(char: str = "|"):
    min_size = Box(1, 0)
    def render(frame: Frame, box: Box):
        frame.draw_box(char, 1, box.height, box.offset)
    return Node(min_size, render)

def hbar(char: str = "-"):
    min_size = Box(0, 1)
    def render(frame: Frame, box: Box):
        frame.draw_box(char, box.width, 1, box.offset)
    return Node(min_size, render)

V_PROGRESS = " ▁▂▃▄▅▆▇█"

def static_box(nodes: list[Node]):
    min_size = Box(
        max(i.min_size.width for i in nodes),
        max(i.min_size.height for i in nodes)
    ) if nodes else Box(0, 0)

    def render(frame: Frame, box: Box):
        for node in nodes:
            node.render(frame, box)
    return Node(min_size, render)
# ╵╷│
def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def v_scroll_bar(start: float, showing: float):
    def render(frame: Frame, box: Box):
        start_at_pixel = box.height * start
        start_at_pixel_int = floor(start_at_pixel)
        start_at_progress = abs(start_at_pixel - start_at_pixel_int -1)

        end_at_pixel = box.height * start + box.height * showing # should be clampt
        end_at_pixel_int = floor(end_at_pixel)
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
        
        for i in range(box.height):
            if i == start_at_pixel_int:
                frame.draw_pixel(start_char, box.offset + Coordinate(0, i))
            elif i == end_at_pixel_int:
                frame.draw_pixel(end_char, box.offset + Coordinate(0, i))
            elif start_at_pixel_int < i < end_at_pixel_int:
                frame.draw_pixel("│", box.offset + Coordinate(0, i))
    return Node(lambda _: Rect(1, 1), render)



# def v_scroll_bar(start: float, end: float, progress_gradient=V_PROGRESS):
#     min_size = Box(1, 0)
#     def render(frame: Frame, box: Box):
#         start_at = box.height * start
#         start_at_int = floor(start_at)
#         start_at_progress = abs(start_at - start_at_int - 1)

#         end_at = box.height * end
#         end_at_int = floor(end_at)
#         end_at_progress = end_at - end_at_int
#         # print("start: ", start_at, "end: ", end_at)
#         # print("starti: ", start_at_int, "endi: ", end_at_int)
#         # print("startp: ", start_at_progress, "endp: ", end_at_progress)
#         for i in range(box.height):
#             render_frame = frame
#             if i == start_at_int:
#                 pixel = progress_gradient[int(start_at_progress * (len(progress_gradient)-1))]
#             elif i == end_at_int:
#                 pixel = progress_gradient[int(end_at_progress * (len(progress_gradient)-1))]
#                 render_frame = frame.with_pixel(frame.default_pixel.add_styles(CharStyle.REVERSED))
#             elif start_at_int < i < end_at_int:
#                 pixel = progress_gradient[-1]
#             else:
#                 pixel = progress_gradient[0]

#             render_frame.draw_pixel(pixel, Coordinate(0, i) + box.offset)

#     return Node(min_size, render)
