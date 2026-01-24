from functui.classes import *
from functui.common import *
from functui.text_wrapping import adaptive_text
from functui import result_to_str
from functui.io.html import result_to_html_str
from functui.common import custom_border, _border_render
from color import result
from functools import lru_cache, partial

result = layout_to_result(Rect(80, 20),hbox_flex([
    text("hej") | no_flex,
    adaptive_text(LOREM) | border | flex,
    adaptive_text(LOREM) | border | flex
]) | border | shrink_x | bg_char("."))

print(result_to_str(result))

