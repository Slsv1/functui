from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any, Iterable, Self, Callable
from enum import Flag, auto, Enum
from abc import ABC, abstractmethod
from functools import reduce, partial, cache, lru_cache
from wcwidth import wcswidth
from random import random
import math
import os


# FIXME:
# total_shrink in flexbox can sometimes be 0 causing a devision by zero!!!!!!!!!!!!

# TODO: move _navigate_by_keyboard to AppState class and make persistent dataids work!!!!

# Terminology:
# Node:
# A class that represents a node in the ui tree.
# 
# Element:
# A function that returns a Node
#
# Element constructor:
# A function that returns an Element

LRU_MAX_SIZE = 64
#
# utilities
#

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def even_divide(num, denomenator) -> list[int]:
    return [num // denomenator + (1 if x < num % denomenator else 0)  for x in range (denomenator)]

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
    fg_color: Any = Color.RESET
    bg_color: Any = Color.RESET
    style: CharStyle = CharStyle(0)

    def with_char(self, char: str) -> Self:
        return self.__class__(
            char,
            self.char_type,
            self.fg_color,
            self.bg_color,
            self.style,
        )
    def with_char_type(self, char_type):
        return self.__class__(
            self.char,
            char_type,
            self.fg_color,
            self.bg_color,
            self.style,
        )

    def with_style(self, style: CharStyle) -> Self:
        return self.__class__(
            self.char,
            self.char_type,
            self.fg_color,
            self.bg_color,
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
    string: list[Pixel]
    at: Coordinate

type DrawCommand = DrawPixel | DrawBox | DrawStringLine

type MeasureTextFunc = Callable[[str], int]

@dataclass(frozen=True, eq=True)
class Frame:
    """a view on to the canvas"""
    view_box: Box
    screen_rect: Rect
    default_pixel: Pixel
    measure_text: MeasureTextFunc

    def with_pixel(self, pixel: Pixel):
        return self.__class__(
            view_box=self.view_box,
            screen_rect=self.screen_rect,
            default_pixel=pixel,
            measure_text=self.measure_text,
        )

    def shrink_to(self, other_box):
        return Frame(
            view_box=self.view_box.intersect(other_box),
            screen_rect=self.screen_rect,
            default_pixel=self.default_pixel,
            measure_text=self.measure_text,
        )

def _get_default_data(width: int, height: int):
    return [[Pixel() for _ in range(width)] for _ in range(height)]
class Canvas:
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
                for x in range(box.offset.x, box.offset.x + box.width):
                    for y in range(box.offset.y, box.offset.y + box.height):
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



type MinSize = Callable[[MeasureTextFunc, Rect], Rect]
type ElementConstructor = Applicable[Node, Node]

# minsize util functions

def min_size_expand(
    child_size: MinSize,
    width_change: int,
    height_change: int
) -> MinSize:
    def out(measure_text: MeasureTextFunc, from_size: Rect):
        return child_size(measure_text, from_size.expand(-width_change, -height_change)).expand(width_change, height_change)
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
        if at.y < bounds.offset.y or at.y >= bounds.offset.y + bounds.height:
            return

        content_len = frame.measure_text(content)
        outer_x_bound = bounds.offset.x + bounds.width
        #         #---#
        # content |   | content
        #         #---#
        if at.x +content_len < bounds.offset.x or at.x >= outer_x_bound:
            return

        # find initial x offset
        #         #---#
        #    content  |
        #    ^^^^^#---#
        required_offset = bounds.offset.x - at.x
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
                out.append(frame.default_pixel.with_char(char))
            else:
                out.append(frame.default_pixel.with_char(char).with_char_type(CharType.WIDE_HEAD))
                out.append(frame.default_pixel.with_char("").with_char_type(CharType.WIDE_TAIL))
        self._draw_commands.append(DrawStringLine(
            out, at
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


@dataclass()
class Node:
    func: Callable
    """will be used for hash"""
    hash: tuple
    min_size: MinSize
    render: Callable[[Frame, Box], Result]
    def __hash__(self) -> int:
        return hash((self.func, self.hash))
    def __eq__(self, value: object, /) -> bool:
        return (self.func, self.hash) == (value.func, value.hash)




def default_color_to_fg_ansi(color: Color):
    return f"\033[{color.value}m"

def default_color_to_bg_ansi(color: Color):
    return f"\033[{color.value + 10}m"

@cache
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

ANSI_RESET_STYLES = "\033[0m"

def render_ansi(canvas: Canvas) -> str:
    out = []
    lines = canvas.split_by_lines()
    curr_style = CharStyle(0)
    curr_fg = Color.RESET
    curr_bg = Color.RESET
    for line in lines:
        for pixel in line:
            pixel_str = []
            if curr_style != pixel.style:
                style_changes = (curr_style ^ pixel.style)
                new_style =  style_changes & pixel.style
                removed_style = bool(style_changes & curr_style)
                curr_style = pixel.style
                pixel_str.append(
                    [ANSI_RESET_STYLES, style_to_ansi(pixel.style)]\
                    if removed_style\
                    else [style_to_ansi(new_style)]
                )
            if curr_fg != pixel.fg_color:
                curr_fg = pixel.fg_color
                pixel_str.append(default_color_to_fg_ansi(curr_fg))
            if curr_bg != pixel.bg_color:
                curr_bg = pixel.bg_color
                pixel_str.append(default_color_to_bg_ansi(curr_bg))
            pixel_str.append(pixel.char)
            out.append("".join(pixel_str))
        out.append("\n")
    return "".join(out[:-1]) # -1 to remove the \n on the end


def ansi_go_up(y):
    return f"\033[{y}A"

def get_result(dimensions: Rect, measure_text: MeasureTextFunc, root_node: Node) -> Result:
    result = root_node.render(
        Frame(
            screen_rect=dimensions,
            view_box=Box(dimensions.width, dimensions.height),
            default_pixel=Pixel(),
            measure_text=measure_text
        ),
        Box(width=dimensions.width, height=dimensions.height),
    )
    return result

#
# Reactivity
#

class Direction(Enum):
    VERTICAL = auto()
    HORIZONTAL = auto()

@dataclass(frozen=True, eq=True)
class InteractibleIDPart:
    direction: Direction
    local_id: int
    persistent: bool


@dataclass(frozen=True, eq=True)
class InteractibleID:
    data: tuple[InteractibleIDPart, ...]
    """every intercatible id stores its own part at the end of the data tuple, and its ancestors part before it"""
    def child(self, local_id: int, direction: None | Direction = None, persistent: bool = False) -> Self:
        if len(self.data):
            return self.__class__((*self.data, InteractibleIDPart(
                direction=self.data[-1].direction if direction is None else direction,
                local_id=local_id,
                persistent=persistent
            )))
        return self.__class__((*self.data, InteractibleIDPart(
            direction=direction if direction is not None else Direction.VERTICAL,
            local_id=local_id,
            persistent=persistent
        )))
    @property
    def local_direction(self):
        return self.data[-1].direction
    def __bool__(self):
        return bool(len(self.data))
    def with_direction(self, direction: Direction):
        return self.__class__(
            (*self.data[:-1], InteractibleIDPart(
                direction=direction,
                local_id=self.data[-1].local_id,
                persistent=self.data[-1].persistent)
            )
        )
root_vertical = InteractibleID((InteractibleIDPart(direction=Direction.VERTICAL, local_id=0, persistent=False),))
root_horizontal = InteractibleID((InteractibleIDPart(direction=Direction.HORIZONTAL, local_id=0, persistent=False),))

@dataclass(frozen=True, eq=True)
class InteractibleData(ResultData):
    data: tuple[InteractibleID, ...]
    def merge_children(self, child_data):
        return InteractibleData((*self.data, *child_data.data))
    @classmethod
    def create_dummy(cls):
        return cls(tuple())

@dataclass(frozen=True, eq=True)
class NextInteractible(ResultData):
    next_id: InteractibleID
    def merge_children(self, child_data):
        return child_data
    @classmethod
    def create_dummy(cls):
        return cls(InteractibleID(()))

@dataclass(frozen=True, eq=True)
class SetState(ResultData):
    new_state: tuple[tuple[InteractibleID, Any], ...]
    def merge_children(self, child_data):
        return SetState((*self.new_state, *child_data.new_state))
    @classmethod
    def create_dummy(cls):
        return cls(tuple())

def set_state(*new_state: tuple[InteractibleID, Any]):
    return SetState(new_state)

def try_find_nearest(nav_data: list[InteractibleID], current_index: int, direction: Direction, backwards: bool) -> int | None:
    next_index = current_index
    advance = lambda: next_index + (-1 if backwards else 1)
    next_index = advance()

    original_depth = len(nav_data[current_index].data)
    changed_directions = False

    while True:
        # if next index is out of bounds
        if next_index >= len(nav_data) or next_index < 0:
            return None

        # if next index parent is a different direction then inputed,
        # in this case just keep advancing index untill either end of nav_data or direction matches and nav_depth is same or less than original

        if nav_data[next_index].data[
            (original_depth-2) if len(nav_data[next_index].data) >= original_depth else -2 # look at the same parent as of the original depth
        ].direction != direction:
            changed_directions = True 
            next_index = advance()
            continue
        if changed_directions and (len(nav_data[next_index].data) > original_depth): # if depth exceeds original depth then continue
            next_index = advance()
            continue
        return next_index







        return 

def visualize_interactible_id(id: InteractibleID):
    return ":".join(f"{i.local_id}{"V" if i.direction == Direction.VERTICAL else "H"}" for i in id.data)

@dataclass
class AppState:
    mouse_position: Coordinate = Coordinate(-1, -1)
    _last_nav: Coordinate = Coordinate(0, 0)
    _selected: InteractibleID = InteractibleID(())
    _persistent_state: dict[tuple[InteractibleID, Any], Any] = field(default_factory=dict)
    # _persistent_nav: dict[InteractibleID, InteractibleID]


    @property
    def last_nav(self):
        return self._last_nav
    @property
    def selected(self):
        return self._selected

    #
    # persistent state
    #
    def try_state[T](self, interactible_id: InteractibleID, data: type[T]) -> T | None:
        return self._persistent_state.get((interactible_id, data))
    def _set_state(self, interactible_id: InteractibleID, data: Any) -> None:
        self._persistent_state[(interactible_id, data.__class__)] = data
    #
    # state management
    #
    def is_active(self, key: InteractibleID) -> bool:
        return key.data == self._selected.data[: len(key.data)]
    def is_just_activated(self, key: InteractibleID) -> bool:
        ...
    def is_selected(self, key: InteractibleID) -> bool:
        ...
    def is_just_selected(self, key: InteractibleID) -> bool:
        ...
    # while True:
    #    res = render() (print)
    #    input()
    #    step()

    def step(self, mouse_position: Coordinate, nav: Coordinate, res: Result):
        self.mouse_position = mouse_position
        self._last_nav = nav

        # persistent state
        if set_state := res.try_data(SetState):
            for key, state in set_state.new_state:
                self._set_state(key, state)

        # reactivity
        interactible_data=res.try_data(InteractibleData)
        if interactible_data is None:
            return

        nav_data = list(interactible_data.data)

        if (nav.x != 0 or nav.y != 0) and len(nav_data):
            # handle keyboard nav and its edge cases
            if self._selected in nav_data and self._selected != InteractibleID(()):
                selected_index = nav_data.index(self._selected)
                if new_index := _navigate_by_keyboard(self, selected_index, nav_data, nav):
                    self._selected = new_index
            else:
                self._selected = nav_data[0]
        elif next_inderactible := res.try_data(NextInteractible):
            # use mouse navigation instead
            self._selected = next_inderactible.next_id


    def interaction(self, interactible_id: InteractibleID):
        @applicable
        def _out(child: Node):
            return Node(
                func=self.interaction,
                hash=(child,),
                min_size=child.min_size,
                render=partial(_render_read_box, interactible_id, self.mouse_position, child)
            )
        return _out

def _render_read_box(
    interactible_id: InteractibleID,
    mouse_position: Coordinate,
    child: Node,
    frame: Frame,
    box: Box
) -> Result:
    res = Result()
    availabe_box = frame.view_box.intersect(box)
    res.set_data(InteractibleData(
        data=(interactible_id,),
    ))
    if availabe_box.is_point_inside(mouse_position):
        res.set_data(NextInteractible(interactible_id))
    res.add_children_after([child.render(frame, box)])
    return res

def _blessed_get_input(term) -> str:
    while True:
        val = term.inkey()
        if not val.is_sequence:
            return val
@cache
def pixel_styles_to_ansi(pixel: Pixel) -> str:
    return "".join([
        style_to_ansi(pixel.style),
        default_color_to_bg_ansi(pixel.bg_color),
        default_color_to_fg_ansi(pixel.fg_color),
    ])
def blessed_render(term, result: Result):
    for command in result.get_commands():
        if isinstance(command, DrawPixel):
            with term.location(command.at.x, command.at.y):
                print(pixel_styles_to_ansi(command.pixel) + command.pixel.char , end="")


        elif isinstance(command, DrawBox):
            box = command.box
            for x in range(box.offset.x, box.offset.x + box.width):
                for y in range(box.offset.y, box.offset.y + box.height):
                    with term.location(x, y):
                        print(pixel_styles_to_ansi(command.fill) + command.fill.char , end="")
                    # self.set(Coordinate(x, y), command.fill)
        else: #DrawStringLine
            for delta_x, pixel in enumerate(command.string):
                at = Coordinate(command.at.x + delta_x, command.at.y)
                with term.location(at.x, at.y):
                    print(pixel_styles_to_ansi(command.string[0]) + pixel.char , end="")
                ...
        print("", end="", flush=True)


                # self.set(at, pixel)


def blessed_loop(blessed_lib, app: AppState, layout: Callable[[], Node], size_override: Rect | None=None):
    term = blessed_lib.Terminal()
    measure_text = lambda s: wcswidth(s)
    with term.cbreak():
        while True:
            if size_override is None:
                terminal_size = os.get_terminal_size()
                width = terminal_size.columns
                height = terminal_size.lines
            else:
                width = size_override.width
                height = size_override.height

            result = get_result(Rect(width, height), measure_text,  layout())
            canvas = Canvas(width, height)
            canvas.apply_draw_commands(measure_text, result.get_commands()) # 20 %
            out_string = render_ansi(canvas) # 30 %

            with term.location(0, 0), term.hidden_cursor():
                print(out_string, end="", flush=True)

            nav = Coordinate(0, 0)
            val = _blessed_get_input(term)
            nav_val = val.lower()
            if nav_val == "h":
                nav = Coordinate(-1, 0)
            elif nav_val == "j":
                nav = Coordinate(0, 1)
            elif nav_val == "k":
                nav = Coordinate(0, -1)
            elif nav_val == "l":
                nav = Coordinate(1, 0)
            elif nav_val == "q":
                print(term.move_down(height))
                return
            app.step(Coordinate(-1, -1), nav, result)

#
# Element utils
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
        hash=(),
        min_size=min_size_constant(Rect(0, 0)),
        render=lambda f, b: Result(),
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
        hash=split_string,
        min_size = lambda measure_text, _: Rect(
            width=max([measure_text(i) for i in split_string]),
            height=len(split_string)
        ),
        render = partial(_text_render, split_string)
    )

@lru_cache(LRU_MAX_SIZE)
def _text_render(text: tuple[str, ...], frame: Frame, box: Box):
    print("hej jag 'r i text funktionen lol")
    res = Result()
    for y, line in enumerate(text):
        res.draw_string_line(frame, line, box.offset + Coordinate(0, y))
    return res

class Justify(Enum):
    LEFT = auto()
    CENTER = auto()
    RIGHT = auto()

class Expand(Enum):
    VERTICAL = auto()
    HORIZONTAL = auto()

@cache
def _line_len(measure_text: MeasureTextFunc, line: tuple[str]) -> int:
    return sum(measure_text(i) for i in line) + len(line) - 1

@cache
def _split_by_lines(measure_text: MeasureTextFunc, max_width: int, words: tuple[str, ...]) -> list[str]:
    lines: list[list[str]] = []
    curr_line: list[str] = []
    for word in words:
        if  _line_len(measure_text, tuple(curr_line)) + 1 + measure_text(word)<= max_width: # +1 because space between existing line and new word
            curr_line.append(word)
        else:
            lines.append(curr_line)
            curr_line = [word]
    if curr_line != "":
        lines.append(curr_line)
    return [" ".join(i) for i in lines]


def adaptive_text(string: str, justify=Justify.LEFT, overflow=Expand.VERTICAL):
    words = tuple(string.split())
    def min_size(measure_text, available: Rect):
        lines = _split_by_lines(measure_text, available.width, words)
        return Rect(
            max(measure_text(i) for i in lines),
            len(lines)
        )
    return Node(
        func=adaptive_text,
        hash=(words, justify),
        min_size=min_size,
        render=partial(_adaptive_text_render, words, justify),
    )

@lru_cache(LRU_MAX_SIZE)
def _adaptive_text_render(words: tuple[str], justify: Justify, frame: Frame, box: Box):
    res = Result()
    lines = _split_by_lines(frame.measure_text, box.width, words)
    match justify:
        case Justify.LEFT:
            for index, line in enumerate(lines):
                res.draw_string_line(frame, line, box.offset + Coordinate(0, index))
        case Justify.CENTER:
            for index, line in enumerate(lines):
                available_space = box.width - len(line)
                res.draw_string_line(frame, line, box.offset + Coordinate(available_space // 2, index))
        case Justify.RIGHT:
            for index, line in enumerate(lines):
                available_space = box.width - len(line)
                res.draw_string_line(frame, line, box.offset + Coordinate(available_space, index))
    return res

def vbar(char: str = "|"):
    return Node(vbar, (char,), min_size_constant(Rect(1, 1)), partial(_vbar_render, char))
@lru_cache(LRU_MAX_SIZE)
def _vbar_render(char: str, frame: Frame, box: Box):
    res = Result()
    res.draw_box(frame, char, Box(1, box.height, box.offset))
    return res

def hbar(char: str = "-"):
    return Node(hbar, (char,), min_size_constant(Rect(1, 1)), partial(_hbar_render, char))
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
        hash=(child,),
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

def add_style(style: CharStyle, child: Node):
    return Node(
        func=add_style,
        hash=(child, style),
        min_size=child.min_size,
        render=partial(_add_style_render, child, style)
    )
def _add_style_render(child: Node, style: CharStyle, frame: Frame, box: Box):
    return child.render(
        frame.with_pixel(frame.default_pixel.with_style(
            frame.default_pixel.style | style
        )),
        box
    )

@applicable
def no_style(child: Node):
    return Node(
        func=no_style,
        hash=(child,), 
        min_size=child.min_size, 
        render=partial(_no_style_render, child)
    )

def _no_style_render(child: Node, frame: Frame, box: Box):
    return child.render(
        frame.with_pixel(Pixel(style=CharStyle(0))),
        box
    )
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

def _fg_render(color: Any, child: Node, frame: Frame, box: Box) -> Result:
        return child.render(
            frame.with_pixel(Pixel(
                fg_color=color,
                bg_color=frame.default_pixel.bg_color,
                style=frame.default_pixel.style
            )),
            box
        )
def fg(color: Any):
    @applicable
    def _create_fg(child: Node):
        return Node(
            func=fg,
            hash=(color,child),
            min_size=child.min_size,
            render=partial(_fg_render, color, child)
        )
    return _create_fg
def _bg_render(color: Any, child: Node, frame: Frame, box: Box) -> Result:
        return child.render(
            frame.with_pixel(Pixel(
                fg_color=frame.default_pixel.fg_color,
                bg_color=color,
                style=frame.default_pixel.style
            )),
            box
        )
def bg(color: Any):
    @applicable
    def _create_fg(child: Node):
        return Node(
            func=bg,
            hash=(color, child),
            min_size=child.min_size,
            render=partial(_bg_render, color, child)
        )
    return _create_fg

#
# Containers
#

def static_box(children: Iterable[Node]):
    children = tuple(children)
    return Node(
        func=static_box,
        hash=children,
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
        hash=(children, at_y),
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
        hash=(children, at_x),
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
#
def bg_fill_char(char: str):
    @applicable
    def out(child: Node):
        return Node(
            func=bg_fill_char,
            hash=(char,child),
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
    return flex_custom(1, 1, False) ** node

@applicable
def no_flex(node: Node):
    return flex_custom(0, 0, True) ** node


def vbox_flex(children: Iterable[Flex]):
    children = tuple(children)
    return Node(
        func=vbox_flex,
        hash=children,
        min_size=min_size_vertical([i.node.min_size for i in children]),
        render=partial(_vbox_flex_render, children)
    )


@lru_cache(LRU_MAX_SIZE)
def _vbox_flex_render(children: tuple[Flex, ...], frame: Frame, box: Box):
    reserved_space = sum(i.node.min_size(frame.measure_text, box.rect).height for i in children if i.basis)
    total_grow = sum(i.grow for i in children)
    total_shrink = sum(i.shrink for i in children)

    available_space = box.height - reserved_space
    space_rations = even_divide(available_space, total_grow if available_space >= 0 else total_shrink)
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
        hash=children,
        min_size=min_size_horizontal([i.node.min_size for i in children]),
        render=partial(_hbox_flex_render, children)
    )
@lru_cache(LRU_MAX_SIZE)
def _hbox_flex_render(children: Iterable[Flex], frame: Frame, box: Box):
    reserved_space = sum(i.node.min_size(frame.measure_text, box.rect).width for i in children if i.basis)
    total_grow = sum(i.grow for i in children)
    total_shrink = sum(i.shrink for i in children)

    available_space = box.width - reserved_space
    space_rations = even_divide(available_space, total_grow if available_space >= 0 else total_shrink)
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

@applicable
def shrink(child: Node):
    return Node(
        func=shrink,
        hash=(child,),
        min_size=child.min_size,
        render=partial(_shrink_render, child),
    )
def _shrink_render(child: Node, frame: Frame, box: Box):
    min_size = child.min_size(frame.measure_text, box.rect)
    child_box = Box(
        min_size.width,
        min_size.height,
        box.offset
    )
    return child.render(frame, child_box)

def offset(x: int=0, y: int=0):
    coord = Coordinate(x, y)
    @applicable
    def out(child: Node):
        return Node(
            func=offset,
            hash=(child, coord),
            min_size=min_size_expand(child.min_size, coord.x, coord.y),
            render=partial(_offset_render, coord, child),
        )
    return out
@lru_cache(LRU_MAX_SIZE)
def _offset_render(by: Coordinate, node: Node, frame: Frame, box: Box):
    return node.render(frame, box.offset_by(by))


#
# V_PROGRESS = " ▁▂▃▄▅▆▇█"
#

# # ╵╷│
#
def h_guage(progress: int):
    return Node(
        func=h_guage,
        hash=(progress,),
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
        hash=(start, showing),
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

#
# Components
#

type Component = Callable[[AppState, InteractibleID], Node]

def nav(children: Iterable[Component], state: AppState, id: InteractibleID) -> list[Node]:
    return [child(state, id.child(i)) for i, child in enumerate(children)]

# vbox_scroll be needin:
#   nav direction
#   STORED - last at_y (important if some other thingy goes active)
#
# if nav is down then:
#    make sure that selected_object's end is visible (current behaviour)
# if nav is up then:
#    make sure that selected object's beggining is visible
#

UNLIMITED_SPACE = 2 ** 16
def vbox_scroll(components: list[Component], state: AppState, key: InteractibleID):
    key = key.with_direction(Direction.HORIZONTAL)
    container_key = key.child(0, Direction.VERTICAL)
    scroll_bar_key = key.child(1)

    child_nodes = []
    selected_index = 0
    direction_down = state.last_nav.y > 0

    for i, comp in enumerate(components):
        child_key = container_key.child(i)
        child_nodes.append(comp(state, child_key))

        if state.is_active(child_key):
            selected_index = i

    # we need a custom node here so that we can get the available_height
    def render(frame: Frame, box: Box):
        available_height = box.height
        content_height = vbox(child_nodes)\
            .min_size(frame.measure_text, Rect(box.width-1, UNLIMITED_SPACE)).height

        # pick end

        # selected at y is at what y coordinate the selected child starts
        # desired at y is where the at_y var needs to be so that the childs end is included at the bottom of the box
        selected_at_y_end = vbox(child_nodes[:selected_index+1])\
            .min_size(frame.measure_text, Rect(box.width-1, UNLIMITED_SPACE)).height
        desired_at_y_end = selected_at_y_end-available_height if (selected_at_y_end-available_height) > 0 else 0
        # pick beggining
        desired_at_y_beggining = vbox(child_nodes[:selected_index])\
            .min_size(frame.measure_text, Rect(box.width-1, UNLIMITED_SPACE)).height

        desired_at_y = desired_at_y_end if direction_down else desired_at_y_beggining

        last_at_y = state.try_state(key, int)

        # if last_at_y is not None:
        #     print("last", last_at_y, "beggining", desired_at_y_beggining, "last_end", last_at_y + box.height, "end", selected_at_y_end)
        if last_at_y is not None and last_at_y < desired_at_y_beggining and selected_at_y_end < (last_at_y + box.height):
            at_y = last_at_y
        else:
            at_y = desired_at_y



        percent_available = available_height / content_height
        percent_progress = at_y/content_height

        layout = hbox_flex([
            flex ** vbox(child_nodes, -at_y),
            no_flex ** state.interaction(scroll_bar_key)\
                  ** (fg(Color.CYAN) if state.is_active(scroll_bar_key) else fg(Color.RED))\
                (v_scroll_bar(percent_progress, percent_available))
        ])
        res = Result()
        res.set_data(set_state((key, at_y)))
        res.add_children_after([layout.render(frame, box)])
        return res

    return Node(
        func=vbox_scroll,
        hash=(*tuple(child_nodes), state.selected, direction_down, state.try_state(key, int)), 
        min_size=min_size_vertical([i.min_size for i in child_nodes]),
        render=render
    )
