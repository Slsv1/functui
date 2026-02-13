from .classes import *
from .common import vbar

from enum import Enum, auto
from dataclasses import dataclass
from typing import Self, Any
from functools import partial


class ResizableSplitAction(Enum):
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    CENTER = auto()

@dataclass(frozen=True, eq=True, unsafe_hash=True)
class ResizableSplitResultData(ResultData):
    id_to_data: dict[int, tuple[int,int, Box]]
    def merge_children(self, child_data):
        return ResizableSplitResultData({**self.id_to_data, **child_data.id_to_width})

def _v_resizable_split_render(
        left: Layout,
        right: Layout,
        sep: Layout,
        obj_id: int,
        split_at: int,
        frame: Frame,
        box: Box
) -> Result:
    split_rect = sep.min_size(frame.measure_text, box.rect)

    split_at = clamp(split_at, 0, box.width-1-split_rect.width)

    left_box = Box(
        split_at,
        box.height,
        box.position,
    )
    right_box = Box(
        box.width-split_at-split_rect.width,
        box.height,
        box.position + Coordinate(split_at + split_rect.width, 0)
    )
    split_box = Box(
        split_rect.width,
        box.height,
        box.position + Coordinate(split_at, 0)
    )

    res = Result()
    res.set_data(ResizableSplitResultData({obj_id: (split_at, box.width, split_box)}))

    res.add_children_after([
        left.render(left_box, frame.shrink_to(left_box)),
        sep.render(split_box, frame.shrink_to(split_box)),
        right.render(right_box, frame.shrink_to(right_box)),
    ])
    return res


    

@dataclass
class VResizableSplit:
    position = 0
    def view(self, left: Layout, right: Layout, sep: Layout = vbar) -> Layout:
        return Layout(
            self.view,
            min_size_horizontal([left.min_size, right.min_size, sep.min_size]),
            partial(_v_resizable_split_render, left, right, sep, id(self), self.position)
        )
    def update(self, result: Result, action: ResizableSplitAction | None, mouse_position: Coordinate) -> Self:
        data = result.try_data(ResizableSplitResultData)
        if data is None:
            return self
        relevant_data = data.id_to_data.get(id(self), None)
        if relevant_data is None:
            return self
        actual_position, box_width, mouse_box = relevant_data

        match action:
            case ResizableSplitAction.MOVE_LEFT:
                self.position -= 1
            case ResizableSplitAction.MOVE_RIGHT:
                self.position += 1
            case ResizableSplitAction.CENTER:
                self.position = box_width // 2





