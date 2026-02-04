from functui import Rect, layout_to_str, rule_fg, rgb
from functui.common import *

from functui.io.html import layout_to_html_str
style_rule = rule_fg(rgb(0, 255, 255))

layout = text("This text is not styled.\nBut the border around it is.")\
    | styled(border, style_rule)

print(layout_to_html_str(layout, Rect(30, 4)))
