from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Callable

from classes import *
from classes import Node
from node import *

class NavDirection(Enum):
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()
    STAY = auto()


class Component(ABC):
    @abstractmethod
    def get_node(self) -> Node:
        """renders the component"""
        ...
    def use_nav(self, nav_direction: NavDirection) -> bool:
        """Navigate. Return if the navigation was successful or not"""
        return False

    def use_input(self, user_input: str) -> bool:
        """Do something with input. Returns a boolean of weather the input was used or not"""
        return False

class ContainerV(Component):
    def __init__(
            self,
            container_type: Callable[[list[Node]], Node],
            items: list[Component]
        ) -> None:
        super().__init__()
        self.container_type = container_type
        self.items = items

        self._selected_item_idx = None   

    def get_node(self):
        return self.container_type([i.get_node() for i in self.items])

    def use_input(self, user_input: str) -> bool:
        if self._selected_item_idx:
            return self.items[self._selected_item_idx].use_input(user_input)
        return False

    def use_nav(self, nav_direction: NavDirection) -> bool:
        if not self.items:
            return False

        if self._selected_item_idx is None:
            self._selected_item_idx = 0
        
        if self.items[self._selected_item_idx].use_nav(nav_direction):
            return True

        match nav_direction:
            case nav_direction.UP:
                # if on beggining of list
                if self._selected_item_idx == 0:
                    return False
                self._selected_item_idx -= 1
            case nav_direction.DOWN:
                # if on end of list
                if self._selected_item_idx == len(self.items):
                    return False
                self._selected_item_idx += 1
            case _:
                return False

        return True
        

        # RETURN TRUE IF IN BOUNDS, ELSE FALSE

class Button(Component):
    def __init__(self, text: Node) -> None:
        super().__init__()
        self.text = text
    
    def get_node(self) -> Node:
        return self.text
    def use_input(self, user_input: str) -> bool:
        return super().use_input(user_input)

# class TextInput(Component):
#     def __init__(self) -> None:
#         super().__init__()
#         self._active = False
#         self._accumulated_input = ""
#     def render(self) -> Node:
#         return border(text("hi"))
#     def use_input(self, user_input: str) -> bool:
#         self._accumulated_input += user_input

#         if user_input == ENTER:
#             self._active = True
        

#     def navigate(self, nav_direction: NavDirection) -> bool:
#         return self._active
