import dataclasses
from functools import cache, lru_cache, partial
from textui import *
from textui import _border_render
from dataclasses import dataclass
from typing import Callable

def get_layout():
    return vbox_flex([
        flex ** vbox([
            border ** text("hej"),
            border ** text("hej")
        ]),
        no_flex ** bg(Color.BLACK) ** fill ** hbox_flex([
            no_flex ** bg(Color.CYAN) ** hbox([text("Bar")]),
            flex ** nothing(),
            no_flex ** text("hej hej")
        ])
    ])

string, result = render(20, 10, get_layout(), end=False)
print(string)


