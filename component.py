from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Callable, Iterable, Self
from dataclasses import dataclass, field

from classes import *
from classes import Node
from node import empty
from enum import Enum, auto

__all__ = [
    "Direction",
    "DataID",
    "root_vertical",
    "AppState"
]

class Direction(Enum):
    VERTICAL = auto()
    HORIZONTAL = auto()

@dataclass(frozen=True)
class DataID:
    data: tuple[tuple[Direction, int], ...]
    def child(self, id: int, direction: None | Direction = None) -> Self:
        if len(self.data):
            return self.__class__((*self.data, (self.data[-1][0], id)))
        return self.__class__((*self.data, (direction or Direction.VERTICAL, id)))
    @property
    def direction(self):
        return self.data[-1][0]

def root_vertical():
    return DataID(((Direction.VERTICAL, 0),))

def try_find_nearest(nav_data: list[DataID], current_index: int, direction: Direction, backwards: bool) -> int | None:
    next_index = current_index
    advance = lambda: next_index + (-1 if backwards else 1)
    next_index = advance()
    print("supposed next", next_index)

    original_depth = len(nav_data[current_index].data)
    nested = False

    while True:
        if next_index >= len(nav_data) or next_index < 0:
            print("out of bounds", next_index)
            return None
        if nav_data[next_index].direction != direction:
            nested = True 
            print("wheeeat!")
            next_index = advance()
            continue
        if nested and len(nav_data[next_index].data) > original_depth:
            print("nested!!!")
            next_index = advance()
            continue
        return next_index

@dataclass
class AppState:
    mouse_position: Coordinate = Coordinate(-1, -1)
    _next_data_id: DataID = DataID(())
    _nav_data: list[DataID] = field(default_factory=list)
    _current_selected_index: int = -1
    _current_selected_dataid: DataID = DataID(())

    #
    # state management
    #
    def is_selected(self, key: DataID) -> bool:
        return key == self._current_selected_dataid
    def queue_to_become_selected(self, key: DataID):
        print("queued", key)
        self._next_data_id = key

    def step(self, mouse_position: Coordinate=Coordinate(-1, -1), nav=Coordinate(0, 0)):
        self.mouse_position = mouse_position
        self._current_selected_dataid = self._next_data_id
        print(self._current_selected_dataid)
        self._next_data_id = DataID(())
        print(self._current_selected_dataid)
    

        if (nav.x != 0 or nav.y != 0) and len(self._nav_data):
            print("selected index before", self._current_selected_index)
            if self._current_selected_index == -1:
                self._current_selected_index = 0
                self._current_selected_dataid = self._nav_data[0]
            direction = Direction.HORIZONTAL if nav.x else Direction.VERTICAL
            if direction == Direction.HORIZONTAL:
                backwards = True if nav.x < 0 else False
            elif direction == Direction.VERTICAL:
                backwards = True if nav.y < 0 else False
            print(direction, backwards)
            next_index = try_find_nearest(self._nav_data, self._current_selected_index, direction, backwards)
            if next_index is not None:
                print("found", next_index)
                self._current_selected_index = next_index
                self._current_selected_dataid = self._nav_data[next_index]
                
        print("selected index after", self._current_selected_index)
        print("selected data after", self._current_selected_dataid)
        self._nav_data.clear()
        
    #
    # nodes
    #
    def interaction(self, key: DataID):
        self._nav_data.append(key)
        @applicable
        def _out(child: Node):
            return read_box(self, key, self.mouse_position, child)
        return _out

def read_box(app_state: AppState, key: DataID, mouse_position: Coordinate, child: Node) -> Node:
    def render(frame: Frame, box: Box):
        if box.is_point_inside(mouse_position):
            app_state.queue_to_become_selected(key)
        child.render(frame, box)
    return Node(child.min_size, render)
