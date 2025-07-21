import dataclasses
from functools import cache, lru_cache, partial
from textui import *
from textui import _border_render
from dataclasses import dataclass
from typing import Callable

# print(render(20, 20, border ** border ** adaptive_text(LOREM)))
# print(render(20, 20, border ** border ** adaptive_text(LOREM)))
# print(render(100, 20,\
#     border ** vbox_flex([
#         flex ** border ** adaptive_text(LOREM),
#         no_flex ** hbar(),
#         flex ** text("hej")
#     ])
# ))
print(render(100, 20,\
    border ** vbox_flex([
        flex ** fg(Color.RED) ** border ** adaptive_text(LOREM),
        no_flex ** hbar(),
        flex ** border ** hbox_flex([
             flex_custom(2, 0) ** text("hejsan"),
             no_flex ** shrink ** vbar(),
             flex ** text("hejs\nhej"),
        ])
    ])
))
print(_border_render.cache_info())

