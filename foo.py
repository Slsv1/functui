from functui import Rect, layout_to_str
from functui.common import border, text
from functui.flex import flex, hbox_flex
layout = hbox_flex([
    text("Flex.") | border | flex,
    text("No flex.") | border,
]) | border
print(layout_to_str(layout, Rect(40, 5)))
