from functui import Rect, layout_to_result
from functui.flex import flex, flex_custom, hbox_flex_wrap, hbox_flex, vbox_flex
from functui.common import *
from functui.classes import *
from functui.io.ansi import result_to_str
from functui.io.html import result_to_html_str
from functui.canvas import plot, PlotXY
from itertools import batched

from functui.text_wrapping import adaptive_text
import math


def display_char_styles():
    out = []
    for i in StyleAttr:
        out.append(text(i.name) | push_rule(StyleRule(add_attrs=i)))
    return hbox(intersperse(out, text(" ")))

def cell_white_text(color8: int):
    return text(f"{color8: >3}") | padding | bg_fill | bg(color8) | fg(Color4.BRIGHT_WHITE)
def cell_black_text(color8: int):
    return text(f"{color8: >3}") | padding | bg_fill | bg(color8) | fg(16)

def display_color_8():
    light_cube = []
    dark_cube = []
    for i in range(16, 232):
        if ((i+2) % 36) < 18:
            light_cube.append(
                cell_black_text(i)
            )
        else:
            dark_cube.append(
                cell_white_text(i)
            )
    return vbox([
        *(hbox(row) for row in batched(dark_cube, 6*3)),
        *(hbox(row) for row in batched(light_cube, 6*3)),
    ])


def title(c: Layout):
    return static_box([
        hbar,
        c | bold | offset(x=1) | shrink,
    ]) | custom_padding(top = 1, bottom = 0)

def flex_item(string: str):
    return text(string) | center | custom_padding(1, 1, 1, 1)
def flex_itemw(string: str):
    return text(string) | center | custom_padding(1, 1, 1, 1)

layout = vbox_flex([
    hbox_flex([
        vbox([
            text("4 bit") | fg(Color4.GREEN),
            text("8 bit") | fg(45),
            text("True\ncolor") | fg(Color4.BRIGHT_RED),

        ]) | padding | flex,
        display_color_8()
    ]) | border_with_title(text("Colors")),
    display_char_styles() | border_with_title(text("Styles")),
    hbox_flex([
        vbox_flex([
            hbox_flex(intersperse([
                flex_item("flex") | flex,
                flex_item("flex_custom(2)") | flex_custom(2),
                flex_item("no flex"),
            ], sep=vbar)) | border_with_title(text("Flexible Containers")),
            adaptive_text(LOREM) | padding | dim | border_with_title(text("Text wrapping")) | flex,
        ]) | flex,
        hbox_flex_wrap(
            [(text("flex") | custom_padding(1, 1, 1, 1) | styled(border, rule_fg(i+0)) | flex_custom(1, basis=True)) for i in range(10)]
        )| border_with_title(text("Flexible and Wrappable Containers")) | flex,
    ]) | flex,
    plot(
        PlotXY(x=range(100), y=tuple([math.sin(i/2)+1 for i in range(100)]),style=rule_fg(Color4.BRIGHT_RED))
    ) | min_height(5) | border_with_title(text("Braille Ploting"))
])

result = layout_to_result(layout, Rect(102, 45))
print(result_to_str(result))
