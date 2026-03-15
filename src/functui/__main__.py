from functui.common import *
from functui.classes import *
from functui.rich_text import adaptive_text, span
from functui import Rect, layout_to_result, result_to_str, Color4
from itertools import batched

def cell_white_text(color8: int):
    return text(f"{color8: >3}") | padding | bg_fill | bg(color8) | fg(Color4.BRIGHT_WHITE)
def cell_black_text(color8: int):
    return text(f"{color8: >3}") | padding | bg_fill | bg(color8) | fg(16)
def display_char_style():
    out = []
    for i in StyleAttr:
        out.append(text(i.name) | push_rule(StyleRule(add_attrs=i))) # type: ignore
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


def display_true_color():
    colors = []
    STEPS_X = 90
    STEPS_Y = 5
    for i in range(STEPS_Y):
        ky = (0.5 - (i / STEPS_Y) * 0.25)
        for j in range(STEPS_X):
            kx = j / STEPS_X
            colors.append(text(" ") | bg(hsl(kx, 1, ky)))
    return vbox(list(hbox(row) for row in batched(colors, STEPS_X)))


def title(c: str):
    return combine(padding, border_with_title(text(f" {c} ") | center, styled(border_rounded, rule_dim)))


layout = vbox([
    display_color_8() | title("Color8"),
    display_true_color() | title("True Color"),
    display_char_style() | title("StyleAttr"),
    vbox([
        text("Will break border if assumed width of 1 🥰, おはよう"),
    ]) | title("Wide chars")
]) | shrink

result = layout_to_result(layout, Rect(94, 36))

if __name__ == "__main__":
    print(result_to_str(result))
