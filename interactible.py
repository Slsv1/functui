from classes import *
from functools import partial
from enum import Enum, auto

# class NavDirection(Enum):
#     LEFT = auto()
#     RIGHT = auto()
#     UP = auto()
#     DOWN = auto()


# def set_class_dict_item(item, child: Node) -> Node:
#     return partial(_set_class_dict_item, item, child)

# def _set_class_dict_item(item, child: Node, view: View, box: Box, shrink: bool, class_dict: ClassDict):
#     class_dict.set(item)
#     return child(view, box, shrink, class_dict)

# def v_container(model, children: list[Node], view: View, box: Box, shrink: bool, class_dict: ClassDict):
#     if nav_dir := class_dict.try_get(NavDirection):
#         match nav_dir:
#             case NavDirection.UP:
                

#         children = [set_class_dict_item(item, i) for i in children]
#         model(children)
