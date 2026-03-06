from functui.flex import flex, flex_custom, vbox_flex, hbox_flex
from functui.common import _bg_char_render, bg_char, text, border_ascii, shrink

from functui import layout_to_str, Rect
from functui.rich_text import adaptive_text

def item(s: str):
    return text(s) | border_ascii

def render_to_fit(layout, result: list[str]) -> list[str]:
    height = len(result)
    width = len(result[0])
    return layout_to_str(layout, Rect(width, height)).splitlines()

def test_flex_and_no_flex():
    layout = hbox_flex([
        item("a") | flex,
        item("b"),
    ]) | border_ascii
    expected = [
        "+----------+",
        "|+-----++-+|",
        "||a    ||b||",
        "|+-----++-+|",
        "+----------+",
    ]
    assert render_to_fit(layout,expected)

def test_flex_grow_uniform_without_basis():
    layout = hbox_flex([
        item("abc") | flex,
        item("123456789") | flex,
    ]) | border_ascii
    expected = [
        "+----------------------------+",
        "|+------------++------------+|",
        "||abc         ||123456789   ||",
        "|+------------++------------+|",
        "+----------------------------+",
    ]
    assert render_to_fit(layout, expected) == expected

def test_flex_shrink_with_basis():
    flex_config = flex_custom(grow=0, shrink=1, basis=True)
    layout = hbox_flex([
        item("======aaaaaaa") | flex_config,
        item("bbbbbb") | flex_config,
    ]) | border_ascii
    expected = [
        "+-------------+",
        "|+------++---+|",
        "||======||bbb||",
        "|+------++---+|",
        "+-------------+",
    ]
    assert render_to_fit(layout, expected) == expected

def test_flex_different_shrink_with_basis():
    layout = hbox_flex([
        item("======aaaaaaa") | flex_custom(grow=0, shrink=1, basis=True),
        item("bbbbbbccccccc") | flex_custom(grow=0, shrink=2, basis=True),
    ]) | border_ascii
    expected = [
        "+-------------------+",
        "|+---------++------+|",
        "||======aaa||bbbbbb||",
        "|+---------++------+|",
        "+-------------------+",
    ]
    assert render_to_fit(layout, expected) == expected

def test_flex_shrink_to_min_size_vertical_and_horizontal():
    layout = hbox_flex([
        adaptive_text("aaa bbb") | border_ascii | flex_custom(1),
        adaptive_text("ccc") | bg_char(".") | border_ascii|  flex_custom(1),
    ]) | border_ascii | shrink
    expected = [
        "+----------+ ",
        "|+---++---+| ",
        "||aaa||ccc|| ",
        "||bbb||   || ",
        "|+---++---+| ",
        "+----------+ ",
        "             ",
    ]
    assert render_to_fit(layout, expected) == expected

# def test_flex_shrink_to_min_size():
#     layout = hbox_flex([
#         adaptive_text("aaa bbb") | border_ascii | flex_custom(1),
#         adaptive_text("ccc") | bg_char(".") | border_ascii|  flex_custom(1),
#     ]) | border_ascii | shrink
#     expected = [
#         "+----------+",
#         "|+---++---+|",
#         "||aaa||ccc||",
#         "||bbb||   ||",
#         "|+---++---+|",
#         "+----------+",
#         "            ",
#     ]
#     assert render_to_fit(layout, expected) == expected
#
"""
min_size:
    if shrink:
        for each shrink>0:
            actuall_size = basis_size * factor
    if grow:
        for each grow>0:
            actuall_size = basis_size + ration


    return sum(asctuall_sizes)

actuall:
    if shrink:
        for each shrink>0:
            actuall_size = basis_size * factor
    if grow:
        for each grow>0:
            actuall_size = basis_size + ration

    for each actuall_size:
        child(actuall_size)

"""
