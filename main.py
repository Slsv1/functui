import asyncio
from node import *
from classes import Coordinate, Node
from node import empty, render, Color, render_to_fit_terminal
from functools import lru_cache
from dataclasses import dataclass
from classes import CharStyle
# desing requirements:


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

# print(render(100, 10, layout))

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
