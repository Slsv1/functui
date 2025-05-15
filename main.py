import asyncio
from node import *
from classes import Coordinate, Node
from node import empty, render, Color, render_to_fit_terminal
from functools import lru_cache
from dataclasses import dataclass
from classes import CharStyle
from component import AppState, DataID, Direction

state = AppState()
x = 0
y = 0
nav_y = 0
active = combine(foreground(Color.CYAN), border, no_style)
while True:
    user_in = input()
    nav_y = 0
    if user_in == "esc":
        break
    elif user_in == "s":
        y += 1
    elif user_in == "w":
        y -= 1
    elif user_in == "a":
        x -= 1
    elif user_in == "d":
        x += 1
    elif user_in == "j":
        nav_y = 1
    elif user_in == "k":
        nav_y = -1
    mouse_pos = Coordinate(x, y)
    print(mouse_pos)
    state.step(mouse_pos, Coordinate(0, nav_y))

    nav = DataID(((Direction.VERTICAL, 0),))
    layout = static_box([
        border ** vbox([
            shrink ** state.interaction(
                key=nav.child(0),
                default=border ** text("hej"),
                hover=active ** text("hej\nsand"),
            ),
            shrink ** state.interaction(
                key=nav.child(1),
                default=border ** text("hej h"),
                hover=active ** text("hej  \nhej"),
            ),
            shrink ** state.interaction(
                key=nav.child(2),
                default=border ** text("hej h"),
                hover=active ** text("hej  \nhej"),
            )
        ]),
        offset(mouse_pos.x, mouse_pos.y) ** text("x")
    ])
    print(render(20, 10, layout))
    # state._nav(Coordinate(0, 0))


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
    while True:
        user_input = await loop.run_in_executor(executor=None, func=get_char)
        # fire and forget method:
        # asyncio.create_task(blink())

# def update_on_input(f: Callable[[str, ], int]):
#     ...

# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
#     ...
