import asyncio
from node import *

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
