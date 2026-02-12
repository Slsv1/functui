from functui.classes import *
from functui.common import *
from functui.nav import ROOT_HORIZONTAL, ROOT_VERTICAL, InteractibleID, NavState, DEFAULT_NAV_BINDINGS, interaction_area
from functui.io.raw import terminal

import curses
from dataclasses import dataclass


@dataclass
class Model():
    nav: NavState

    # Add more attributes to contain all of your persistent state.


def update(input: InputEvent, res: Result, m: Model):
    # update NavState for keyboard and mouse interactivity.
    action = None
    if input.key_event in DEFAULT_NAV_BINDINGS:
        action = DEFAULT_NAV_BINDINGS[input.key_event]

    m.nav = m.nav.update(
        res=res,
        action=action, 
        nav_tree=[],
        mouse_position=input.mouse_position_event
    )

    # Put your update code here.

    # Create your keyboard navigation tree here.


def view(m: Model):
    # Layout rendering code here.
    layout = vbox([
        text("Hello World!") | border,
        text("Press ctrl+c to exit.") | fg(Color4.CYAN) | border,
    ])
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

