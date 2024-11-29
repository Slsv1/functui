from dataclasses import dataclass
from typing import Self
from classes import Frame, Box, Node, Screen, Coordinate

import os

__all__ = [
    "render",

    # decorators
    "border",

    # data
    "separator",
    "text",

    # containers
    "vbox",
    "vbox_flex",
    "Flex"
]

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
