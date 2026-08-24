from functui.nodes import *
from functui import NavState, DEFAULT_NAV_BINDINGS, InputEvent, ResultData, Coordinate, open_terminal, render_fit_terminal, Screen

from dataclasses import dataclass, field



@dataclass
class Model():
    nav: NavState
    keycodes: list[str] = field(default_factory=list)
    mouse_positions: list[Coordinate] = field(default_factory=list)


def update(input: InputEvent, res: ResultData, m: Model):
    action = None
    if input.key_event in DEFAULT_NAV_BINDINGS:
        action = DEFAULT_NAV_BINDINGS[input.key_event]

    m.nav = m.nav.update(
        res=res,
        event=input, 
        nav_tree=None,
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
            [text(f"<{i}>") | hpadding for i in reversed(m.keycodes)],
        ) | border_with_title(text("[key event]") | center) | flex,
        vbox(
            [text(f"<{repr(i)}>") | hpadding for i in reversed(m.mouse_positions)],
        ) | border_with_title(text("[mouse position event]") | center)| flex,
    ]) | hpadding

    return layout


m = Model(
    nav = NavState(),
)


with open_terminal() as term:
    screen = Screen()
    while True:
        # render
        res = render_fit_terminal(term, screen, view(m))
        # wait for input
        event = term.wait_for_input()

        # update
        if event.key_event == "ctrl+c":
            break
        update(event, res, m)
