from functui.classes import *
from functui.common import *
from functui.flex import hbox_flex, flex
from functui.nav import ROOT_HORIZONTAL, ROOT_VERTICAL, InteractibleID, NavState, DEFAULT_NAV_BINDINGS, interaction_area
from functui.io.raw import terminal

import curses
from dataclasses import dataclass, field



@dataclass
class Model():
    nav: NavState
    keycodes: list[str] = field(default_factory=list)
    mouse_positions: list[Coordinate] = field(default_factory=list)


def update(input: InputEvent, res: Result, m: Model):
    action = None
    if input.key_event in DEFAULT_NAV_BINDINGS:
        action = DEFAULT_NAV_BINDINGS[input.key_event]

    m.nav = m.nav.update(
        res=res,
        action=action, 
        nav_tree=[],
        mouse_position=input.mouse_position_event
    )

    if input.key_event is not None:
        m.keycodes.append(input.key_event)
    if input.mouse_position_event is not None:
        m.mouse_positions.append(input.mouse_position_event)

    if len(m.keycodes) > 50:
        del m.keycodes[0]
    if len(m.mouse_positions) > 50:
        del m.mouse_positions[0]

def view(m: Model):
    layout = hbox_flex([
        vbox(
            [text(f"<{i}>") | padding for i in m.keycodes],
            reverse=True
        ) | border_with_title(text("[key event]") | center) | flex,
        vbox(
            [text(f"<{repr(i)}>") | padding for i in m.mouse_positions],
            reverse=True
        ) | border_with_title(text("[mouse position event]") | center)| flex,
    ]) | padding
    return layout


m = Model(
    nav = NavState(),
)


with terminal() as term:
    while True:
        # render
        res = layout_to_result(view(m), term.get_terminal_size())
        term.display_result(res)

        # wait for input
        event = term.block_untill_input()

        # update
        if event.key_event == "ctrl+c":
            break
        update(event, res, m)
