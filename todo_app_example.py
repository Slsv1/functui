from node import *
from dataclasses import dataclass

@dataclass
class Task():
    text: str
    done: bool

tasks = [Task("example task", True), Task("example task 1", False)]

def task_widget(task: Task, selected: bool):
    return (background(Color.CYAN) if selected else empty) ** fill ** hbox_flex([
        no_flex ** text("[x]" if task.done else "[ ]"),
        no_flex ** text(" "),
        flex(1) ** (strike_through if task.done else empty) ** text(task.text)
    ])


def render_layout(user_selected_index: int):
    layout = border ** vbox_flex([
        flex(1) ** vbox([
            task_widget(task, user_selected_index == i) for i, task in enumerate(tasks)
        ])
    ])

    print(render_to_fit_terminal(layout))

selected_index = 0
while True:
    user_in = input()
    if user_in == "esc":
        break
    if user_in == "j":
        selected_index += 1
    elif user_in == "k":
        selected_index -= 1


    render_layout(selected_index)
