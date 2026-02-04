from functui.classes import *
from functui.common import *
from functui.nav import ROOT_HORIZONTAL, ROOT_VERTICAL, InteractibleID, NavState, default_nav_bindings, interaction_area
from functui.io.curses import get_input_event, draw_result, wrapper

import curses
from dataclasses import dataclass


@dataclass
class Model():
    nav: NavState

    # Add more attributes to contain all of your persistent state.


def update(input: InputEvent, res: Result, m: Model):
    # update NavState for keyboard and mouse interactivity.
    action = None
    if input.key_event in default_nav_bindings:
        action = default_nav_bindings[input.key_event]

    m.nav = m.nav.update(
        res=res,
        action=action, 
        nav_data=[],
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


def main(stdscr: curses.window):
    while True:
        y, x = stdscr.getmaxyx()
        res = layout_to_result(view(m), Rect(x, y))
        draw_result(res, stdscr)

        key: InputEvent = get_input_event(stdscr)
        if key.key_event == 'ctrl+c':
            break # exit program
        update(key, res, m)

if __name__ == "__main__":
    wrapper(main)
