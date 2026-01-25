"""Interactible Nodes"""
from .nav import *
from .classes import *
from .common import *
from typing import NamedTuple

class _NewActiveBox(NamedTuple):
    box: Box
    reverse: bool = False

def v_scroll(container_id: InteractibleID, nav: NavState):
    def _v_scroll(child: Layout):
        at_y: int | None = nav.try_state(container_id, int)

        if at_y is None:
            at_y = 0

        # find active box
        active_box = None
        if (_active_box := nav.areas.get(nav.active_id, None)) is not None\
            and nav.action in KEYBOARD_NAV_ACTION\
            and nav.active_id.data[:len(container_id.data)] == container_id.data:
            # ^^^^^^^^ if active_id is a child of container_id
            active_box = _NewActiveBox(_active_box.actual_box, nav.action == NavAction.NAV_UP)


        at_y += nav.get_scrolling_difference()

        return Layout(
            func=v_scroll,
            min_size=child.min_size,
            render=partial(
                _v_scroll_render,
                at_y,
                active_box,
                container_id,
                child,
            )
        )
    return _v_scroll

def _v_scroll_render(
    scroll_dy: int,
    active_box: _NewActiveBox | None,
    container_id: InteractibleID,
    child: Layout,
    frame: Frame, 
    box: Box
):
    # move to selected if selected out of bounds
    a = []
    if active_box is not None:
        selected_at_y = active_box.box.position.y - box.position.y # to local space
        start = 0 # including
        end = box.height # excluding
        # a.append(text(str(start)))
        # a.append(text(str(end)))
        # a.append(text("scroll_dy:" + str(scroll_dy)))
        # a.append(text("selected_at_local:" + str(selected_at_y)))
        # a.append(text("selected_at_global:" + str(active_box)))

        if not (start <= selected_at_y < end):
            a.append(text("NOT_INCLUDED"))
            if active_box.reverse:
                # aproach form below
                scroll_dy += (selected_at_y)
            else:
                # aproach from above
                scroll_dy += (selected_at_y - box.height + active_box.box.height)

    scroll_dy = clamp(scroll_dy,
        0,
        child.min_size(frame.measure_text, Rect(box.width, 9999)).height - box.height
    )

    res = Result()
    res.set_data(set_state((container_id, scroll_dy)))
    # a.append(text("final:" + str(scroll_dy)))
    modified_child = vbox([child,], at_y=-scroll_dy)
    res.add_children_after([modified_child.render(frame, box)])
    return res

