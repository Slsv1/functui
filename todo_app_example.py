from node import *
from classes import Coordinate, Node
from dataclasses import dataclass
from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Callable
from component import AppState, DataID

@dataclass
class Task():
    text: str
    done: bool

tasks = [Task("example task", True), Task("example task 1", False), Task("example task 1", False)]
app_state = AppState()


def task_node(id: DataID, task: Task):
    remaining = fill ** hbox_flex([
        no_flex ** text("[x]" if task.done else "[ ]"),
        no_flex ** text(" "),
        flex(1) ** (strike_through if task.done else empty) ** adaptive_text(task.text)
    ])
    return app_state.on_mouse(
        key=id,
        default=remaining,
        hover=background(Color.CYAN) ** remaining,
    )


def main_component():
    ...


# min_size <- min_size
# wrap around with min_size
# 
# a unit must store
#  its size
#  children units and be able to access their size
# method for getting the component out
while True:
    user_in = input()
    if user_in == "esc":
        break
    if user_in == "j":
        selected_index += 1
    elif user_in == "k":
        selected_index -= 1
