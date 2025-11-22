from functui import Rect, layout_to_str
from functui.common import border, text
from functui.flex import flex, flex_custom, hbox_flex
layout = hbox_flex([
    text("basis and grow") | border | flex_custom(grow=1, basis=True),
    text("grow") | border | flex, # flex is same as flex_custom(grow=1)
]) | border
print(layout_to_str(layout, Rect(40, 5)))
