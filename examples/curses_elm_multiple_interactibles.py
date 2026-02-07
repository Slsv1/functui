from functui.classes import *
from functui.common import *
from functui.nav import ROOT_HORIZONTAL, ROOT_VERTICAL, InteractibleID, NavState, default_nav_bindings, interaction_area
from functui.io.curses import get_input_event, draw_result, wrapper

import curses
from dataclasses import dataclass


@dataclass
class Model():
    nav: NavState
    button_1: InteractibleID
    button_2: InteractibleID


def update(input: InputEvent, res: Result, m: Model):
    action = None
    if input.key_event in default_nav_bindings:
        action = default_nav_bindings[input.key_event]

    m.nav = m.nav.update(
        res=res,
        action=action, 
        nav_data=[m.button_1, m.button_2],
        mouse_position=input.mouse_position_event
    )


# If you want ui nodes to be reusable, put them into a function.
def selectable_element(nav: NavState, id: InteractibleID, string: str):
    return text(string) | styled(
        border,
        (rule_fg(Color4.BLUE) if m.nav.is_hover(id) else StyleRule()) | (rule_bg(Color4.BLUE) if m.nav.is_active(id) else StyleRule())
    ) | interaction_area(id)



def view(m: Model):
    layout = vbox([
        selectable_element(m.nav, m.button_1, "Hello"),
        selectable_element(m.nav, m.button_2, "World"),
    ]) | border
    return layout


root = ROOT_VERTICAL

# for interactible ids that never change it is possible to define them when model is first created.
m = Model(
    nav = NavState(),
    button_1 = root.child(0),
    button_2 = root.child(1),
)


def main(stdscr: curses.window):
    while True:
        y, x = stdscr.getmaxyx()
        res = layout_to_result(view(m), Rect(x-1, y-1))
        draw_result(res, stdscr)

        key: InputEvent = get_input_event(stdscr)
        if key.key_event == 'ctrl+c':
            break
        update(key, res, m)
if __name__ == "__main__":
    wrapper(main)
