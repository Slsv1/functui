import blessed
from component import visualise_nav_data
from textui import *
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


class Style(SimpleNamespace):
    was_active = Color.CYAN
    active = Color.BLUE
    done = Color.GREEN

@dataclass
class Model():
    state_machine: StateMachine
    nav_state: NavState
    tasks: list[Task]
    selected_task_index: int
    tasks_ids: Iterable[InteractibleID]
    nav_data: list[InteractibleID]
    delete_button: InteractibleID = EMPTY_INTERACTIBLE
    complete_button: InteractibleID = EMPTY_INTERACTIBLE
    create_button: InteractibleID = EMPTY_INTERACTIBLE
    edit_button: InteractibleID = EMPTY_INTERACTIBLE
    tasks_container: InteractibleID = EMPTY_INTERACTIBLE


tasks = [
    Task(LOREM, False),
    Task("Sample Task", True),
    Task("Sample Task 2", True)
]


#
# Logic
#

def update(res: Result, m: Model) -> Model:

    # Input

    nav = m.nav_state
    if simple_text_input := m.state_machine.try_state(SimpleTextInput):
        action = blessed_get_input_text(term)
        if action == Action.DESELECT:
            m.state_machine.queue_next_state(None)
        else:
            m.state_machine.queue_next_state(simple_text_input.step(action)) # type: ignore
    else:
        action = blessed_get_input_default(term)
        nav = m.nav_state.step(res, action, m.nav_data)
    m.state_machine.switch_state()

    # Logic

    selected_task_index = m.selected_task_index
    for index, task_id in enumerate(m.tasks_ids):
        if nav.is_active(task_id):
            selected_task_index = index

    if len(m.tasks):
        if nav.is_active(m.delete_button) and action == Action.SELECT:
            del m.tasks[m.selected_task_index]
            selected_task_index = 0
    if nav.is_active(m.create_button) and action == Action.SELECT:
        m.tasks.append(Task("New Task", False))

    if nav.is_active(m.edit_button) and action == Action.SELECT:
        task = m.tasks[m.selected_task_index]
        m.state_machine.queue_next_state(SimpleTextInput(
            task.description, len(task.description)
        ))


    # Keyboard navigation

    nav_data = []
    root = ROOT_HORIZONTAL
    tasks_container = root.child(0, Direction.VERTICAL, persistent=True)

    # continers
    side_container = root.child(1, Direction.VERTICAL)
    info_container = side_container.child(0, Direction.VERTICAL)
    tasks_ids = [tasks_container.child(i) for i, _ in enumerate(tasks)]
    nav_data.extend(tasks_ids)

    # buttons
    if len(m.tasks):
        delete_button = info_container.child(0)
        nav_data.append(delete_button)
        complete_button = info_container.child(1)
        nav_data.append(complete_button)
        edit_button = info_container.child(2)
        nav_data.append(edit_button)
    else:
        complete_button = EMPTY_INTERACTIBLE
        delete_button = EMPTY_INTERACTIBLE
        edit_button = EMPTY_INTERACTIBLE

    create_button = side_container.child(1)
    nav_data.append(create_button)


    return Model(
        state_machine=m.state_machine,
        nav_state=nav,
        tasks=m.tasks,
        selected_task_index=selected_task_index,
        tasks_ids = tasks_ids,
        delete_button=delete_button,
        complete_button=complete_button,
        create_button=create_button,
        edit_button=edit_button,
        tasks_container=tasks_container,
        nav_data=nav_data
    )

#
# Visual
#

def button(id, nav: NavState):
    return combine(
        fg(Style.active) if nav.is_active(id) else empty,
        border,
        no_style,
    )

def item(item, id, nav: NavState):
    return empty\
        ** (fg(Style.was_active) if nav.was_active(id) else empty)\
        ** (fg(Style.active) if nav.is_active(id) else empty)\
        ** limit_height(5)\
        ** border\
        ** no_style\
        ** (combine(strike_through, fg(Style.done)) if item.done else empty)\
        ** adaptive_text(item.description)

def view(nav: NavState):
    text_widget = nothing()
    if text_input := m.state_machine.try_state(SimpleTextInput):
        text_widget = center\
            ** border_with_title(center ** text("Input"))\
            ** adaptive_text(text_input.acc)

    return static_box([
    hbox_flex([
        flex\
            ** border_with_title(center ** bold ** text("[Items]")) \
            ** vbox_scroll(
                state=nav,
                key=m.tasks_container,
                children=[(id, item(task, id, nav)) for id, task in zip(m.tasks_ids, m.tasks)],
            ),
        flex ** vbox_flex([
            flex\
                ** border_with_title(center ** bold ** text("[Properties]"))\
                ** (vbox_flex([
                    no_flex ** adaptive_text(m.tasks[m.selected_task_index].description),
                    flex ** nothing(),
                    no_flex ** button(m.delete_button, nav) ** fg(Color.RED) ** center ** text("delete"),
                    no_flex ** button(m.complete_button, nav) ** fg(Color.GREEN) ** center ** text("complete"),
                    no_flex ** button(m.edit_button, nav) ** center ** text("edit"),
                ]) if m.tasks else center ** text("There are no tasks")),
            no_flex\
                ** button(m.create_button, nav) ** center ** text("New Task")
        ])
    ]),
    text_widget
    ])



m = Model(
    state_machine=StateMachine(),
    nav_state=NavState(),
    tasks=tasks,
    selected_task_index=1,
    tasks_ids=[],
    nav_data=[],
)
term = blessed.Terminal()
with term.cbreak():
    while True:
        res = get_result(Rect(70, 40), view(m.nav_state))
        print(render_as_ansi_string(res))
        m = update(res, m)
