from functui.classes import hex, Color24, rgb, Rect
from functui.common import *
from functui.io.ansi import layout_to_str

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
    layout = text(".\n.") | bg(200)
    ADD_COLOR = "\x1b[48;5;200m"
    RESET_COLOR = "\x1b[49m"
    assert layout_to_str(layout, Rect(1, 2)) == f'{ADD_COLOR}.{RESET_COLOR}\n{ADD_COLOR}.{RESET_COLOR}'

