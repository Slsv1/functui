from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Callable, Iterable
from dataclasses import dataclass, field

from classes import *
from classes import Node
from node import *
from enum import Enum, auto

type DataID = list[int]

class Direction(Enum):
    VERTICAL = auto()
    HORIZONTAL = auto()
    

@dataclass
class ContainerNode:
    node: Node
    child_nav: Direction

def _get_children_dict(d: Iterable[DataID]) -> dict[DataID, list[DataID]]:
    out = {}
    for id in d:
        out.setdefault(id[:-1], []).append(out[id])
    return out

@dataclass
class AppState:
    _mouse_position: Coordinate = Coordinate(-1, -1)
    _data_current: dict[DataID, ContainerNode] = field(default_factory=dict)
    _data_next: dict[DataID, ContainerNode] = field(default_factory=dict)
    def queue_state(self, key: DataID, state: ContainerNode):
        self._data_next[key] = state
    
    def step(self, mouse_position: Coordinate=Coordinate(-1, -1), nav_positon=Coordinate(-1, -1)):
        self._mouse_position = mouse_position
        self._data_current = self._data_next
        self._data_next = {}

    
    def _nav(self, nav: Coordinate):
        x_remaining = nav.x
        y_remaining = nav.y
        current_container_id = [0]
        access = lambda x: self._data_current[x]
        child_dict = _get_children_dict(self._data_current.keys())

        while True:
            if access(current_container_id).child_nav == Direction.VERTICAL:
                children_amount = len(child_dict[current_container_id])
                if children_amount >= y_remaining:
                    self.queue_state(child_dict[current_container_id+])
                    # maybe make it so that children need to be in order





    def interaction(self, key: DataID, default: Node, hover: Node, child_nav=Direction.VERTICAL):
        return read_box(
            self,
            key,
            self._mouse_position,
            ContainerNode(default, child_nav),
            ContainerNode(hover, child_nav),
            self._data_current.get(key, ContainerNode(default, child_nav)).node
        )
 

def read_box(app_state: AppState, key: DataID, mouse_position: Coordinate, default: ContainerNode, hover: ContainerNode, child: Node) -> Node:
    def render(frame: Frame, box: Box):
        if box.is_point_inside(mouse_position):
            app_state.queue_state(key, hover)
        else:
            app_state.queue_state(key, default)
        child.render(frame, box)
    return Node(child.min_size, render)
