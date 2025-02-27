from node import *
from classes import Coordinate, Node
from dataclasses import dataclass
from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Callable
from component import nav, Component, wrap_around

@dataclass
class Task():
    text: str
    done: bool

tasks = [Task("example task", True), Task("example task 1", False), Task("example task 1", False)]


def task_component(task: Task):
    def get_node(selected: bool, index: int):
        return (background(Color.CYAN) if selected else empty) ** fill ** hbox_flex([
            no_flex ** text("[x]" if task.done else "[ ]"),
            no_flex ** text(" "),
            flex(1) ** (strike_through if task.done else empty) ** adaptive_text(task.text)
        ])
    return Component(get_node, lambda: 1)


def main_component():
    child_components = [task_component(task) for task in tasks]
    def get_node(selected: bool, index: int):
        return border ** vbox_flex([
            flex(1) ** vbox(nav(index, child_components))
        ])
    return Component(get_node, lambda: sum(i.indicies() for i in child_components))


selected_index = 0
while True:
    user_in = input()
    if user_in == "esc":
        break
    if user_in == "j":
        selected_index += 1
    elif user_in == "k":
        selected_index -= 1
    main = main_component()
    selected_index = wrap_around(selected_index, 0, main.indicies() -1)
    print(render_to_fit_terminal(main.get_node(True, selected_index)))
