from dataclasses import dataclass, field
from typing import Any, Iterable, Self, Callable
from enum import IntFlag, auto, Enum
from wcwidth import wcswidth
# from abc import ABC, abstractmethod
from functools import reduce, partial, cache
import os

# TODO:
# test caching
# - using partials
# - using classes

# Terminology:
# Node:
# A class that represents a node in the ui tree.
# 
# Element:
# A function that returns a Node
#
# Element constructor:
# A function that returns an Element


#
# Applicable function
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

    def is_empty(self) -> bool:
        return self.width <= 0 or self.height <= 0

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

class CharStyle(IntFlag):
    BOLD = auto()
    REVERSED = auto()
    ITALIC = auto()
    UNDERLINED = auto()
    STRIKE_THROUGH = auto()


#
# Ui specific datastructures
#

@dataclass(frozen=True, eq=True)
class Pixel:
    char: str = " "
    fg_color: Any = None
    bg_color: Any = None
    style: CharStyle = CharStyle(0)
    def with_char(self, char: str) -> Self:
        return self.__class__(
            char,
            self.fg_color,
            self.bg_color,
            self.style
        )
    def add_styles(self, style: CharStyle) -> Self:
        return self.__class__(
            self.char,
            self.fg_color,
            self.bg_color,
            self.style | style
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
    style: Pixel
    string: str
    at: Coordinate

type DrawCommand = DrawPixel | DrawBox | DrawStringLine



@dataclass(frozen=True, eq=True)
class Frame:
    """a view on to the canvas"""
    view_box: Box
    default_pixel: Pixel


    def with_pixel(self, pixel: Pixel):
        return self.__class__(
            view_box=self.view_box,
            default_pixel=pixel,
        )


    def shrink_to(self, other_box):
        return Frame(
            view_box=self.view_box.intersect(other_box),
            default_pixel=self.default_pixel,
        )

class Canvas:
    def __init__(self, width: int, height: int, fill: Pixel=Pixel(" ", None, None)):
        self.width = width
        self.height = height
        self._data: list[Pixel] = [fill for _ in range(width * height)]
        """
        matrix indicies work in this pattern:
        0 1 2 3 4
        5 6 7 8 9
        """

    def get(self, pos: Coordinate) -> Pixel:
        return self._data[pos.x + pos.y * self.width]

    def set(self, pos: Coordinate, data: Pixel) -> None:
        """may error if out of range!!!"""
        self._data[pos.x + pos.y * self.width] = data
    def split_by_lines(self) -> tuple[tuple[Pixel, ...], ...]:
        out: list[tuple[Pixel, ...]] = []
        for h in range(self.height):
            current_row = tuple([self.get(Coordinate(w, h)) for w in range(self.width)])
            out.append(current_row)
        return tuple(out)
    def apply_draw_commands(self, measure_text_func: Callable[[str], int],  draw_commands: Iterable[DrawCommand]):
        for command in draw_commands:
            if isinstance(command, DrawPixel):
                self.set(command.at, command.pixel)

            elif isinstance(command, DrawBox):
                box = command.box
                for x in range(box.offset.x, box.offset.x + box.width):
                    for y in range(box.offset.y, box.offset.y + box.height):
                        self.set(Coordinate(x, y), command.fill)
            else: #DrawStringLine
                delta_x = 0
                for char in command.string:
                    at = Coordinate(command.at.x + delta_x, command.at.y)
                    self.set(at, self.get(at).with_char(char))
                    delta_x += measure_text_func(char)

type MeasureTextFunc = Callable[[str], int]
type MinSize = Callable[[Rect], Rect]
type ElementConstructor = Applicable[Node, Node]

# minsize util functions

def min_size_expand(
    child_size: MinSize,
    width_change: int,
    height_change: int
) -> MinSize:
    def out(from_size: Rect):
        return child_size(from_size.expand(-width_change, -height_change)).expand(width_change, height_change)
    return out

def min_size_vertical(
    children_sizes: list[MinSize],
) -> MinSize:
    def out(from_size):
        return Rect(
            max(i(from_size).width for i in children_sizes),
            sum(i(from_size).height for i in children_sizes),
        ) if children_sizes else Rect(0, 0)
    return out

def min_size_horizontal(
    children_sizes: list[MinSize],
) -> MinSize:
    def out(from_size):
        return Rect(
            sum(i(from_size).width for i in children_sizes),
            max(i(from_size).height for i in children_sizes),
        ) if children_sizes else Rect(0, 0)
    return out
def min_size_union(
    children_sizes: list[MinSize],
) -> MinSize:
    def out(from_size):
        return Rect(
            max(i(from_size).width for i in children_sizes),
            max(i(from_size).height for i in children_sizes),
        ) if children_sizes else Rect(0, 0)
    return out

@dataclass(unsafe_hash=True)
class Result:
    _draw_commands: list[DrawCommand] = field(default_factory=list)
    def add_children_after(self, child_results: list[Self]):
        for child in child_results:
            self._draw_commands.extend(child._draw_commands)

    def add_children_before(self, child_results: list[Self]):
        new_commands = []
        for child in child_results:
            new_commands.extend(child._draw_commands)
        new_commands.extend(self._draw_commands)
        self._draw_commands = new_commands

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
    def draw_string(
        self,
        frame: Frame,
        content: str,
        at: Coordinate = Coordinate(0, 0)
    ):
        for y, line in enumerate(content.split('\n')):
            self._draw_commands.append(DrawStringLine(
                frame.default_pixel,
                line,
                frame.view_box.offset + at + Coordinate(0, y), 
        ))
    def get_commands(self):
        return tuple(self._draw_commands)

def measure_text(text: str) -> int:
    return wcswidth(text)

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


@dataclass()
class Node:
    min_size: MinSize
    render: Callable[[Frame, Box], Result]
    name: str
    hash: tuple
    def __hash__(self) -> int:
        return hash((self.name, self.hash))
    def __eq__(self, value: object, /) -> bool:
        return (self.name, self.hash) == (value.name, value.hash)

# def create_node(
#     *,
#     name: str,
#     hash: tuple,
#     min_size: MinSize,
#     render: Callable[[Frame, Box], Result]
# ) -> Node:
#     return Node(
#         min_size = min_size,
#         render = render,
#         name = name,
#         _h = hash,
#     )
#
# Rendering
#


class Color(Enum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37


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

def default_color_to_ansi_driver(pixel: Pixel) -> str:
    out = []
    if isinstance(pixel.fg_color, Color):
        out.append(default_color_to_fg_ansi(pixel.fg_color)) 

    if isinstance(pixel.bg_color, Color):
        out.append(default_color_to_bg_ansi(pixel.bg_color)) 

    out.append(style_to_ansi(pixel.style))
    out.append(pixel.char)
    out.append("\033[39m\033[49m\033[0m") # reset fg, bg and styles
    return "".join(out)


def render(width: int, height: int, root_node: Node, end = ""):
    canvas = Canvas(width, height)
    measure_text_func = lambda text: wcswidth(text)
    result = root_node.render(
        Frame(
            view_box=Box(width, height),
            default_pixel=Pixel(),
        ),
        Box(width=width, height=height),
    )
    canvas.apply_draw_commands(measure_text_func, result.get_commands())
    return "\n".join("".join(default_color_to_ansi_driver(pixel) for pixel in line) for line in canvas.split_by_lines()) + end

def render_to_fit_terminal(root_node: Node, end='\033[H') -> str:
    terminal_size = os.get_terminal_size()
    width = terminal_size.columns
    height = terminal_size.lines - 1
    return render(width, height, root_node, end=end)

#
# Elements
#
def combine(*node_constructors: ElementConstructor) -> ElementConstructor:
    @applicable
    def out(child: Node):
        rnode_constructors = reversed(node_constructors)
        return reduce(lambda a, b: b(a), rnode_constructors, child)
    return out

# text

LOREM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

def text(string: str):
    split_string = tuple(string.split('\n'))
    return Node(
        name="text",
        hash=split_string,
        min_size = lambda _: Rect(
            width=max([measure_text(i) for i in split_string]),
            height=len(split_string)
        ),
        render = partial(_text_render, split_string)
    )

@cache
def _text_render(text: tuple[str, ...], frame: Frame, box: Box):
    res = Result()
    for line in text:
        res.draw_string(frame, line, box.offset)
    return res

# border

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
        name="border",
        hash=(child,),
        min_size=min_size_expand(child.min_size, 2, 2),
        render=partial(_border_render, child),
    )

@cache
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
    res.add_children_before([child.render(frame, box.shrink(1, 1, 1, 1))])
    return res


# @applicable
# def floating(node: Node):
#     return create_node(
#         name="floating",
#         min_size=lambda _: Rect(0, 0), render)
#
# def _render_floating(frame: Frame, box: Box):
#     nw_box = Box(frame.screen.width, frame.screen.height)
#     node.render(Frame(box, frame.screen, frame.default_pixel), new_box)
#
# class Justify(Enum):
#     LEFT = auto()
#     CENTER = auto()
#     RIGHT = auto()
#
# class Expand(Enum):
#     VERTICAL = auto()
#     HORIZONTAL = auto()
#
# def _line_len(line: list[str]) -> int:
#     return sum(len(i) for i in line) + len(line) - 1
#
# def _split_by_lines(max_width: int, words: list[str]) -> list[str]:
#     lines: list[list[str]] = []
#     curr_line: list[str] = []
#     for word in words:
#         if _line_len(curr_line) + 1 + len(word)<= max_width: # +1 because space between existing line and new word
#             curr_line.append(word)
#         else:
#             lines.append(curr_line)
#             curr_line = [word]
#     if curr_line != "":
#         lines.append(curr_line)
#     return [" ".join(i) for i in lines]
#
# def adaptive_text(string: str, justify=Justify.LEFT, overflow=Expand.VERTICAL):
#     # min_size = Box(width=len(string), height=1)
#     words = string.split()
#     def render(frame: Frame, box: Box):
#         lines = _split_by_lines(box.width, words)
#         match justify:
#             case Justify.LEFT:
#                 for index, line in enumerate(lines):
#                     frame.draw_string(line, box.offset + Coordinate(0, index))
#             case Justify.CENTER:
#                 for index, line in enumerate(lines):
#                     available_space = box.width - len(line)
#                     frame.draw_string(line, box.offset + Coordinate(available_space // 2, index))
#             case Justify.RIGHT:
#                 for index, line in enumerate(lines):
#                     available_space = box.width - len(line)
#                     frame.draw_string(line, box.offset + Coordinate(available_space, index))
#     def min_size(available: Rect):
#         lines = _split_by_lines(available.width, words)
#         return Rect(
#             max(len(i) for i in lines),
#             len(lines)
#         )
#     return Node(min_size, render)
#
#
# nothing = Node(
#     min_size=lambda _: Rect(0, 0),
#     render=lambda f, b: None,
# )
#
# def empty(node: Node):
#     return node
#
#
# def add_style(style: CharStyle, node: Node):
#     def render(frame: Frame, box: Box):
#         node.render(
#             frame.with_pixel(frame.default_pixel.add_styles(style)),
#             box
#         )
#     return Node(node.min_size, render)
# @applicable
# def no_style(node: Node):
#     def render(frame: Frame, box: Box):
#         node.render(
#             frame.with_pixel(Pixel(style=CharStyle(0))),
#             box
#         )
#     return Node(node.min_size, render)
# @applicable
# def bold(node: Node):
#     return add_style(CharStyle.BOLD, node)
# @applicable
# def reverse(node: Node):
#     return add_style(CharStyle.REVERSED, node)
# @applicable
# def underlined(node: Node):
#     return add_style(CharStyle.UNDERLINED, node)
# @applicable
# def italic(node: Node):
#     return add_style(CharStyle.ITALIC, node)
# @applicable
# def strike_through(node: Node):
#     return add_style(CharStyle.STRIKE_THROUGH, node)
#
# def _foreground(color: Any, node: Node):
#     def render(frame: Frame, box: Box):
#         node.render(
#             frame.with_pixel(Pixel(
#                 fg_color=color,
#                 bg_color=frame.default_pixel.bg_color,
#                 style=frame.default_pixel.style
#             )),
#             box
#         )
#     return Node(node.min_size, render)
#
# def _background(color: Any, node: Node):
#     def render(frame: Frame, box: Box):
#         node.render(
#             frame.with_pixel(Pixel(
#                 fg_color=frame.default_pixel.fg_color,
#                 bg_color=color,
#                 style=frame.default_pixel.style
#             )),
#             box
#         )
#     return Node(node.min_size, render)
#
# @applicable
# def foreground(color: Any):
#     @applicable
#     def out(node: Node):
#         return _foreground(color, node)
#     return out
#
# @applicable
# def background(color: Any):
#     @applicable
#     def out(node: Node):
#         return _background(color, node)
#     return out
#
# def vbox(nodes: list[Node], at_y: int=0):
#     def render(frame: Frame, box: Box):
#         nonlocal at_y
#         for node in nodes:
#             child_min_size = node.min_size(box.rect)
#             child_box = Box(box.width, child_min_size.height).offset_by(box.offset + Coordinate(0, at_y))
#             node.render(frame.shrink_to(child_box.intersect(box)), child_box)
#             at_y += child_box.height
#     return Node(min_size_vertical([i.min_size for i in nodes]), render)
#
# def hbox(nodes: list[Node]):
#     def render(frame: Frame, box: Box):
#         at_x = 0
#         for node in nodes:
#             child_min_size = node.min_size(box.rect)
#             child_box = Box(child_min_size.width, box.height).offset_by(box.offset + Coordinate(at_x, 0))
#             node.render(frame.shrink_to(child_box.intersect(box)), child_box)
#             at_x += child_box.width
#     return Node(min_size_horizontal([i.min_size for i in nodes]), render)
#
# @applicable
# def center(node: Node):
#     def render(frame: Frame, box: Box):
#         empty_space_x = even_divide(box.width - node.min_size.width, 2)
#         empty_space_y = even_divide(box.height - node.min_size.height, 2)
#         node.render(
#             frame,
#             box.shrink(
#                 top=empty_space_y[0],
#                 bottom=empty_space_y[1],
#                 left=empty_space_x[0],
#                 right=empty_space_x[1]
#             )
#         )
#
#     return Node(node.min_size, render)
#
# def _fill_custom(char: str, node: Node):
#     def render(frame: Frame, box: Box):
#         frame.draw_box(char, box.width, box.height, box.offset)
#         node.render(frame, box)
#     return Node(node.min_size, render)
#
# def fill_custom(char: str):
#     @applicable
#     def out(node: Node):
#         return _fill_custom(char, node)
#     return out
#
# def _offset(x: int, y: int, node: Node):
#     def render(frame: Frame, box: Box):
#         node.render(frame, box.offset_by(Coordinate(x, y)))
#     return Node(min_size_expand(node.min_size, x, y), render)
#
# def offset(x: int=0, y: int=0):
#     @applicable
#     def out(node: Node):
#         return _offset(x, y, node)
#     return out
#
# def border_with_title(title: Node, border_node=border):
#     @applicable
#     def out(node: Node):
#         return _border_with_title(title, border_node, node)
#     return out
#
# def _border_with_title(title: Node, border_style, node: Node):
#     return static_box([
#         border_style ** node,
#         offset(1, 0) ** title,
#     ])
#
#
# @applicable
# def fill(node: Node):
#     return _fill_custom(" ", node)
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
# @applicable
# def shrink(node: Node):
#     def render(frame: Frame, box: Box):
#         min_size = node.min_size(box.rect)
#         child_box = Box(
#             min_size.width,
#             min_size.height,
#             box.offset
#         )
#         node.render(frame, child_box)
#     return Node(node.min_size, render)
#
# # def _min_size(width: int, height: int, node: Node):
# #     def render(frame: Frame, box: Box):
# #         node.render(frame, box)
# #     return Node(Box(width, height, node.min_size.offset), render)
#
# # def min_size(width: int, height: int):
# #     @applicable
# #     def out(node: Node):
# #         return _min_size(width, height, node)
# #     return out
#
# @dataclass
# class Flex:
#     node: Node
#     grow: int
#     shrink: int
#
# def flex_custom(grow=1, shrink=1):
#     @applicable
#     def out(node: Node):
#         return Flex(node, grow, shrink)
#     return out
#
# @applicable
# def flex(node: Node):
#     return flex_custom(1, 1) ** node
#
# @applicable
# def no_flex(node: Node):
#     return flex_custom(0, 0) ** node
#
# def even_divide(num, denomenator) -> list[int]:
#     return [num // denomenator + (1 if x < num % denomenator else 0)  for x in range (denomenator)]
#
# def vbox_flex(nodes: list[Flex]):
#     def render(frame: Frame, box: Box):
#         reserved_space = sum(i.node.min_size(box.rect).height for i in nodes)
#         total_grow = sum(i.grow for i in nodes)
#         total_shrink = sum(i.shrink for i in nodes)
#
#         available_space = box.height - reserved_space
#         space_rations = even_divide(available_space, total_grow if available_space >= 0 else total_shrink)
#         at_y = 0
#         for flex in nodes:
#             child_min_size = flex.node.min_size(box.rect)
#             child_box = Box(
#                 width=box.width,
#                 height=child_min_size.height + sum(space_rations.pop() for _ in range(flex.grow if available_space >= 0 else flex.shrink))
#             )
#             child_box = child_box.offset_by(box.offset + Coordinate(0, at_y))
#             flex.node.render(frame.shrink_to(child_box), child_box)
#             at_y += child_box.height
#     return Node(min_size_vertical([i.node.min_size for i in nodes]), render)
#
# def hbox_flex(nodes: list[Flex]):
#     def render(frame: Frame, box: Box):
#         reserved_space = sum(i.node.min_size(box.rect).width for i in nodes)
#         total_grow = sum(i.grow for i in nodes)
#         total_shrink = sum(i.shrink for i in nodes)
#
#         available_space = box.width - reserved_space
#         space_rations = even_divide(available_space, total_grow if available_space >= 0 else total_shrink)
#         at_x = 0
#         for flex in nodes:
#             child_min_size = flex.node.min_size(box.rect)
#             child_box = Box(
#                 width=child_min_size.width + sum(space_rations.pop() for _ in range(flex.grow if available_space >= 0 else flex.shrink)),
#                 height=box.height,
#             )
#             child_box = child_box.offset_by(box.offset + Coordinate(at_x, 0))
#             flex.node.render(frame.shrink_to(child_box), child_box)
#             at_x += child_box.width
#     return Node(min_size_horizontal([i.node.min_size for i in nodes]), render)
#
#
# def vbar(char: str = "|"):
#     def render(frame: Frame, box: Box):
#         frame.draw_box(char, 1, box.height, box.offset)
#     return Node(lambda _: Rect(1, 0), render)
#
# def hbar(char: str = "-"):
#     def render(frame: Frame, box: Box):
#         frame.draw_box(char, box.width, 1, box.offset)
#     return Node(lambda _: Rect(0, 1), render)
#
# V_PROGRESS = " ▁▂▃▄▅▆▇█"
#
# def static_box(nodes: list[Node]):
#     def render(frame: Frame, box: Box):
#         for node in nodes:
#             node.render(frame, box)
#     return Node(min_size_union([i.min_size for i in nodes]), render)
# # ╵╷│
# def clamp(n, smallest, largest): return max(smallest, min(n, largest))
#
# def v_scroll_bar(start: float, showing: float):
#     def render(frame: Frame, box: Box):
#         start_at_pixel = box.height * start
#         start_at_pixel_int = floor(start_at_pixel)
#         start_at_progress = abs(start_at_pixel - start_at_pixel_int -1)
#
#         end_at_pixel = box.height * start + box.height * showing # should be clampt
#         end_at_pixel_int = floor(end_at_pixel)
#         end_at_progress = end_at_pixel - end_at_pixel_int
#
#         match [start_at_progress > 0.33, start_at_progress > 0.66]:
#             case [True, True]:
#                 start_char = "│"
#             case [True, False]:
#                 start_char = "╷"
#             case _:
#                 start_char = " "
#
#         match [end_at_progress > 0.33, end_at_progress > 0.66]:
#             case [True, True]:
#                 end_char = "│"
#             case [True, False]:
#                 end_char = "╵"
#             case _:
#                 end_char = " "
#
#         for i in range(box.height):
#             if i == start_at_pixel_int:
#                 frame.draw_pixel(start_char, box.offset + Coordinate(0, i))
#             elif i == end_at_pixel_int:
#                 frame.draw_pixel(end_char, box.offset + Coordinate(0, i))
#             elif start_at_pixel_int < i < end_at_pixel_int:
#                 frame.draw_pixel("│", box.offset + Coordinate(0, i))
#     return Node(lambda _: Rect(1, 1), render)
