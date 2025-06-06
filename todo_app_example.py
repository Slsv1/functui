from node import *
from classes import Coordinate, Node
from dataclasses import dataclass
from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Callable
from component import *
from pynput import keyboard, mouse

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

@dataclass
class Task():
    text: str
    done: bool

tasks = [Task("example task", True), Task("example task 1", False), Task("example task 1", False)]
active_border = combine(foreground(Color.CYAN), border, no_style)

def button(state: AppState, key: DataID, text: Node):
    return state.interaction(key) ** (active_border if state.is_selected(key) else border) ** text

def todo_item(state: AppState, key: DataID, task: Task):
    button_container = key.child(0, Direction.VERTICAL)
    return state.interaction(key) ** (active_border if state.is_selected(key) else border)\
        ** vbox([
            hbox([text("Task "), adaptive_text(task.text)]),
            hbox([
                button(state, button_container.child(0), text("edit")),
                button(state, button_container.child(1), text("delte")),
            ]) if state.is_selected(key) else text("")
        ])

def get_layout(state: AppState, root: DataID):
    return border_with_title(text("Todo App")) ** vbox_flex([
        flex ** vbox([
            todo_item(state, root.child(0).child(i), task) for i, task in enumerate(tasks)
        ]),
        no_flex ** hbar(),
        no_flex ** hbox([]),
    ])

state = AppState()
root = root_vertical()
nav_y = 0
with keyboard.Events() as events:
    for event in events:
        if not isinstance(event, keyboard.Events.Release):
            continue
        if event.key == keyboard.Key.esc:
            break
        user_in = event.key.char
        nav_y = 0
        x=0
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
        print(render_to_fit_terminal(get_layout(state, root), end=''))
