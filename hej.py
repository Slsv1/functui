import dataclasses
from functools import cache, lru_cache, partial
from textui import render, text, border, _border_render, _text_render, Node, combine, adaptive_text, _adaptive_text_render, LOREM
from dataclasses import dataclass
from typing import Callable

print(render(20, 20, adaptive_text(LOREM)))
print(render(20, 20, adaptive_text(LOREM)))

print(_text_render.cache_info())
print(_border_render.cache_info())


