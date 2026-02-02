# TODO

# documentation
#
# text jusitication 
# word wrapping
#
# simple grid layout
#
# change to using pipes
import curses
import sys
from functui import *
from functui.common import *
from functui.classes import *
from functui.flex import flex_custom, hbox_flex, vbox_flex, flex
from functui.textfield import create_text_input_event, default_text_input_bindings
from functui.text_wrapping import adaptive_text
from functui.nav import default_nav_bindings, h_resizable_split, interaction_area, v_scroll
from functui.io.curses import wrapper, get_input_event, draw_result # type: ignore
from dataclasses import dataclass
from enum import Enum, auto
from types import SimpleNamespace
from typing import Iterable


#
# Data
#

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
    tasks_ids: Iterable[InteractibleID]
    nav_data: list[InteractibleID]
    current_text_input: TextInput | None = None
    delete_button: InteractibleID = EMPTY_INTERACTIBLE
    complete_button: InteractibleID = EMPTY_INTERACTIBLE
    create_button: InteractibleID = EMPTY_INTERACTIBLE
    edit_button: InteractibleID = EMPTY_INTERACTIBLE
    tasks_container: InteractibleID = EMPTY_INTERACTIBLE
    text_container: InteractibleID = EMPTY_INTERACTIBLE

def get_border_rule(nav: NavState, id: InteractibleID):
    return StyleRule(
        fg=Colors.active if nav.is_hover(id) else None,
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

def update(input: InputEvent, res: Result, m: Model):
    if m.current_text_input is not None:
        if event := create_text_input_event(input.key_event):
            m.current_text_input = m.current_text_input.update(event)
    else:
        event = input.key_event if input.key_event is not None else input.mouse_button_event
        action = None
        if event in default_nav_bindings:
            action = default_nav_bindings[event]

        m.nav = m.nav.update(res, action, m.nav_data, input.mouse_position_event)

    for index, task_id in enumerate(m.tasks_ids):
        if m.nav.is_selected(task_id):
            m.selected_task_index = index

    if len(m.tasks):
        if m.nav.is_selected(m.delete_button):
            del m.tasks[m.selected_task_index]
            m.selected_task_index = 0


        if m.nav.is_selected(m.complete_button):
            task = m.tasks[m.selected_task_index]
            m.tasks[m.selected_task_index] = Task(task.description, True)

        if m.nav.is_selected(m.edit_button):
            task = m.tasks[m.selected_task_index]
            if m.current_text_input is None:
                m.current_text_input = start_text_input(task.description)
            elif m.current_text_input.submited:
                m.tasks[m.selected_task_index] = Task(m.current_text_input.value, task.done)
                m.current_text_input = None
    if m.nav.is_selected(m.create_button):
        m.tasks.append(Task("New Task", False))

    # Keyboard navigation

    nav_data = []
    root = ROOT_HORIZONTAL
    m.tasks_container = root.child(0, Direction.VERTICAL, persistent=True)

    # continers
    side_container = root.child(1, Direction.VERTICAL)
    info_container = side_container.child(0, Direction.VERTICAL)
    m.tasks_ids = [m.tasks_container.child(i) for i, _ in enumerate(tasks)]
    nav_data.extend(m.tasks_ids)

    # buttons
    if len(m.tasks):
        m.delete_button = info_container.child(0)
        nav_data.append(m.delete_button)
        m.complete_button = info_container.child(1)
        nav_data.append(m.complete_button)
        m.edit_button = info_container.child(2)
        nav_data.append(m.edit_button)
        m.text_container = info_container.child(-1)
    else:
        m.complete_button = EMPTY_INTERACTIBLE
        m.delete_button = EMPTY_INTERACTIBLE
        m.edit_button = EMPTY_INTERACTIBLE

    m.create_button = side_container.child(1)
    nav_data.append(m.create_button)
    m.nav_data = nav_data

#
# Visual
#

def button(id, nav: NavState):
    return combine(styled(border, get_border_rule(nav, id)), interaction_area(id))

def item(item, m: Model, id, nav: NavState):
    return adaptive_text(item.description)\
        | padding\
        | (combine(strike_through, fg(Colors.done)) if item.done else empty)\
        | styled(border, get_border_rule(nav, id))\
        | clamp_height(5)\
        | (fg(Colors.was_active) if m.tasks[m.selected_task_index] is item else empty)\
        | interaction_area(id)


def view(m: Model):
    nav = m.nav
    text_widget = nothing()
    if m.current_text_input is not None:
        text_widget = adaptive_text(m.current_text_input.value)\
            | bg_fill\
            | border_with_title(text("Input") | center, border_double)\
            | custom_padding(2, 2, 2, 2)\
            | center

    return static_box([
        h_resizable_split(
            ROOT_HORIZONTAL.child(12323),
            nav,
            left=vbox([item(task, m, id, nav) for id, task in zip(m.tasks_ids, m.tasks)]) | v_scroll(
                container_id=m.tasks_container,
                nav=nav,
            ) | border_with_title(text(" [Items] ") | bold | center, border_thick),

            right=vbox_flex([
                (vbox_flex([
                    adaptive_text(m.tasks[m.selected_task_index].description)\
                        | padding\
                        | v_scroll(m.text_container, nav),
                    nothing() | flex,

                    text("delete") | center | fg(Color4.RED) | button(m.delete_button, nav),
                    text("complete") | center | fg(Color4.GREEN) | button(m.complete_button, nav),
                    text("edit") | center | button(m.edit_button, nav),
                ]) if m.tasks else text("There are no tasks") | center) \
                    | border_with_title(text(" [Properties] ") | center | bold, border_thick)\
                    | flex,

                text("New Task") | center | button(m.create_button, nav),
            ]),

        ),
        text_widget
    ])

# adaptive_styled_text([
#     "hejsan", styled("hehejsan", fg=Color.RED), "hej hej hej"
# ], Justify.CENTER, cursor_at_position=49, cursor_pixel=Pixel())

m = Model(
    nav=NavState(),
    tasks=tasks,
    selected_task_index=1,
    tasks_ids=[],
    nav_data=[],
)
def main(stdscr: curses.window):
    while True:
        y, x = stdscr.getmaxyx()
        res = layout_to_result(Rect(x-1, y-1), view(m))
        stdscr.erase()
        draw_result(res, stdscr)
        # stdscr.refresh()

        # sys.stdout.write(result_to_str(res))
        key: InputEvent = get_input_event(stdscr)  # Get a single key press
        if key.key_event == 'ctrl+c':
            break
        update(key, res, m)
wrapper(main)
