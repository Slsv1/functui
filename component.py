from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Callable
from dataclasses import dataclass

from classes import *
from classes import Node
from node import *

type DataID = tuple[int, ...]


@dataclass
class AppState:
    _mouse_position: Coordinate
    _data_current: dict[DataID, NodeConstructor]
    _data_next: dict[DataID, NodeConstructor]
    def queue(self, key: DataID, state: NodeConstructor):
        self._data_next[key] = state
    
    def step(self):
        self._data_current = self._data_next

    def on_hover(self, key: DataID, default: NodeConstructor, hover: NodeConstructor, selected: NodeConstructor):
        return state_manager(
            app_state=self,
            key=key,
            mouse_position=self._mouse_position,
            hover=hover,
            selected=selected,
            child=self._data_current.get(key, default)
        )

def state_manager(app_state: AppState, key: DataID, mouse_position: Coordinate, hover: Node, selected: Node, child: Node):
    def render(frame: Frame, box: Box):
        if box.is_point_inside(mouse_position):
            app_state.queue(key, hover)
        else:
            app_state.queue(key, empty)
        child.render(frame, box)
    return Node(child.min_size, render)



@dataclass
class Component:
    get_node: Callable[[bool, int], Node]
    indicies: Callable[[], int]

def wrap_around(i: int, minimum: int, maximum: int) -> int:
    if i < minimum:
        return maximum
    elif i > maximum:
        return minimum
    return i

def nav(selected: int, components: list[Component], start_at = 0) -> list[Node]:
    out = []
    acc = start_at
    for component in components:
        indicies = component.indicies()
        out.append(component.get_node(selected - acc in range(indicies), selected-acc))
        acc += indicies
    return out
