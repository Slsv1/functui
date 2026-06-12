# TODO

# documentation
#
# text jusitication 
# word wrapping
#
# simple grid layout
#
# change to using pipes
import sys
from functui import *
from functui.common import *
from functui.classes import *
from functui.flex import vbox_flex, flex
from functui.textfield import create_text_input_event, default_text_input_bindings, TextInput, start_text_input
from functui.rich_text import adaptive_text
from functui.nav import DEFAULT_NAV_BINDINGS, NavContainer, NavState, hoverable, v_scroll, v_resizable_split, vnav, hnav
from functui.io.raw import terminal
from dataclasses import dataclass
from enum import Enum, auto
from types import SimpleNamespace
from typing import Iterable

#
# Data
#

class NodeIds(Enum):
    BUTTON_CREATE = auto()
    BUTTON_COMPLETE = auto()
    BUTTON_DELETE = auto()
    BUTTON_EDIT = auto()
    CONTAINER_TASKS = auto()
    TASK = auto()

@dataclass(frozen=True, eq=True)
class Task():
    description: str
    done: bool

class Colors(SimpleNamespace):
    was_active = Color4.CYAN
    active = Color24(50, 100, 200)
    done = Color4.GREEN

@dataclass
class Model():
    nav: NavState
    tasks: list[Task]
    selected_task_index: int
    tasks_ids: list[NodeId]
    nav_tree: NavContainer | None = None
    current_text_input: TextInput | None = None

def get_border_rule(nav: NavState, id: NodeId):
    return StyleRule(
        fg=Colors.active if nav.is_hovered(id) else None,
        bg=Colors.active if nav.is_active(id) or nav.is_held_down(id) else None
    )

tasks = [
    Task(LOREM, False),
    Task("おはよう", False),
    Task("Sample Task 2", True)
]


#
# Logic
#

def update(input: InputEvent, res: ResultData, m: Model):

    if m.current_text_input is not None:
        if event := create_text_input_event(input.key_event):
            m.current_text_input = m.current_text_input.update(event)
    else:
        action = None
        if input.key_event in DEFAULT_NAV_BINDINGS:
            action = DEFAULT_NAV_BINDINGS[input.key_event]

        m.nav = m.nav.update(res, action, m.nav_tree, input.mouse_position_event)


    for index, task_id in enumerate(m.tasks_ids):
        if m.nav.is_selected(task_id):
            m.selected_task_index = index


    if len(m.tasks):
        if m.nav.is_selected(NodeIds.BUTTON_DELETE):
            del m.tasks[m.selected_task_index]
            m.selected_task_index = 0


        if m.nav.is_selected(NodeIds.BUTTON_COMPLETE):
            task = m.tasks[m.selected_task_index]
            m.tasks[m.selected_task_index] = Task(task.description, True)

        if m.nav.is_selected(NodeIds.BUTTON_EDIT):
            task = m.tasks[m.selected_task_index]
            if m.current_text_input is None:
                m.current_text_input = start_text_input(task.description)
            elif m.current_text_input.submited:
                m.tasks[m.selected_task_index] = Task(m.current_text_input.value, task.done)
                m.current_text_input = None

    if m.nav.is_selected(NodeIds.BUTTON_CREATE):
        m.tasks.append(Task("New Task", False))

    # Keyboard navigation


    # continers
    m.tasks_ids = [(NodeIds.TASK, i) for i, _ in enumerate(tasks)]

    # buttons
    m.nav_tree = hnav(
        vnav(*m.tasks_ids, remember=True),
        vnav(
            NodeIds.BUTTON_DELETE,
            NodeIds.BUTTON_COMPLETE,
            NodeIds.BUTTON_EDIT,
            NodeIds.BUTTON_CREATE,
            remember=True,
        ) if m.tasks_ids else hnav(
            NodeIds.BUTTON_CREATE
        )
    )

#
# Visual
#

def button(id, nav: NavState):
    return combine(styled(border, get_border_rule(nav, id)), hoverable(id))

def item(item, m: Model, id, nav: NavState):
    return adaptive_text(item.description)\
        | padding\
        | (combine(strike_through, fg(Colors.done)) if item.done else empty)\
        | styled(border, get_border_rule(nav, id))\
        | clamp_height(5)\
        | (fg(Colors.was_active) if m.tasks[m.selected_task_index] is item else empty)\
        | hoverable(id)


def view(m: Model):
    nav = m.nav
    text_widget = nothing()
    if m.current_text_input is not None:
        text_widget = adaptive_text(m.current_text_input.view_as_span())\
            | bg_fill\
            | border_with_title(text("Input") | center, border_double)\
            | custom_padding(2, 2, 2, 2)\
            | center

    return static_box([
        v_resizable_split(
            nav=m.nav,
            node_id="resizable-split",
            left=vbox([item(task, m, id, nav) for id, task in zip(m.tasks_ids, m.tasks)]) | v_scroll(
                container_id="task-container",
                children=m.tasks_ids,
                nav=nav,
            ) | border_with_title(text(" [Items] ") | bold | center, border_thick),

            right=vbox_flex([
                (vbox_flex([
                    adaptive_text(m.tasks[m.selected_task_index].description)\
                        | padding | flex,
                    text("delete") | center | fg(Color4.RED) | button(NodeIds.BUTTON_DELETE, nav),
                    text("complete") | center | fg(Color4.GREEN) | button(NodeIds.BUTTON_COMPLETE, nav),
                    text("edit") | center | button(NodeIds.BUTTON_EDIT, nav),
                ]) if m.tasks else text("There are no tasks") | center) \
                    | border_with_title(text(" [Properties] ") | center | bold, border_thick)\
                    | flex,

                text("New Task") | center | button(NodeIds.BUTTON_CREATE, nav),
            ]),
        ),
        text_widget
    ]) | bg_fill

# adaptive_styled_text([
#     "hejsan", styled("hehejsan", fg=Color.RED), "hej hej hej"
# ], Justify.CENTER, cursor_at_position=49, cursor_pixel=Pixel())

m = Model(
    nav=NavState(),
    tasks=tasks,
    selected_task_index=1,
    tasks_ids=[],
)

with terminal() as term:
    while True:
        # render
        res = layout_to_result(view(m), term.get_terminal_size())
        term.display_layout(res)

        # wait for input
        event = term.block_until_input()

        # update
        if event.key_event == "ctrl+c":
            break
        update(event, res.data, m)

