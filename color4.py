from functui.classes import *
from functui.common import *
from functui.io.ansi import layout_to_str, result_to_str
from functui.io.html import result_to_html_str

def main():
    items = []
    bright_items = []
    for i in Color4:
        if i.name.startswith("BRIGHT"):
            bright_items.append(text(i.name) | bg_fill | bg(i) | fg(16))
        else:
            items.append(text(i.name) | bg_fill | bg(i) | fg(Color4.BRIGHT_WHITE))
    layout = hbox([
        vbox(items) | shrink,
        text(" "),
        vbox(bright_items) | shrink,
    ]) | padding
    res = layout_to_result(layout, Rect(26, 20))
    print(result_to_html_str(res))

if __name__ == "__main__":
    main()

