from dataclasses import dataclass
from functui.common import *
from functui import layout_to_str, Rect, Layout

import os

# To avoid writing boilerplate use a dataclass that is included
# in pythons standard library.
@dataclass
class Model():
    counter: int = 0

def update(input: str, m: Model):
    if input == "i":
        m.counter += 1
    elif input == "d":
        m.counter -= 1

def view(m: Model) -> Layout:
    layout = text(str(m.counter)) | center | border
    return layout

m = Model()

# Event loop.
while True:
    # first clear terminal and draw
    os.system('cls' if os.name == 'nt' else 'clear')
    print(layout_to_str(layout=view(m), dimensions=Rect(11, 3)))

    # then get input
    i = input()
    if i == "exit":
        break # exit program

    # then update
    update(i, m)

