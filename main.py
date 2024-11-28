import asyncio
import os
from typing import Callable, Self
from dataclasses import dataclass
from functools import reduce
from abc import ABC, abstractmethod
from enum import Enum, auto


# desing requirements:

# MOVEMENT
# jk for vertical box
# lh for horizontal box (if j or k pressed it takes you further down)

# VISIBILITY CONTROL
# different elements visible declerativly (functions return ui)

# LAYOUT
# containers addapt size to fill content
# boxes get layouted outside of eachother
# parent may decide children (RULES)

@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int
    def __add__(self, other):
        return Coordinate(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Coordinate(self.x - other.x, self.y - other.y)
    
class Screen:
    def __init__(self, width: int, height: int, fill: str):
        self.width = width
        self.height = height
        self._data: list[str] = [fill for _ in range(width * height)]
        """
        matrix indicies work in this pattern:
        0 1 2 3 4
        5 6 7 8 9
        """

    def get(self, pos: Coordinate) -> str:
        return self._data[pos.x + pos.y * self.width]

    def set(self, pos: Coordinate, data: str) -> None:
        self._data[pos.x + pos.y * self.width] = data

    def split_by_lines(self) -> tuple[str, ...]:
            out: list[str] = []
            for h in range(self.height):
                current_row = [self.get(Coordinate(w, h)) for w in range(self.width)]
                out.append("".join(current_row))
            return tuple(out)

@dataclass(frozen=True)
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


@dataclass(frozen=True)
class Frame:
    """a sub part of the screen"""
    view_box: Box
    screen: Screen

    def draw_pixel(self, fill: str, at: Coordinate) -> None:
        if not self.view_box.is_point_inside(at):
            return
        self.screen.set(at, fill)

    def draw_box(self, fill: str, width: int, height: int, start: Coordinate = Coordinate(0, 0)) -> None:
        for x in range(start.x, start.x + width):
            for y in range(start.y, start.y + height):
                self.draw_pixel(fill, Coordinate(x, y))

    def draw_string(self, content: str, at: Coordinate = Coordinate(0, 0)) -> None:
        for y, line in enumerate(content.split('\n')):
            for x, char in enumerate(line):
                self.draw_pixel(char, Coordinate(x+at.x, y+at.y))

    def shrink_to(self, other_box):
        return Frame(
            view_box=self.view_box.intersect(other_box),
            screen=self.screen
        )

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
    corner_tl="┌",
    corner_tr="┐",
    corner_bl="└",
    corner_br="┘",
)

@dataclass(frozen=True)
class Node:
    min_size: Box
    render: Callable[[Frame, Box], None]
    # Frame is the view to the screen
    # Box is the dimensions for the node


# type Node = Callable[[Frame], Result]
def render(root_node: Node) -> str:
    terminal_size = os.get_terminal_size()
    width = terminal_size.columns
    height = terminal_size.lines - 1
    screen = Screen(width, height, " ")
    root_node.render(Frame(Box(width, height), screen), Box(width, height))
    return "\n".join(screen.split_by_lines())

def text(string: str):
    split_string = string.split('\n')
    min_size = Box(
        width=max([len(i) for i in split_string]),
        height=len(split_string)
    )
    def render(frame: Frame, box: Box):
        frame.draw_string(string, box.offset)
    return Node(min_size, render)

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

@dataclass
class Flex:
    grow: int = 1
    shrink: int = 1
    basis: bool = False
    def __or__(self, other: Node) -> tuple[Self, Node]:
        return (self, other)

def even_divide(num, denomenator) -> list[int]:
    return [num // denomenator + (1 if x < num % denomenator else 0)  for x in range (denomenator)]

def vbox_flex(nodes: list[tuple[Flex, Node]]):
    min_size = Box(
        max(i[1].min_size.width for i in nodes),
        sum(i[1].min_size.height for i in nodes)
    ) if nodes else Box(0, 0)

    reserved_space = sum(i[1].min_size.height if i[0].basis else 0 for i in nodes)
    total_grow = sum(i[0].grow for i in nodes)
    total_shrink = sum(i[0].shrink for i in nodes)

    def render(frame: Frame, box: Box):
        available_space = box.height - reserved_space
        space_rations = even_divide(available_space, total_grow if available_space >= 0 else total_shrink)
        at_y = 0
        for flex, node in nodes:
            child_box = Box(
                width=box.width,
                height=(node.min_size.height if flex.basis else 0) + sum(space_rations.pop() for _ in range(flex.grow if available_space >= 0 else flex.shrink))
            )
            child_box = child_box.offset_by(box.offset + Coordinate(0, at_y))
            node.render(frame.shrink_to(child_box), child_box)
            at_y += child_box.height
    return Node(min_size, render)

def separator():
    min_size = Box(0, 1)
    def render(frame: Frame, box: Box):
        frame.draw_box("-", box.width, 1, box.offset)
    return Node(min_size, render)

class NavDirection(Enum):
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()


class Component(ABC):
    @abstractmethod
    def render(self) -> Node:
        """renders the component"""
        ...
    def navigate(self, nav_direction: NavDirection) -> bool:
        return False

    def use_input(self, user_input: str) -> bool:
        """Do something with input. Returns a boolean of weather the input was used or not"""
        return False

class ContainerV(Component):
    def __init__(
            self,
            container_type: Callable[[list[Node]], Node],
            items: list[Component]
        ) -> None:
        super().__init__()
        self.container_type = container_type
        self.items = items

        self._selected_item_idx = None   

    def render(self):
        return self.container_type([i.render() for i in self.items])

    def use_input(self, user_input: str) -> bool:
        if self._selected_item_idx:
            return self.items[self._selected_item_idx].use_input(user_input)
        return False
    # actually accepting just user input would also do. I mean it would propagate and consume.
    # but no if i try implement mouse input it would be bad
    def navigate(self, nav_direction: NavDirection) -> bool:
        if self._selected_item_idx is None:
            self._selected_item_idx = 0

        # TODO: also handle if container is empty please
        if self.items[self._selected_item_idx].navigate(nav_direction):
            return True

        if nav_direction == NavDirection.UP:
            self._selected_item_idx -= 1
        
        # RETURN TRUE IF IN BOUNDS, ELSE FALSE

class TextInput(Component):
    def __init__(self) -> None:
        super().__init__()
        self._active = False
        self._accumulated_input = ""
    def render(self) -> Node:
        return border(text("hi"))
    def use_input(self, user_input: str) -> bool:
        self._accumulated_input += user_input

        if user_input == ENTER:
            self._active = True
        

    def navigate(self, nav_direction: NavDirection) -> bool:
        return self._active





layout = border(vbox_flex([
    Flex() | vbox([
        text(str(i) + " hi") for i in range(15)
    ]),
    Flex(grow=0, shrink=0, basis=True) | vbox([
        separator(),
        text("menuhej"),
        text("menuhejsan"),
    ])
]))

print(render(layout))
# ok now

# so screenview and allocated space is different
# allocated space may change after every node
# screenview changes only on containers so that elements think they have more space han they have



# TODO:
# navigation up down left right, maybe a function nav(direction)
# some way to have different nodes depending on state. (for example button chaning color)
#   and preferably without needing to re-initialize (not render there is a difference!) the whole node tree but only the changed branch
 

# OPTIMISATIONS:
# dont even start renderign stuff out of screen.

# define getchar
try:
    # if on windows
    import msvcrt
    def get_char():
        return msvcrt.getwch()
except ImportError:
    # if on linux (thx chatgippity)
    import sys
    import tty
    import termios

    def get_char():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

# async def blink():
#     while True:
#         await asyncio.sleep(1)
#         print("blink")

async def main(layout):
    loop = asyncio.get_event_loop()
    active_component: Component | None = None
    while True:
        user_input = await loop.run_in_executor(executor=None, func=get_char)

        if active_component is not None:
            ...
        




        # fire and forget method:
        # asyncio.create_task(blink())

# def update_on_input(f: Callable[[str, ], int]):
#     ...


# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
#     ...
