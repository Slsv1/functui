import blessed
from textui import *


def selectable(state: AppState, id: InteractibleID, data: Node):
    return state.interaction(id) ** shrink\
    ** ( combine(fg(Color.CYAN), border, no_style) if state.is_active(id) else border )** data

def status_bar(state: AppState, id: InteractibleID):
    id = id.with_direction(Direction.HORIZONTAL)

    return bg(Color.BLACK) ** fill ** hbox_flex([
        no_flex ** bg(Color.RED) ** hbox([text("Bar")]),
        flex ** nothing(),
        no_flex **state.interaction(id.child(0))\
            ** (bg(Color.CYAN) ** text("j") if state.is_active(id.child(0)) else text("x")),
        no_flex **state.interaction(id.child(1))\
            ** (bg(Color.CYAN) ** text("お") if state.is_active(id.child(1)) else text("x")),
    ])

def get_layout(state: AppState, root: InteractibleID):
    return vbox_flex([
        flex ** vbox([
            selectable(state, root.child(0), text("おはよう")),
            selectable(state, root.child(1), text("hej")),
            selectable(state, root.child(2), static_box([
                fill_char(".") ** nothing(),
                text("うう\nうう"),
                offset(1, 0) ** text("お"),
            ])),
        ]),
        no_flex ** status_bar(state, root.child(3))
    ])

state = AppState()
blessed_loop(
    blessed,
    state,
    lambda: get_layout(state, root_vertical),
    # Rect(5, 1)
)
