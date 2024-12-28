import asyncio
from node import *
from classes import Coordinate
from node import empty, render, Color, render_to_fit_terminal, v_scroll_bar
from functools import lru_cache
from dataclasses import dataclass
from component import NavDirection, ContainerV, Button, IfHover
from classes import CharStyle

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

# layout_tree = ContainerV(vbox, (
#     IfHover(
#         then=border,
#         otherwise=empty,
#         next_component=Button(text("hej 1"))
#     ),
#     IfHover(
#         then=border,
#         otherwise=empty,
#         next_component=Button(text("hej 1"))
#     ),
#     IfHover(
#         then=border,
#         otherwise=empty,
#         next_component=Button(text("hej 1"))
#     ),
#     IfHover(
#         then=border,
#         otherwise=empty,
#         next_component=ContainerV(vbox, (
#             IfHover(
#                 then=border,
#                 otherwise=empty,
#                 next_component=Button(text("hej 1"))
#             ),
#             IfHover(
#                 then=border,
#                 otherwise=empty,
#                 next_component=Button(text("hej 1"))
#             ),
#             IfHover(
#                 then=border,
#                 otherwise=empty 
#                 next_component=Button(text("hej 1"))
#             ),
#     )))
# ))

# layout_tree.use_nav(NavDirection.DOWN)
# while True:
#     i = input()
#     if i == "k":
#         if not layout_tree.use_nav(NavDirection.UP):
#             layout_tree.use_input(i)
#     elif i == "j":
#         if not layout_tree.use_nav(NavDirection.DOWN):
#             layout_tree.use_input(i)
#     else:
#         layout_tree.use_input(i)

#     print(render(layout_tree.get_node()))

# TODO:
# think about this. Should colour be applied after child renders or before.
# if before then stuff like text cant just override but need to check
# if after then it gets vierd, but maybe then i can use my pipes???

my_position = Coordinate(x=1, y=1)
my_second_position = Coordinate(x=0, y=4)



layout = border ** padding(1) ** hbox_flex([
    flex() ** min_size(0, 0) ** shrink ** static_box([
        border ** padding(1) ** text("hi hur 'r det \ntest test\n\nhej"),
        custom_padding(right=3) ** offset(x=2) ** text("hi hej"),
    ]),
    no_flex ** vbar(":"),
    flex() ** min_size(0, 0) ** padding(1) ** text("hej hej, test")
])

print(render_to_fit_terminal(layout))

#TODO: when there are items with different basis properties flexbox shold prioritese expanding those with basis 0 perchance?
# ok no this is bad idea, i need to add configurable basis and make 1 the default.


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
