from functui.flex import flex, flex_custom, vbox_flex, hbox_flex
from functui.common import text, border_ascii

from functui import layout_to_str, Rect

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

