from functui.classes import *
from functui.common import *
from functui.flex import hbox_flex_wrap, hbox_flex, flex, flex_custom
from functui.text_wrapping import adaptive_text
from functui import result_to_str
from functui.io.html import result_to_html_str
from functui.common import custom_border, _border_render
from color import result
from functools import lru_cache, partial

result = layout_to_result(Rect(20, 15), hbox_flex_wrap([
    text("hej") | border | shrink,
    text("hej\nhej") | border,
    text("hej") | border | flex_custom(basis=True),
    text("hejddddddddddddddddd") | border,
    text("hej") | border | flex_custom(basis=True),
    text("hej") | border,
    text("hej") | border | flex_custom(basis=True),
    text("hej") | border | flex_custom(basis=True),
    text("hej") | border,
    # text("hej") | border,
]) | border | bg_char("."))

print(result_to_str(result))

