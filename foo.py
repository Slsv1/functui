from functui import Rect, layout_to_str
from functui.common import *

layout = vbox([
    text("foo"),
    hbox([text("bar"), vbar(), text("buz")]) | border,
]) | border

print(layout_to_str(layout, Rect(20, 9)))
