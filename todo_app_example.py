from node import *
from classes import Coordinate, Node
from dataclasses import dataclass
from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Callable
from component import *
from pynput import keyboard, mouse

@dataclass
class Task():
    text: str
    done: bool

tasks = [Task("example task", True), Task("example task 1", False), Task("example task 1", False)]
active_border = combine(foreground(Color.CYAN), border, no_style)

def button(state: AppState, key: DataID, text: Node):
    return state.interaction(key) ** (active_border if state.is_selected(key) else border) ** text

def todo_item(state: AppState, key: DataID, task: Task):
    button_container = key.child(0, Direction.HORIZONTAL)
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
        nav_h = 0
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
        elif user_in == "l":
            nav_h = 1
        elif user_in == "h":
            nav_h = -1
        state.step(state.mouse_position + Coordinate(x, y), Coordinate(nav_h, nav_y))
        print(render_to_fit_terminal(static_box([
            get_layout(state, root),
            offset(state.mouse_position.x, state.mouse_position.y) ** foreground(Color.RED) ** bold **  text("x")
        ])))
