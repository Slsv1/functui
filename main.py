import asyncio
from node import *
from classes import Coordinate
from node import empty, render, v_scroll_bar, Color, render_to_fit_terminal
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





print(render_to_fit_terminal(
    vbox_flex([
        flex() ** text("hej hej"),
        no_flex ** hbar(),
        flex() ** hbox_flex([
            flex() ** min_size(0, 0) ** shrink ** border ** text("hej hej"),
            flex() ** min_size(0, 0) ** border ** text("hej hej"),
            flex(3) ** min_size(0, 0) ** border ** text("hej hej"),
            flex() ** min_size(0, 0) ** border ** text("hej hej"),
            flex() ** min_size(0, 0) ** border ** text("hej hej"),
        ]),
        no_flex ** background(Color.CYAN) ** fill ** hbox_flex([
            flex() ** hbox([
                background(Color.BLUE) ** text("text"),
                text(" "),
                background(Color.BLUE) ** text("hej"),
                text(" "),
                background(Color.BLUE) ** text("patreon"),
                text(" "),
                vbar()
            ]),
            no_flex ** text(".")
        ])
    ])
))

#TODO: when there are items with different basis properties flexbox shold prioritese expanding those with basis 0 perchance?
# ok no this is bad idea, i need to add configurable basis and make 1 the default.

# layout = border(vbox_flex([
#     Flex() | vbox([
#         text(str(i) + " hi") for i in range(15)
#     ]),
#     Flex(grow=0, shrink=0, basis=True) | vbox([
#         separator() 
#         text("menuhej"),
#         text("menuhejsan"),
#     ]k
# ]))

# print(render(layout))
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
