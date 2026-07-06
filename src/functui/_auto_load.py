from dataclasses import dataclass, field
from collections.abc import Callable
from functools import partial
import itertools

from functui._classes import BoxData, Frame, Layout, NodeID, min_size_vertical
from functui._geometry import Box, Coordinate, Rect
from functui._nav import NavState
from functui._common import debug_overlay

def _vinfinite_scrollable_render(
    node_id: NodeID,
    children_above_anchor: tuple[Layout, ...],
    children_below_anchor: tuple[Layout, ...],
    anchor_at: int,
    frame: Frame,
    box: Box,
):
    height_above = 0
    for child in children_above_anchor:
        height_above += child.min_size(frame.measure_text, Rect(box.width, 99999)).height

    at_y = box.position.y + anchor_at

    # basicly same as vbox but without avoiding rendering out of bounds stuff.
    visible_box = frame.view_box

    self_height = 0
    for child in itertools.chain(children_below_anchor, children_above_anchor):
        child_min_size = child.min_size(frame.measure_text, Rect(box.width, 9999))

        child_box = Box(
            box.width,
            child_min_size.height,
            Coordinate(box.position.x, at_y)
        )
        self_height += child_min_size.height

        child_frame = frame.shrink_to(child_box.intersect(visible_box))

        # frame.set_box_data((node_id, index), child_box, child_frame.view_box)

        child.render(frame.with_view_box(Box.from_rect(frame.screen_rect, Coordinate(0, 0))), child_box)
        at_y += child_box.height

    box = Box(box.width, self_height, Coordinate(box.position.x, box.position.y + anchor_at))

    frame.set_box_data(node_id, box, frame.view_box)

@dataclass
class VInfinite_Scrollable[T]:
    load_data_func: Callable[[int], T | None]
    load_layout_func: Callable[[T], Layout]
    margin_before_invisible: int = 10
    load_data_chunk: int = 3

    _anchor_at: int = 0
    _anchor_index: int = 0
    _last_box_data: BoxData | None = None
    _children_above_anchor: list[T] = field(default_factory=list)
    _children_below_anchor: list[T] = field(default_factory=list)


    def update(self, nav: NavState):
        if nav.result_data is not None and id(self) in nav.result_data.box_data:
            box_data = nav.result_data.box_data[id(self)]
            box = box_data.box
            visible_box = box_data.visible_box


            # self._anchor_at = box_top

            top_overshoot = visible_box.top - box.top 

            print(f"top: {visible_box.top}   ", end="")

            if top_overshoot < self.margin_before_invisible:
                index = self._anchor_index - len(self._children_above_anchor)
                if (new_data := self.load_data_func(index)) is not None:
                    self._children_below_anchor.insert(0, new_data)
                    self._anchor_index -= 1
                    self._anchor_at -= 3


            # below
            bottom_overshoot = box.bottom - visible_box.bottom

            print(f"bottom: {bottom_overshoot}   ")
            if bottom_overshoot < self.margin_before_invisible:
                # add new children
                index = self._anchor_index + len(self._children_below_anchor)
                for i in range(self.load_data_chunk):
                    if (new_data := self.load_data_func(index + i)) is not None:
                        self._children_below_anchor.append(new_data)
                    else:
                        break

            elif bottom_overshoot > self.margin_before_invisible * 2 and self._children_below_anchor:
                # remove children
                self._children_below_anchor.pop()

            self._last_box_data = box_data


    def view(self):
        layouts_above_anchor = tuple(self.load_layout_func(data) for data in self._children_above_anchor)
        layouts_below_anchor = tuple(self.load_layout_func(data) for data in self._children_below_anchor)

        # anchor_dummy_minsize = lambda _, __: Rect(0, self._anchor_at if self._anchor_at > 0 else 0)

        return Layout(
            func=VInfinite_Scrollable,
            min_size=min_size_vertical(list(i.min_size for i in itertools.chain(layouts_above_anchor, layouts_below_anchor))),
            render=partial(_vinfinite_scrollable_render, id(self), layouts_above_anchor, layouts_below_anchor, self._anchor_at)
        )

def debug_explode_view_box(child: Layout):
    return Layout(
        func = debug_explode_view_box,
        min_size=child.min_size,
        render=partial(_debug_explode_view_box_render, child)
    )
def _debug_explode_view_box_render(child, frame, box):
    child.render(frame.with_view_box(Box.from_rect(frame.screen_rect, Coordinate(0, 0))), box)


if __name__ == "__main__":
    import functui
    from functui.nodes import *


    def load_data(index: int):
        return index

    def create_layout(data: int):
        return text(f"data {data}") | border_rounded

    with functui.open_terminal() as term:
        scr = VInfinite_Scrollable(load_data, create_layout)
        screen = functui.Screen()
        screen.set_dimensions(Rect(80, 40))
        nav = functui.NavState()

        while True:
            layout = nav.vsplit(
                node_id="split",
                left=vbox([scr.view()]) | nav.vscrollable("scrollable", scrolling_speed=1) | border_ascii | constrain(vmax=10) | center,
                right=vbox([
                    text(f"children above: {len(scr._children_above_anchor)}"),
                    text(f"children below: {len(scr._children_below_anchor)}"),
                    text(f"anchor at: {scr._anchor_at}"),
                ]),
            ) | border
            res = functui.render_fit_screen(term, screen, layout)

            event = term.block_until_input()

            if event.key_event == "ctrl+c":
                break

            if event.key_event == "g":
                del scr._children_below_anchor[0]
                scr._anchor_at += 3

            nav.update(res, event, mouse_position=event.mouse_position_event)
            scr.update(nav)
