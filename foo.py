from functui.classes import *
from functui.common import *
from functui.rich_text import adaptive_text, rich_text, span
from functui.io.ansi import layout_to_str
from functui.io.html import layout_to_html_str


layout = adaptive_text(
    "Some of this ",
    span("text", rule=rule_fg(Color4.BRIGHT_RED)),
    " will be ",
    span("styled. ", rule=rule_italic),
    span(
        "Also, it is possible to ",
        span("nest",rule=rule_fg(Color4.BRIGHT_BLACK) | rule_bold),
        " spans!",
        rule=rule_bg(Color4.BLUE)
    )
) | border

print(layout_to_html_str(layout, Rect(20, 10)))
