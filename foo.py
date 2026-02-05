from functui.classes import *
from functui.common import *
from functui.io.html import layout_to_html_str

style_rule = StyleRule(
    fg=Color4.BRIGHT_YELLOW,
    bg=rgb(10, 134, 143),
    add_attrs=StyleAttr.ITALIC | StyleAttr.BOLD
)

# now with bg_fill node
layout = text("styled_text") | bg_fill | push_rule(style_rule) | border

print(layout_to_html_str(layout, Rect(20, 3)))
