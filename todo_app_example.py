from node import *
from node import clamp
from classes import Coordinate, Node, Rect, Frame, Box, min_size_vertical
from dataclasses import dataclass
from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Callable
from component import *
from pynput import keyboard, mouse
from functools import partial

# @dataclass
# class Task():
#     text: str
#     done: bool

# tasks = [Task("example task", True), Task("example task 1", False), Task("example task 1", False)]
# active_border = combine(foreground(Color.CYAN), border, no_style)

# def button(state: AppState, key: DataID, text: Node):
#     return state.interaction(key) ** (active_border if state.is_selected(key) else border) ** text

# def todo_item(state: AppState, key: DataID, task: Task):
#     button_container = key.child(0, Direction.HORIZONTAL)
#     return state.interaction(key) ** (active_border if state.is_selected(key) else border)\
#         ** vbox([
#             hbox([text("Task "), adaptive_text(task.text)]),
#             hbox([
#                 button(state, button_container.child(0), text("edit")),
#                 button(state, button_container.child(1), text("delte")),
#             ]) if state.is_selected(key) else nothing
#         ])

# def get_layout(state: AppState, root: DataID):
#     return border_with_title(text("Todo App")) ** vbox_flex([
#         flex ** vbox([
#             todo_item(state, root.child(0).child(i), task) for i, task in enumerate(tasks)
#         ]),
#         no_flex ** hbar(),
#         no_flex ** hbox([text("hi")]),
#     ])

type Component = Callable[[AppState, DataID], Node]

def v_box_scroll(state: AppState, parent: DataID, components: list[Component], at_y=0):
    key = parent.child(0, Direction.HORIZONTAL)
    container_key = key.child(0, Direction.VERTICAL)
    scroll_bar_key = key.child(1)
    child_nodes = []
    selected_index = 0

    for i, comp in enumerate(components):
        child_key = container_key.child(i)
        child_nodes.append(comp(state, child_key))

        if state.is_active(child_key):
            selected_index = i

    # we need a custom node here so that we can get the available_height
    def render(frame: Frame, box: Box):
        available_height = box.height
        content_height = vbox(child_nodes).min_size(Rect(0, 0)).height
        selected_at_y = vbox(child_nodes[:selected_index+1]).min_size(Rect(0, 0)).height
        at_y = selected_at_y-available_height if (selected_at_y-available_height) > 0 else 0

        percent_available = available_height / content_height
        percent_progress = at_y/content_height

        layout = hbox_flex([
            flex ** vbox(child_nodes, -at_y),
            no_flex ** state.interaction(scroll_bar_key)\
                  ** (v_scroll_bar(percent_progress, percent_available) if percent_available < 1 else nothing)
        ])
        layout.render(frame, box)

    return Node(min_size_vertical([i.min_size for i in child_nodes]), render)

def item(str: str, state: AppState, key: DataID):
    if state.is_active(key):
        return state.interaction(key) ** foreground(Color.CYAN) ** border ** text(str)
    else:
        return state.interaction(key) ** border ** text(str)

def get_layout(state: AppState, root: DataID):
    return padding ** border_with_title(text("My App")) ** v_box_scroll(state, root, [partial(item, "hej 1"),partial(item, "hej 2"),partial(item, "hej 3"),partial(item, "dej 4")])

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
            offset(state.mouse_position.x, state.mouse_position.y) ** foreground(Color.RED) ** bold ** text("x")
        ])))
