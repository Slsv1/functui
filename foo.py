from functui.classes import *
from functui.common import *
from functui.io.html import result_to_html_str
from functui.common import custom_border, _border_render
from color import result
from functools import lru_cache, partial

# result = layout_to_result(Rect(10, 10), text("hej") | fg(Color4.YELLOW))
print(result_to_html_str(result))

