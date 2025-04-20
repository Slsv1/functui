from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Callable
from dataclasses import dataclass, field

from classes import *
from classes import Node
from node import *

type DataID = tuple[int, ...]

@dataclass
class AppState:
    _mouse_position: Coordinate = Coordinate(-1, -1)
    _data_current: dict[DataID, Node] = field(default_factory=dict)
    _data_next: dict[DataID, Node] = field(default_factory=dict)
    def queue_state(self, key: DataID, state: Node):
        self._data_next[key] = state
    
    def step(self, mouse_position: Coordinate):
        self._mouse_position = mouse_position
        self._data_current = self._data_next
        self._data_next = {}

    def on_mouse(self, key: DataID, default: Node, hover: Node):
        return read_box(
            self,
            key,
            self._mouse_position,
            default,
            hover,
            self._data_current.get(key, default)
        )

def read_box(app_state: AppState, key: DataID, mouse_position: Coordinate, default: Node, hover: Node, child: Node) -> Node:
    def render(frame: Frame, box: Box):
        if box.is_point_inside(mouse_position):
            app_state.queue_state(key, hover)
        child.render(frame, box)
    return Node(child.min_size, render)
