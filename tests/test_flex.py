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

def test_hflex_and_no_flex():
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

def test_vflex_and_no_flex():
    layout = vbox_flex([
        item("a") | flex,
        item("b"),
    ]) | border_ascii
    expected = [
        "+---+",
        "|+-+|",
        "||a||",
        "|| ||",
        "|| ||",
        "|+-+|",
        "|+-+|",
        "||b||",
        "|+-+|",
        "+---+",
    ]
    assert render_to_fit(layout,expected)

def test_hflex_grow_uniform_without_basis():
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

def test_vflex_grow_uniform_without_basis():
    layout = vbox_flex([
        item("a") | flex,
        item("1\n2") | flex,
    ]) | border_ascii
    expected = [
        "+---+",
        "|+-+|",
        "||a||",
        "|| ||",
        "|| ||",
        "|+-+|",
        "|+-+|",
        "||1||",
        "||2||",
        "|| ||",
        "|+-+|",
        "+---+",
    ]
    assert render_to_fit(layout, expected) == expected

def test_hflex_shrink_with_basis():
    flex_config = flex_custom(grow=0, shrink=True, basis=True)
    layout = hbox_flex([
        text("======aaaaaaa") | flex_config,
        text("bbbbbb") | flex_config,
    ]) | border_ascii
    expected = [
        "+---------+",
        "|======bbb|",
        "+---------+",
    ]
    assert render_to_fit(layout, expected) == expected

def test_vflex_shrink_to_min_size():
    layout = vbox_flex([
        adaptive_text("aaa bbb") | border_ascii | flex_custom(1),
        adaptive_text("ccc") | border_ascii|  flex_custom(1),
    ]) | border_ascii | shrink
def test_vflex_no_shrink_to_min_size():
    layout = vbox_flex([
        adaptive_text("aaa bbb") | border_ascii | flex_custom(1),
        adaptive_text("ccc") | border_ascii|  flex_custom(1),
    ]) | border_ascii

    expected = [
        "+--------+",
        "|+------+|",
        "||aaa   ||",
        "||bbb   ||",
        "|+------+|",
        "|+------+|",
        "||ccc   ||",
        "||      ||",
        "|+------+|",
        "+--------+",
    ]
    assert render_to_fit(layout, expected) == expected

    expected = [
        "+------+  ",
        "|+----+|  ",
        "||aaa ||  ", # extra space after "aaa" becaue adaptive text insludes
        "||bbb ||  ", # whitespace when wrapping
        "|+----+|  ",
        "|+----+|  ",
        "||ccc ||  ",
        "||    ||  ",
        "|+----+|  ",
        "+------+  ",
    ]
    assert render_to_fit(layout | shrink, expected) == expected


def test_hflex_shrink_to_min_size_vertically():
    layout = hbox_flex([
        adaptive_text("aaa bbb") | border_ascii | flex_custom(1),
        adaptive_text("ccc") | border_ascii|  flex_custom(1),
    ]) | border_ascii | shrink
    expected = [
        "+----------+",
        "|+---++---+|",
        "||aaa||ccc||",
        "||bbb||   ||",
        "|+---++---+|",
        "+----------+",
        "            ",
        "            ",
        "            ",
        "            ",
    ]
    assert render_to_fit(layout, expected) == expected


def test_no_exception_when_no_space():
    layout = hbox_flex([
        adaptive_text("aaa bbb") | border_ascii | flex_custom(1),
        adaptive_text("ccc") | border_ascii|  flex_custom(1),
    ]) | border_ascii | shrink
    expected = [
        "+", # limit to a 1 x 1 screen size
    ]
    assert render_to_fit(layout, expected) == expected
