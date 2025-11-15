from .nav import *
from .classes import *
from .default_elements import *
from typing import NamedTuple

# class _VboxRenderParams(NamedTuple):
#     child_nodes: list[Node]
#     at_y: int
#     start: float
#     showing: float
#     state: NavState
#     key: InteractibleID

# def no_scrollbar(p: _VboxRenderParams):
#     return vbox([
#
#     ])


UNLIMITED_SPACE = 2 ** 16
def vbox_scroll(
        state: NavState,
        key: InteractibleID,
        children: Iterable[tuple[InteractibleID, Layout]],
        # scroll_bar_key: InteractibleID = EMPTY_INTERACTIBLE,
        # render=lambda,
        # scroll_bar: Callable[[_VboxRenderParams], Node] = lambda start, showing, state, key: nothing()# (fg(Color.CYAN) if state.is_active(key) else empty)** v_scroll_bar(start, showing),
    ):

    child_nodes = []
    selected_index = None
    direction_down = True if state.action == NavAction.NAV_DOWN else False

    for i, (id, node) in enumerate(children):
        child_nodes.append(node)
        if state.is_active(id):
            selected_index = i
    # we need a custom node here so that we can get the available_height

    return Layout(
        func=vbox_scroll,
        min_size=min_size_vertical([i.min_size for i in child_nodes]),
        render=partial(_vbox_scroll_render, key, tuple(child_nodes), selected_index, direction_down, state.try_state(key, int))
    )
def _vbox_scroll_render(
        key: InteractibleID,
        child_nodes: tuple[Layout],
        selected_index: int | None,
        direction_down: bool,
        last_at_y: int | None,
        frame: Frame, 
        box: Box
):
    available_height = box.height
    content_height = vbox(child_nodes)\
        .min_size(frame.measure_text, Rect(box.width-1, UNLIMITED_SPACE)).height
    # decide at_y

    if selected_index is not None:
        # selected at y is at what y coordinate the selected child starts
        # desired at y is where the at_y var needs to be so that the childs end is included at the bottom of the box
        selected_at_y_end = vbox(child_nodes[:selected_index+1])\
            .min_size(frame.measure_text, Rect(box.width-1, UNLIMITED_SPACE)).height
        desired_at_y_end = selected_at_y_end-available_height if (selected_at_y_end-available_height) > 0 else 0
        # pick beggining
        desired_at_y_beggining = vbox(child_nodes[:selected_index])\
            .min_size(frame.measure_text, Rect(box.width-1, UNLIMITED_SPACE)).height
        desired_at_y = desired_at_y_end if direction_down else desired_at_y_beggining


        if (last_at_y is not None) and (last_at_y < desired_at_y_beggining) and (selected_at_y_end <= (last_at_y + box.height)):
            at_y = last_at_y
        else:
            at_y = desired_at_y

    elif last_at_y is not None:
        at_y = last_at_y
    else:
        at_y = 0

    # render

    if content_height != 0:
        percent_available = available_height / content_height
        percent_progress = at_y/content_height
    else:
        percent_available = 1
        percent_progress = 0

    layout = vbox(child_nodes, at_y = -at_y)
    # layout = hbox_flex([
    #     flex ** vbox(child_nodes, -at_y),
        # no_flex ** state.interaction_area(scroll_bar_key)\
        #     ** scroll_bar(percent_progress, percent_available, state, scroll_bar_key)
            #   ** (fg(Color.CYAN) if state.is_active(scroll_bar_key) else fg(Color.RED))\
            # (v_scroll_bar(percent_progress, percent_available))
    # ])
    res = Result()
    res.set_data(set_state((key, at_y)))
    res.add_children_after([layout.render(frame, box)])
    return res
