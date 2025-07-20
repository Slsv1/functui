import dataclasses
from functools import cache, lru_cache, partial
from textui import render, text, border, _border_render, _text_render, Node
from dataclasses import dataclass
from typing import Callable



print(render(10, 10, border ** border ** text("hej")))
print(render(10, 10, border ** border ** text("hej")))
print(render(10, 10, border ** border ** text("hej")))
print(render(10, 10, border ** text("hej")))

print(_text_render.cache_info())
print(_border_render.cache_info())


