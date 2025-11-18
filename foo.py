from functui import Rect, layout_to_str
from functui.common import *
layout = static_box([
    text("first") | border | shrink,
    text("second") | border | shrink | offset(1, 2)
]) | border
print(layout_to_str(layout, Rect(10, 8)))
