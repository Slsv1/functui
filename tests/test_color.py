from functui import hex, Color, rgb, Rect, rgba, render_simple
from functui.nodes import *

def test_rgb_to_hex():
    v = rgb(50, 100, 200)
    assert v.hex == 0x3264c8


def test_hex_to_rgb():
    v = hex(0x3264c8)
    assert (v.r, v.g, v.b) == (50, 100, 200)

def test_hex_to_rgb_beggining_with_zero():
    v = hex(0x080808)
    assert (v.r, v.g, v.b) == (8, 8, 8)

def test_rbg_to_hex_beggining_with_zero():
    v = rgb(8, 8, 8)
    assert v.hex == 0x080808

def test_rbg_to_hex_str_beggining_with_zero():
    v = rgb(8, 8, 8)
    assert v.hex_str == "#080808"

def test_rgb_to_hex_str():
    v = rgb(50, 100, 200)
    assert v.hex_str == "#3264c8"

def test_color_not_overflowing():
    layout = text("..\n..") | bg(200)
    ADD_COLOR = "\x1b[48;5;200m"
    # resets styles and both fore and background colors at end of each line
    RESET_COLOR = "\x1b[0m\x1b[39m\x1b[49m"
    assert render_simple(layout, 2, 2) == f'{ADD_COLOR}..{RESET_COLOR}\n{ADD_COLOR}..{RESET_COLOR}'

def test_color_parse_rgb():
    c = Color.parse("rgb(50, 100, 20)")
    assert c == rgb(50, 100, 20)

    c = Color.parse(" rgb(  50 , 100    , 20 )  ")
    assert c == rgb(50, 100, 20)

def test_color_parse_rgba():
    c = Color.parse("rgba(50, 100, 20, 0.5)")
    assert c == rgba(50, 100, 20, 0.5)

    c = Color.parse(" rgba(  50 , 100    , 20 , 0.5)  ")
    assert c == rgba(50, 100, 20, 0.5)

def test_color_parse_hex():
    c = Color.parse("#20FFB1")
    assert c == hex(0x20FFB1)

