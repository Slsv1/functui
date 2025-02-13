from dataclasses import dataclass
from typing import Callable, Self
from classes import *

@dataclass
class Add:
    add_by: int
    def forward(self, original: int):
        return original + self.add_by
    def back(self, altered: int):
        return altered - self.add_by

type MinSize = Callable[[Rect], Rect]

def create_min_size(
    child_size: MinSize,
    width_func: Add,
    height_func: Add
):
    def out(from_size: Rect):
        return child_size(Rect(
            width_func.back(from_size.width),
            height_func.back(from_size.height)
        )).expand(
            width_func.forward(from_size.width),
            height_func.forward(from_size.height),
        )
    return out

# @dataclass
# class BaseMinSize:
#     width_func: Add
#     height_func: Add

# @dataclass
# class MinSize(BaseMinSize):
#     child_min_size: Self

#     def width_from_height(self, max_height: int):
#         original = self.width_func.back(max_height)
#         return self.child_min_size.width_from_height(original)
#     def height_from_width(self, max_width: int):
#         original = self.width_func.back(max_width)
#         return self.child_min_size.height_from_width(original)




# MinSize(
#     min_size,
#     Add(2),
#     Add(2)
# )
