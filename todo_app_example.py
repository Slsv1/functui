from node import *
from classes import Coordinate, Node
from dataclasses import dataclass
from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Callable
from component import *

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

@dataclass
class Task():
    text: str
    done: bool

tasks = [Task("example task", True), Task("example task 1", False), Task("example task 1", False)]

def todo_item(state: AppState, key: DataID, task: Task):
    continuation = hbox([text("Task "),adaptive_text(task.text)])
    return state.interaction(
        key=key,
        default=border ** continuation,
        hover=foreground(Color.CYAN) ** border ** no_style** continuation
    )

def get_layout(state: AppState, root: DataID):
    return border_with_title(text("Todo App")) ** vbox_flex([
        flex() ** vbox([todo_item(state, root.child(1).child(index), task) for index, task in enumerate(tasks)]),
        no_flex ** hbar(),
        no_flex ** hbox([
            state.interaction(
                key=root.child(2, direc)
            )
        ])
    ])

state = AppState()
root = root_vertical()
nav_y = 0
while True:
    user_in = get_char()
    nav_y = 0
    x= 0
    y=0
    if user_in == "e":
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
    print(render_to_fit_terminal(get_layout(state, root)))
