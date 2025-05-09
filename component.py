from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Callable, Iterable
from dataclasses import dataclass, field

from classes import *
from classes import Node
from node import empty
from enum import Enum, auto

type DataID = tuple[int, ...]

class ContainerType(Enum):
    VERTICAL = auto()
    HORIZONTAL = auto()

@dataclass
class AppState:
    _mouse_position: Coordinate = Coordinate(-1, -1)

    _data_current: dict[DataID, Node] = field(default_factory=dict)

    _data_next: dict[DataID, Node] = field(default_factory=dict)
    """will become _data_current when step() is called"""

    _containers: dict[DataID, ContainerType] = field(default_factory=dict)

    _selected_key: DataID | None = None
    #
    # state management
    #
    def queue_state(self, key: DataID, state: Node):
        self._data_next[key] = state

    def step(self, mouse_position: Coordinate=Coordinate(-1, -1), nav=Coordinate(0, 0)):
        self._mouse_position = mouse_position
        self._data_current = self._data_next
        self._data_next = {}

        if new_key := self._nav(self._selected_key or (0, 0), ContainerType.VERTICAL, nav.y):
            print("new selected key ! !!")
            self._selected_key = new_key
    
    #
    # navigation
    #
    def get_children(self, parent_key: DataID)-> list[int]:
        out = []
        target_len = len(parent_key)
        for key in self._data_current:
            if len(key) == target_len and key[:target_len-1] == parent_key:
                out.append(key[target_len])
        return out

    def _try_nearest_container(self, key: DataID, type: ContainerType) -> DataID | None:
        for i in range(len(key)):
            current_key = key[:-i]
            result = self._containers.get(current_key)
            if not result:
                continue
            if result != type:
                continue
            return key
        return None
    
    def _nav(self, current_key: DataID, direction: ContainerType, delta: int) -> DataID | None:
        if nearest_container := self._try_nearest_container(current_key, direction):
            current_id = current_key[-1]
            children = self.get_children(nearest_container)
            new_index = current_id - delta
            if new_index < 0: # if overflowing container
                return self._nav(current_key[:-1], direction, new_index)
            elif new_index > len(children):
                return self._nav(current_key[:-1], direction, new_index - len(children))
            return (*current_key[:-1], new_index)
        
        return None
    #
    # nodes
    #
    def interaction(self, key: DataID, default: Node, hover: Node):
        return read_box(
            self,
            key,
            self._mouse_position,
            default,
            hover,
            self._data_current.get(key, default)
        )
    
    def container(self, key: DataID, direction: ContainerType):
        self._containers[key] = direction
        return empty # just so that this function can be used with this syntax " container(KEY, DIRECTION) ** vbox([...])"
 

def read_box(app_state: AppState, key: DataID, mouse_position: Coordinate, default: Node, hover: Node, child: Node) -> Node:
    def render(frame: Frame, box: Box):
        if box.is_point_inside(mouse_position) or key == app_state._selected_key:
            app_state.queue_state(key, hover)
        else:
            app_state.queue_state(key, default)
        child.render(frame, box)
    return Node(child.min_size, render)
