import blessed
from textui import _offset_render
from textui import *


def selectable(data: Node, state: NavState, id: InteractibleID):
    return state.interaction(id) ** shrink\
    ** ( combine(fg(Color.CYAN), border, no_style) if state.is_active(id) else border )** data

def status_bar(state: NavState, id: InteractibleID):
    id = id.with_attributes(direction=Direction.HORIZONTAL)

    return bg(Color.BLACK) ** bg_fill ** hbox_flex([
        no_flex ** bg(Color.RED) ** hbox([text("Bar")]),
        flex ** nothing(),
        no_flex ** state.interaction(id.child(0))\
            ** (bg(Color.CYAN) ** text("j") if state.is_active(id.child(0)) else text("x")),
        no_flex ** state.interaction(id.child(1))\
            ** (bg(Color.CYAN) ** text("お") if state.is_active(id.child(1)) else text("x")),
    ])

# def get_layout(state: NavState, root: InteractibleID):
#     return border ** bg_fill_char(".") ** vbox_flex([
#         flex ** vbox([
#             selectable(state, root.child(0), text("おはよう")),
#             # selectable(state, root.child(0), text("hej🙂")),
#             selectable(state, root.child(1), text("hej🙂")),
#             selectable(state, root.child(2), text("hej\nhej")),
#             selectable(state, root.child(3), static_box([
#                 text("うう\nうう"),
#                 offset(1, 0) ** text("h")#text("お"),
#             ])),
#             selectable(state, root.child(4), text("hej\nhej")),
#         ]),
#         no_flex ** status_bar(state, root.child(5))
#     ])
def get_layout(state, root):
    # print(_offset_render.cache_info())
    return offset(0, 0) ** border ** vbox_flex([
        no_flex ** vbox(nav([
            partial(selectable, text("hej hej")),
            partial(selectable, text("hej hej")),
        ], state, root.child(0))),
        flex ** border ** vbox_scroll(state, root.child(1), [
            partial(selectable, adaptive_text(LOREM)),
            partial(selectable, adaptive_text(LOREM)),
            # partial(selectable, adaptive_text(LOREM)),
            # partial(selectable, adaptive_text(LOREM)),
            # partial(selectable, adaptive_text(LOREM)),
            # partial(selectable, adaptive_text(LOREM + "おお おおおおおおおお おおおお")),
            # partial(selectable, text("hej")),
            # partial(selectable, text("hej")),
            # partial(selectable, text("hej")),
            # partial(selectable, text("hej")),
            # partial(selectable, text("hej")),
            # partial(selectable, text("hej, おお\nお")),
        ]),
        no_flex ** status_bar(state, root.child(2))
    ])
state = NavState()
blessed_loop(
    blessed,
    state,
    lambda: get_layout(state, root_vertical),
    Rect(70, 40)
)
