from dataclasses import dataclass, field
from collections.abc import Callable
from functools import partial
import itertools
from typing import Any, Iterable, Self

from functui._classes import BoxData, Frame, Layout, NodeID, min_size_vertical
from functui._geometry import Box, Coordinate, Rect
from functui._nav import NavState
from functui._common import debug_overlay, hoverable
from functui._xterm import open_terminal

def _vinfinite_scrollable_render(
    node_id: NodeID,
    child_height: int,
    children: tuple[Layout, ...],
    anchor_at: int,
    frame: Frame,
    box: Box,
):
    at_y = box.position.y + anchor_at

    # basicly same as vbox but without avoiding rendering out of bounds stuff.
    # and child height is decided prematurely
    visible_box = frame.view_box

    self_height = 0
    for child in children:
        child_box = Box(
            box.width,
            child_height,
            Coordinate(box.position.x, at_y)
        )
        self_height += child_height

        child_frame = frame.shrink_to(child_box.intersect(visible_box))

        # child.render(frame.with_view_box(Box.from_rect(frame.screen_rect, Coordinate(0, 0))), child_box)
        child.render(child_frame, child_box)
        at_y += child_box.height

    box = Box(box.width, self_height, Coordinate(box.position.x, box.position.y + anchor_at))

    frame.set_box_data(node_id, box, frame.view_box)

@dataclass
class VAutoLoad:
    child_height: int
    margin_before_invisible: int = 10
    load_data_chunk: int = 3

    _anchor_at: int = 0
    _anchor_index: int = 0
    _children_amount: int = 10
    _visible_children: int = 0
    _last_box_data: BoxData | None = None

    @property
    def children_indices(self):
        return tuple(range(self._anchor_index, self._anchor_index + self._children_amount))

    def update(self, nav: NavState) -> None:
        if nav.result_data is not None and id(self) in nav.result_data.box_data:
            box_data = nav.result_data.box_data[id(self)]
            box = box_data.box
            visible_box = box_data.visible_box

            top_overshoot = visible_box.top - (box.top)

            # print(f"top: {top_overshoot}   ", end="")

            # top
            if top_overshoot > self.margin_before_invisible:
                # delete from top
                self._anchor_index += 1
                self._children_amount -= 1
                self._anchor_at += self.child_height
            elif top_overshoot < self.margin_before_invisible:
                index = self._anchor_index - 1
                # add to top
                if index >= 0:
                    self._visible_children -= 1
                    self._anchor_index -= 1
                    self._anchor_at -= self.child_height

            # below
            bottom_overshoot = box.bottom - visible_box.bottom

            # print(f"bottom: {bottom_overshoot}   ")
            if bottom_overshoot < self.margin_before_invisible:
                # add to bottom
                self._children_amount += 3

            elif bottom_overshoot > self.margin_before_invisible * 2 and self._visible_children:
                # delete from bottom
                self._children_amount -= 1

            self._last_box_data = box_data



    def view(self, children: Iterable[Layout]):
        # hoverable so that boxdata gets saved
        layouts = tuple(children)

        return Layout(
            func=VAutoLoad,
            min_size=min_size_vertical([lambda _, __: Rect(0, self._anchor_at)]+list(l.min_size for l in layouts)),
            render=partial(_vinfinite_scrollable_render, id(self), self.child_height, layouts, self._anchor_at)
        )


if __name__ == "__main__":
    pass

    # with open_terminal() as term:
    #     screen = Screen()
    #     vbox_autoload = VBoxAutoload(item_height = 3)
    #
    #     while True:
    #         layout = vbox_autoload.view(lambda data: node) | border_rounded
    #         render_fit_terminal(term, screen, input)
    #
    #     vbox_autoload = vbox_autoload.update(lambda index: idndex)

    import functui
    from functui.nodes import *

    with functui.open_terminal() as term:
        autoload = VAutoLoad(child_height=3)
        screen = functui.Screen()
        screen.set_dimensions(Rect(80, 40))
        nav = functui.NavState()

        while True:
            layout = nav.vsplit(
                node_id="split",
                left=vbox([autoload.view(
                    text(f"data {data}") | border_rounded for data in autoload.children_indices
                )])\
                    | nav.vscrollable("scrollable", scrolling_speed=1)\
                    | border_ascii\
                    | constrain(vmax=10)\
                    | center,
                right=vbox([
                    text(f"loaded data len: {autoload._visible_children}"),
                    text(f"anchor at: {autoload._anchor_at}"),
                ]),
            ) | border
            res = functui.render_fit_screen(term, screen, layout)

            event = term.block_until_input()

            if event.key_event == "ctrl+c":
                break


            nav.update(res, event)
            autoload.update(nav)
