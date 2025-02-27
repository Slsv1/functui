from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Callable
from dataclasses import dataclass

from classes import *
from classes import Node
from node import *

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
