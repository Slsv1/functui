import asyncio
import os
from typing import Callable, Self
from dataclasses import dataclass
from abc import ABC


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
    
class Matrix:
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

@dataclass
class DrawBox:
    fill: str
    start: Coordinate
    width: int
    height: int

@dataclass
class DrawPixel:
    fill: str
    at: Coordinate

@dataclass
class DrawString:
    content: str
    width: int
    height: int
    at: Coordinate

type DrawCommand = DrawBox | DrawPixel | DrawString
#type DrawCommands = list[DrawCommand]

@dataclass(frozen=True)
class Result:
    commands: list[DrawCommand]
    unused_right: int = 0
    unused_bottom: int = 0
    def extend(self, commands: list[DrawCommand]) -> Self:
        return self.__class__(
            commands=commands + self.commands,
            unused_right=self.unused_right,
            unused_bottom=self.unused_bottom
        )
    # def gather(self, results: list[Result]) -> Self:
    #     return self.__class__(
    #         commands=[i.commands for command
    #     )

@dataclass(frozen=True)
class Frame:
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
    def shrink_by_unused(self, result: Result) -> Self:
        return self.__class__(
            width=self.width - result.unused_right,
            height=self.height - result.unused_bottom,
            offset=self.offset
        )
    def with_offset(self, offset: Coordinate):
        return self.__class__(
            width=self.width,
            height=self.height,
            offset=self.offset + offset
        )
    def draw_pixel(self, fill: str, at: Coordinate) -> DrawPixel:
        return DrawPixel(
            fill=fill,
            at=at + self.offset
        )
        
    def draw_box(self, fill: str, width: int, height: int, start: Coordinate = Coordinate(0, 0)) -> DrawBox:
        return DrawBox(
            fill=fill,
            width=width,
            height=height,
            start=start + self.offset,
        )

    def draw_string(self, content: str, height: int, width: int, at: Coordinate = Coordinate(0, 0)):
        return DrawString(
            content=content,
            height=height,
            width=width,
            at=at + self.offset,
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

type Node = Callable[[Frame], Result]

def render(root_node: Node) -> str:
    terminal_size = os.get_terminal_size()
    width = terminal_size.columns
    height = terminal_size.lines - 1
    frame = Frame(width=width, height=height)
    result = root_node(frame)
    screen = Matrix(width, height, " ")

    for command in result.commands:
        if isinstance(command, DrawPixel):
            screen.set(command.at, command.fill)
        elif isinstance(command, DrawBox):
            for x in range(command.start.x, command.start.x + command.width):
                for y in range(command.start.y, command.start.y + command.height):
                    screen.set(Coordinate(x, y), command.fill)
        elif isinstance(command, DrawString):
            for y, line in enumerate(command.content.split('\n')[:command.height]):
                for x, char in enumerate(line[:command.width]):
                    screen.set(Coordinate(x+command.at.x, y+command.at.y), char)

    return "\n".join(screen.split_by_lines())
            
    
# endpoint 
def text(string: str) -> Node:
    split_string = string.split('\n')
    lines = len(split_string)
    max_chars = max(len(row) for row in split_string)

    def text(frame: Frame) -> Result:
        unused_bottom = frame.height - lines
        unused_right = frame.width - max_chars
        return Result(
            commands=[frame.draw_string(string, frame.height, frame.width)],
            unused_bottom=unused_bottom if unused_bottom > 0 else 0, #BUG: IF OUT OF BOUNDS
            unused_right=unused_right if unused_right > 0 else 0,
        )
    return text


def border(node: Node) -> Node:
    style = BORDER_ROUNDED
    def out(frame: Frame) -> Result:
        result = node(frame.shrink(1, 1, 1, 1))
        frame = frame.shrink_by_unused(result)
        return result.extend([
            frame.draw_box(fill=style.line_v, width=1, height=frame.height),
            frame.draw_box(fill=style.line_h, width=frame.width, height=1),
            frame.draw_box(fill=style.line_v, width=1, height=frame.height, start=Coordinate(frame.width-1, 0)),
            frame.draw_box(fill=style.line_h, width=frame.width, height=1, start=Coordinate(0, frame.height-1)),
            frame.draw_pixel(fill=style.corner_tl, at=Coordinate(0, 0)),
            frame.draw_pixel(fill=style.corner_tr, at=Coordinate(frame.width-1, 0)),
            frame.draw_pixel(fill=style.corner_br, at=Coordinate(frame.width-1, frame.height-1)),
            frame.draw_pixel(fill=style.corner_bl, at=Coordinate(0, frame.height-1)),
        ])
    return out

def vbox(nodes: list[Node]) -> Node:
    def out(frame: Frame) -> Result:
        commands: list[DrawCommand] = []
        remaining_frame = frame
        for node in nodes:
            result = node(remaining_frame)
            offset = Coordinate(frame.offset.x, remaining_frame.offset.y + (remaining_frame.height - result.unused_bottom))
            remaining_frame = Frame(
                frame.width,
                result.unused_bottom,
                offset=offset
            )
            commands.extend(result.commands)
            if result.unused_bottom <= 0:
                break
        
        return Result(
            commands
        )
            
    return out



print(render(
    border(vbox([
        border(text("aaaaaaaaaaa \nb\nc\ndddddddddddddddddddddddd\ne\nf\ngdfdfdf")),
        text("aaaaaaaaaaaa"),
        text("hej"),
        border(text("aaaaaaaaaaaaggg")),
        border(border(text("hej")))
    ]))
)) 
# TODO:
# add used to result!!!!!!
# scrollwheel and input processing
# handle out of screen stuff
# flexboxy

# define getchar
# try:
#     # if on windows
#     import msvcrt
#     def get_char():
#         return msvcrt.getwch()
# except ImportError:
#     # if on linux (thx chatgippity)
#     import sys
#     import tty
#     import termios

#     def get_char():
#         fd = sys.stdin.fileno()
#         old_settings = termios.tcgetattr(fd)
#         try:
#             tty.setraw(fd)
#             ch = sys.stdin.read(1)
#         finally:
#             termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
#         return ch

# async def blink():
#     while True:
#         await asyncio.sleep(1)
#         print("blink")

# async def main():
#     loop = asyncio.get_event_loop()
#     await asyncio.sleep(4)
#     while True:
#         user_input = await loop.run_in_executor(executor=None, func=get_char)
#         # fire and forget method:
#         # asyncio.create_task(blink())

# def update_on_input(f: Callable[[str, ], int]):
#     ...


# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
#     ...
