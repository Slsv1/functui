import asyncio
from node import *
from classes import Coordinate, Node
from node import empty, render, Color, render_to_fit_terminal
from functools import lru_cache
from dataclasses import dataclass
from classes import CharStyle
from component import AppState, DataID, Direction
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

def interactive(id: DataID, app: AppState, default, hover):
    return app.interaction(id) ** (hover if app.is_selected(id) else default)


state = AppState()
active = combine(foreground(Color.CYAN), border, no_style)
nav_y = 0
while True:
    x = 0
    y = 0
    user_in = get_char()
    nav_y = 0
    if user_in == "x":
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
    state.step(state.mouse_position + Coordinate(x, y), Coordinate(0, nav_y))

    nav = DataID(((Direction.VERTICAL, 0),))
    layout = static_box([
        border ** vbox([
            shrink ** interactive(
                id=nav.child(0),
                app=state,
                default=border ** text("hej"),
                hover=active ** text("hej\nsand"),
            ),
            shrink ** interactive(
                id=nav.child(1),
                app=state,
                default=border ** text("hej h"),
                hover=active ** text("hej  \nhej"),
            ),
            shrink ** interactive( 
                id=nav.child(2),
                app=state,
                default=border ** text("hej h"),
                hover=active ** text("hej  \nhej"),
            )
        ]),
        offset(state.mouse_position.x, state.mouse_position.y) ** text("x")
    ])
    print(render(20, 10, layout))
    # state._nav(Coordinate(0, 0))


# define getchar
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
