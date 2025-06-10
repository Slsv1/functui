from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Callable, Iterable, Self
from dataclasses import dataclass, field

from classes import *
from classes import Node
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
            return self.__class__((*self.data, (self.data[-1][0] if direction is None else direction, id)))
        return self.__class__((*self.data, (direction if direction is not None else Direction.VERTICAL, id)))
    @property
    def direction(self):
        return self.data[-1][0]
    def __bool__(self):
        return bool(len(self.data))

def root_vertical():
    return DataID(((Direction.VERTICAL, 0),))

def try_find_nearest(nav_data: list[DataID], current_index: int, direction: Direction, backwards: bool) -> int | None:
    next_index = current_index
    advance = lambda: next_index + (-1 if backwards else 1)
    next_index = advance()

    original_depth = len(nav_data[current_index].data)
    changed_directions = False

    while True:
        # if next index is out of bounds
        if next_index >= len(nav_data) or next_index < 0:
            return None
        
        # if next index parent is a different direction then inputed,
        # in this case just keep advancing index untill either end of nav_data or direction matches and nav_depth is same or less than original
        if nav_data[next_index].data[-2][0] != direction:
            changed_directions = True 
            next_index = advance()
            continue
        if changed_directions and (len(nav_data[next_index].data) > original_depth):
            next_index = advance()
            continue
        return next_index

def visualise_nav_data(d: list[DataID], selected: DataID = DataID(())):
    return "\n".join([
        (
            (">" if i == selected else "")
            + ".".join(f'{"V" if j[0] == Direction.VERTICAL else "H"}{j[1]}' for j in i.data)
        ) for i in d
    ])

@dataclass
class AppState:
    mouse_position: Coordinate = Coordinate(-1, -1)
    _next_data_id: DataID = DataID(())
    _data_id_to_index: dict[DataID, int] = field(default_factory=dict)
    _nav_data: list[DataID] = field(default_factory=list)
    _current_selected_dataid: DataID = DataID(())

    #
    # state management
    #
    def is_active(self, key: DataID) -> bool:
        return key.data == self._current_selected_dataid.data[: len(key.data)]
    def is_just_activated(self, key: DataID) -> bool:
        ...
    def is_selected(self, key: DataID) -> bool:
        ...
    def is_just_selected(self, key: DataID) -> bool:
        ...

    def queue_to_become_selected(self, key: DataID):
        self._next_data_id = key

    def step(self, mouse_position: Coordinate=Coordinate(-1, -1), nav=Coordinate(0, 0), confirm_pressed: bool = False):
        self.mouse_position = mouse_position

        # current selected dataid can be either
        #   same as in previous cycle
        #   set to value in self._next_data_id (this happens when mouse_positoin overlaps with a read_box node)
        #   incremented if nav is not Coordinte(0, 0)

        if (nav.x != 0 or nav.y != 0) and len(self._nav_data):
            if self._current_selected_dataid == DataID(()): # if no previous selected dataid
                self._current_selected_dataid = self._nav_data[0]
            else:

                direction = Direction.HORIZONTAL if nav.x else Direction.VERTICAL
                if direction == Direction.HORIZONTAL:
                    backwards = True if nav.x < 0 else False
                elif direction == Direction.VERTICAL:
                    backwards = True if nav.y < 0 else False

                next_index = try_find_nearest(self._nav_data, self._data_id_to_index[self._current_selected_dataid], direction, backwards)

                # if found next index
                if next_index is not None:
                    self._current_selected_dataid = self._nav_data[next_index]
        else:
            self._current_selected_dataid = self._next_data_id if self._next_data_id else DataID(())


        self._nav_data.clear()
        self._data_id_to_index.clear()
        self._next_data_id = DataID(())
        
    #
    # nodes
    #
    def interaction(self, key: DataID):
        # important to add entry to dictionary before appending to nav data, so that key is same as index
        self._data_id_to_index[key] = len(self._nav_data)
        self._nav_data.append(key)
        @applicable
        def _out(child: Node):
            return read_box(self, key, self.mouse_position, child)
        return _out

def read_box(app_state: AppState, key: DataID, mouse_position: Coordinate, child: Node) -> Node:
    def render(frame: Frame, box: Box):
        availabe_box = frame.view_box.intersect(box)
        if availabe_box.is_point_inside(mouse_position):
            app_state.queue_to_become_selected(key)
        child.render(frame, box)
    return Node(child.min_size, render)
