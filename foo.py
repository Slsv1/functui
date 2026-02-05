from functui.classes import *
from functui.common import *
from functui.io.ansi import layout_to_str
from functui.io.html import layout_to_html_str
from functui.rich_text import rich_text, span, adaptive_text


# now with bg_fill node
layout = rich_text("    styled_t", span("hej", span("d", rule=rule_bold), "h\nejsan", rule=rule_fg(Color4.RED)), "ext\nddf\n\n df") | border

print(layout_to_str(layout, Rect(20, 10)))
