from functui.classes import *
from functui.common import *
from functui.flex import hbox_flex_wrap, hbox_flex, flex, flex_custom
from functui.interactible import v_scroll
from functui.nav import ROOT_HORIZONTAL, ROOT_VERTICAL, InteractibleID, NavState, default_nav_bindings
from functui.text_wrapping import adaptive_text
from functui import result_to_str
from functui.io.curses import get_input_event, draw_result, wrapper
from functui.common import custom_border, _border_render
from color import result
from functools import lru_cache, partial

import curses

@dataclass
class Model():
    nav: NavState
    button_1: InteractibleID
    button_2: InteractibleID

def update(input: InputEvent, res: Result, m: Model):
    action = None
    if input.key_event in default_nav_bindings:
        action = default_nav_bindings[input.key_event]
    m.nav = m.nav.update(res, action, [m.button_1, m.button_2])

def view(m: Model):
    nav = m.nav
    layout = vbox([
        text("hej1") | styled(
            border,
            rule_fg(Color4.BLUE) if m.nav.is_active(m.button_1) else StyleRule()
        ),
        text("hej2") | styled(
            border,
            rule_fg(Color4.BLUE) if m.nav.is_active(m.button_2) else StyleRule()
        ),
    ]) | v_scroll(ROOT_VERTICAL, nav)
    return layout

root = ROOT_VERTICAL

m = Model(
    nav = NavState(),
    button_1 = root.child(0),
    button_2 = root.child(1),
)
def main(stdscr: curses.window):
    while True:
        y, x = stdscr.getmaxyx()
        res = layout_to_result(Rect(x-1, y-1), view(m))
        stdscr.erase()
        draw_result(res, stdscr)

        key: InputEvent = get_input_event(stdscr)  # Get a single key press
        if key.key_event == 'ctrl+c':
            break
        update(key, res, m)
wrapper(main)
