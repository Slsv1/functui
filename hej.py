import dataclasses
import blessed
from functools import cache, lru_cache, partial
from textui import *
from textui import _border_render
from dataclasses import dataclass
from typing import Callable


def selectable(state: AppState, id: InteractibleID, data: Node):
    if state.is_active(id):
        return state.interaction(id) ** fg(Color.CYAN) ** border ** no_style ** data
    else:
        return state.interaction(id) ** border ** data

def status_bar(state: AppState, id: InteractibleID):
    id = id.with_direction(Direction.HORIZONTAL)
    
    return bg(Color.BLACK) ** fill ** hbox_flex([
        no_flex ** bg(Color.RED) ** hbox([text("Bar")]),
        flex ** nothing(),
        no_flex **state.interaction(id.child(0))\
            ** (bg(Color.CYAN) if state.is_active(id.child(0)) else empty) ** text("hej"),
        no_flex **state.interaction(id.child(1))\
            ** (bg(Color.CYAN) if state.is_active(id.child(1)) else empty) ** text("hej"),
    ])


def get_layout(state: AppState, root: InteractibleID):
    return vbox_flex([
        flex ** vbox([
            selectable(state, root.child(0), text("hej")),
            selectable(state, root.child(1), text("hej")),
            selectable(state, root.child(2), text("hej")),
        ]),
        no_flex ** status_bar(state, root.child(3))
    ])
state = AppState()
while True:
    if not blessed_step(blessed, state, get_layout(state, root_vertical), Rect(20, 10)):
        break
