# TODO

# documentation
#
# text jusitication 
# word wrapping
#
# simple grid layout
#
# change to using pipes








import blessed
from functui import *
from functui.common import *
from functui.textfield import blessed_text_input_action
from functui.text_wrapping import adaptive_text
from functui.nav import blessed_nav_action
from functui.interactible import vbox_scroll
from dataclasses import dataclass
from enum import Enum, auto
from types import SimpleNamespace

#
# Data
#

@dataclass(frozen=True, eq=True)
class Task():
    description: str
    done: bool


class Colors(SimpleNamespace):
    was_active = Color.CYAN
    active = Color.BLUE
    done = Color.GREEN

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


tasks = [
    Task(LOREM, False),
    Task("おはよう", False),
    Task("Sample Task 2", True)
]


#
# Logic
#

def update(res: Result, m: Model):
    input_val = term.inkey()

    if m.current_text_input is not None:
        m.current_text_input = m.current_text_input.update(blessed_text_input_action(input_val))
    else:
        action = blessed_nav_action(input_val)
        m.nav = m.nav.update(res, action, m.nav_data)

    for index, task_id in enumerate(m.tasks_ids):
        if m.nav.is_active(task_id):
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
    return styled(border, Style(fg=Colors.active if nav.is_active(id) else None))

def item(item, id, nav: NavState):
    return adaptive_text(item.description)\
        | (combine(strike_through, fg(Colors.done)) if item.done else empty)\
        | styled(border, Style(fg=Colors.active if nav.is_active(id) else None))\
        | clamp_height(5)\
        | (fg(Colors.was_active) if nav.was_active(id) else empty)\


def view(m: Model):
    nav = m.nav
    text_widget = nothing()
    if m.current_text_input is not None:
        text_widget = adaptive_text(m.current_text_input.value)\
            | border_with_title(text("Input") | center)\
            | center

    return static_box([
        hbox_flex([
            vbox_scroll(
                state=nav,
                key=m.tasks_container,
                children=[(id, item(task, id, nav)) for id, task in zip(m.tasks_ids, m.tasks)],
            ) | border_with_title(text(" [Items] ") | bold | center) | flex,
            vbox_flex([
                (vbox_flex([
                    adaptive_text(m.tasks[m.selected_task_index].description) | no_flex,
                    nothing() | flex,
                    text("delete") | center | fg(Color.RED) | button(m.delete_button, nav) | no_flex,
                    text("complete") | center | fg(Color.GREEN) | button(m.complete_button, nav) | no_flex,
                    text("edit") | center | button(m.edit_button, nav) | no_flex,
                ]) if m.tasks else text("There are no tasks") | center) \
                | border_with_title(text(" [Properties] ") | center | bold)\
                | flex,
                text("New Task") | center | button(m.create_button, nav) | no_flex,
            ]) | flex
        ]),
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
term = blessed.Terminal()
with term.cbreak():
    while True:
        res = layout_to_result(Rect(80, 40), view(m))
        with term.location():
            print(result_to_str(res))
        update(res, m)
