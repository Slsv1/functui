from functui.common import *
from functui.io.curses import wrapper, draw_result, get_input_event
from functui.text_wrapping import adaptive_text, span
from functui import Rect, layout_to_result, result_to_str, Color4
from itertools import batched
import curses

def cell_white_text(color8: int):
    return text(f"{color8: >3}") | padding | bg_fill | bg(color8) | fg(Color4.BRIGHT_WHITE)
def cell_black_text(color8: int):
    return text(f"{color8: >3}") | padding | bg_fill | bg(color8) | fg(16)


def display_char_style():
    out = []
    for i in StyleAttr:
        out.append(text(i.name) | push_rule(StyleRule(add_attrs=i)))
    return hbox(intersperse(out, text(" ")))


def display_color_8():
    regular = []
    intense = []
    light_cube = []
    dark_cube = []
    blacks = []
    whites = []
    for i in range(8):
        regular.append(
            cell_white_text(i)
        )
        intense.append(
            cell_black_text(i+8)
        )
    for i in range(16, 232):
        if ((i+2) % 36) < 18:
            light_cube.append(
                cell_black_text(i)
            )
        else:
            dark_cube.append(
                cell_white_text(i)
            )
    for i in range(232, 244):
        blacks.append(
            cell_white_text(i)
        )
        whites.append(
            cell_black_text(i+12)
        )
    return vbox([
        text("Regular and bright colors are rendered differently depending on terminal theme"),
        hbox([text("Regular:  "), *regular]),
        hbox([text("Bright:   "), *intense]),
        text(" "),
        text("Color Cube"),
        *(hbox(row) for row in batched(dark_cube, 6*3)),
        *(hbox(row) for row in batched(light_cube, 6*3)),
        text(" "),
        text("Color ramps, black and white intentionaly excluded"),
        hbox(blacks),
        hbox(whites),
    ])


def title(c: Layout):
    return static_box([
        hbar,
        c | bold | offset(x=1) | shrink,
    ]) | custom_padding(top = 1, bottom = 0)




layout = vbox([
    title(text("8 Bit Colors")),
    display_color_8() | shrink,
    title(text("Style Attributes")),
    display_char_style() | shrink,
    title(text("Special Characters")),
    vbox([
        text("Need to be escaped in HTML: < > & \" \'"),
        text("Wide Characters (will break border if assumed width of 1): 🥰, おはよう") | styled(border, rule_dim) | shrink,
    ])
]) | padding |shrink
result = layout_to_result(Rect(140, 40), layout)
if __name__ == "__main__":
    print(result_to_str(result))
# def main(stdscr):
#     y, x = stdscr.getmaxyx()
#     res = layout_to_result(Rect(x-1, y-1), layout)
#     draw_result(res, stdscr)
#     i = get_input_event(stdscr)
# wrapper(main)
