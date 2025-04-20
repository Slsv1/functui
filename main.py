import asyncio
from node import *
from classes import Coordinate, Node
from node import empty, render, Color, render_to_fit_terminal
from functools import lru_cache
from dataclasses import dataclass
from classes import CharStyle
from component import AppState

import sys, re
if(sys.platform == "win32"):
    import ctypes
    from ctypes import wintypes
else:
    import termios


# app_state = AppState()
# BOX_ID = 1

# layout = border ** app_state.on_hover(
#     id=(BOX_ID),
#     hover=foreground(Color.RED)
#     default=foreground(Color.GREEN)
# ) ** vbox([
#     app_state.on_hover(BOX_ID, 1)
# ])
# vidget.next()

state = AppState()
x = 0
y = 0
active = combine(foreground(Color.CYAN), border, no_style)
while True:
    user_in = input()
    if user_in == "esc":
        break
    if user_in == "s":
        y += 1
    if user_in == "w":
        y -= 1
    if user_in == "a":
        x -= 1
    if user_in == "d":
        x += 1
    mouse_pos = Coordinate(x, y)
    print(mouse_pos)
    state.step(mouse_pos)

    layout = static_box([
        border ** vbox([
            shrink ** state.on_mouse(
                key=(1,),
                default=border ** text("hej"),
                hover=active ** text("eeee\nhej"),
            ),
            shrink ** state.on_mouse(
                key=(2,),
                default=border ** text("crem"),
                hover=active ** text("ddds\nddd"),
            ),
        ]),
        custom_padding(mouse_pos.y, 0, mouse_pos.x) ** text("x"),
    ])
    print(render(10, 10, layout))


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
