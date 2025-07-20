import dataclasses
from functools import cache, lru_cache, partial
from textui import *
from textui import _border_render
from dataclasses import dataclass
from typing import Callable

# print(render(20, 20, border ** border ** adaptive_text(LOREM)))
# print(render(20, 20, border ** border ** adaptive_text(LOREM)))
print(render(100, 15,\
    border ** vbox_flex([
        flex ** border ** adaptive_text(LOREM),
        no_flex ** hbar(),
        flex ** text("hej")
    ])
))
print(_border_render.cache_info())


