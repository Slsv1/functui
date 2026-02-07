from functui.flex import *
from functui.common import *
from functui.classes import *
from functui.rich_text import adaptive_text
from functui.io.ansi import layout_to_str

layout = hbox_flex([
    adaptive_text("foo foo foo foo") | border_ascii | shrink_y | flex,
    adaptive_text("bar bar bar bar bar bar bar") | border_ascii | shrink_y | flex_custom(2),
])
print(layout_to_str(layout, Rect(20, 10)))

