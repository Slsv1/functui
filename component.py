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
    
    def remove_nav(self):
        ...

    def use_input(self, user_input: str) -> bool:
        """Do something with input. Returns a boolean of weather the input was used or not"""
        return False

    

class ContainerV(Component):
    def __init__(
            self,
            container_type: Callable[[list[Node]], Node],
            items: tuple
        ) -> None:
        super().__init__()
        self.container_type = container_type
        self.items = items

        self._selected_item_idx = None   

    def get_node(self):
        return self.container_type([n.get_node() if i != self._selected_item_idx else border(n.get_node()) for i, n in enumerate(self.items)])

    def use_input(self, user_input: str) -> bool:
        if self._selected_item_idx:
            return self.items[self._selected_item_idx].use_input(user_input)
        return False
    
    def remove_nav(self):
        self._selected_item_idx = None
        for i in self.items:
            i.remove_nav()

    def use_nav(self, nav_direction: NavDirection) -> bool:
        if not self.items:
            return False

        if self._selected_item_idx is None:
            self._selected_item_idx = 0
            self.items[self._selected_item_idx].use_nav(nav_direction)
            return True
        
        if self.items[self._selected_item_idx].use_nav(nav_direction):
            return True

        match nav_direction:
            case NavDirection.UP:
                # if on beggining of list
                if self._selected_item_idx == 0:
                    return False
                self.items[self._selected_item_idx].remove_nav()
                self._selected_item_idx -= 1
                self.items[self._selected_item_idx].use_nav(NavDirection.STAY)
                return True
            case NavDirection.DOWN:
                # if on end of list
                if self._selected_item_idx == (len(self.items) - 1):
                    return False
                self.items[self._selected_item_idx].remove_nav()
                self._selected_item_idx += 1
                self.items[self._selected_item_idx].use_nav(NavDirection.STAY)
                return True
            case NavDirection.STAY:
                return True
            case _:
                return False

        # RETURN TRUE IF IN BOUNDS, ELSE FALSE

class Button(Component):
    def __init__(self, text: Node) -> None:
        super().__init__()
        self.text = text
        self.hovered = False
    
    def get_node(self) -> Node:
        return border(self.text) if self.hovered else self.text
    def use_input(self, user_input: str) -> bool:
        print("button pressed yippe")
        return True
    def use_nav(self, nav_direction: NavDirection) -> bool:
        self.hovered = True
        return False
    def remove_nav(self):
        self.hovered = False

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
