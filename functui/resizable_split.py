from .classes import *
from .common import vbar
from .nav import EMPTY_INTERACTIBLE, InteractibleID, NavState, interaction_area

from enum import Enum, auto
from dataclasses import dataclass
from typing import Callable, Self, Any
from functools import partial


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

    split_at = clamp(split_at, 0, box.width-split_rect.width)

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
        left.render(frame.shrink_to(left_box), left_box),
        sep.render(frame.shrink_to(split_box), split_box),
        right.render(frame.shrink_to(right_box), right_box),
    ])
    return res


    

@dataclass(frozen=True, eq=True, slots=True)
class VResizableSplit:
    position: int
    interactible_id: InteractibleID = EMPTY_INTERACTIBLE
    default_position: Callable[[int], int] = lambda width: width // 2
    def view(self, left: Layout, right: Layout, sep: Layout = vbar) -> Layout:
        return Layout(
            self.view,
            min_size_horizontal([left.min_size, right.min_size, sep.min_size]),
            partial(
                _v_resizable_split_render,
                left,
                right,
                sep | interaction_area(self.interactible_id, dragable=True),
                id(self),
                self.position
            )
        )

    def update(self, result: Result, interactible_id: InteractibleID, nav: NavState) -> Self:
        data = result.try_data(ResizableSplitResultData)
        if data is None:
            return self
        relevant_data = data.id_to_data.get(id(self), None)
        if relevant_data is None:
            return self

        actual_position, box_width, mouse_box = relevant_data
        next_position = actual_position

        if nav.is_held_down(interactible_id):
            next_position += nav.get_mouse_drag_difference().x
        return self.__class__(position=next_position, interactible_id=interactible_id)






