from dataclasses import dataclass
from collections.abc import Callable
import itertools

from functui._classes import BoxData, Frame, Layout, NodeID, min_size_vertical
from functui._geometry import Box, Coordinate, Rect
from functui._nav import NavState

def _vinfinite_scrollable_render(
    id: NodeID,
    children_below_anchor: tuple[Layout, ...],
    children_above_anchor: tuple[Layout, ...],
    anchor_at: int,
    frame: Frame,
    box: Box,
):
    height_above = 0
    for child in children_above_anchor:
        height_above += child.min_size(frame.measure_text, Rect(box.width, 99999)).height

    at_y = anchor_at - height_above

    # basicly same as vbox but without avoiding rendering out of bounds stuff.
    visible_box = frame.view_box.intersect(box)

    frame.set_box_data(id, box, frame.view_box)

    for child in itertools.chain(children_below_anchor, children_above_anchor):
        child_min_size = child.min_size(frame.measure_text, Rect(box.width, 9999))

        child_box = Box(
            box.width,
            child_min_size.height,
            Coordinate(box.position.x, at_y)
        )

        child.render(frame.shrink_to(child_box.intersect(visible_box)), child_box)
        at_y += child_box.height



@dataclass
class VInfinite_Scrollable:
    load_item_func: Callable[[int], Layout | None]
    anchor_at: int
    anchor_index: int
    margin_before_invisible: int

    _last_box_data: BoxData
    _children_above_anchor: list[Layout]
    _children_below_anchor: list[Layout]

    def update(self, nav: NavState):
        if nav.result_data is not None:
            box_data = nav.result_data.box_data[id(self)]

            visible_box_bottom = box_data.visible_box.position.y + box_data.view_box.height
            box_bottom = box_data.box.position.y + box_data.box.height

            margin_bottom = box_bottom - visible_box_bottom

            if margin_bottom < self.margin_before_invisible:
                # TODO: add children bleow anchor
                # reset anchor index
                ...


            visible_box_top = box_data.visible_box.position.y
            box_top = box_data.box.position.y

            margin_top = visible_box_top - box_top

            if margin_top < self.margin_before_invisible:
                # TODO: add children abowe anchor
                # reset acnhor index
                ...

            # TODO: is this the right place for this?
            self.anchor_at = box_top


    def view(self):
        pass
        # return Layout(
        #     func=VInfinite_Scrollable,
        #     min_size=min_size_vertical()
        #
        # ):

