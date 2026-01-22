from functui.classes import *
from functui.common import *
from functui import result_to_str
from functui.io.html import result_to_html_str
from functui.common import custom_border, _border_render
from color import result
from functools import lru_cache, partial

result = layout_to_result(Rect(10, 10),vbox([
    text("hej") | fg(2) | offset(x=2) | border | shrink,
    text("gg") | bg_char("x")| offset(x=2) | bg_char(".") | border | shrink
]))

print(result_to_str(result))

