from functui import Rect, Screen, Frame, Color4, ComputedStyle, Box, Coordinate, render_simple
from functui._io import _render_ansi
from functui.nodes import *
from wcwidth import wcswidth

def measure_text(x: str) -> int:
    return wcswidth(x)

def _create_ctx(screen: Screen):
    return Frame(
            screen_rect=screen.dimensions,
            view_box=Box(screen.dimensions.width, screen.dimensions.height),
            default_style=ComputedStyle(fg=Color4.RESET, bg=Color4.RESET),
            measure_text=measure_text,
            _render_later=[],
            _strips = screen._strips,
            _boxes_by_id = {},
        )

def test_text_draw_cut_off_rigth_1():
    s = Screen()
    s.set_dimensions(Rect(3, 1))
    c = _create_ctx(s)
    c.view_box = Box(1, 1)
    c.draw_string_line("abc", Coordinate(0, 0))

    assert _render_ansi(s._strips) == "a  "

def test_text_draw_cut_off_right_2():
    s = Screen()
    s.set_dimensions(Rect(3, 1))
    c = _create_ctx(s)
    c.view_box = Box(2, 1)
    c.draw_string_line("abc", Coordinate(0, 0))

    assert _render_ansi(s._strips) == "ab "

def test_text_draw_cut_off_right_3():
    s = Screen()
    s.set_dimensions(Rect(3, 1))
    c = _create_ctx(s)
    c.view_box = Box(3, 1)
    c.draw_string_line("abc", Coordinate(0, 0))

    assert _render_ansi(s._strips) == "abc"


POSITION = Coordinate(3, 0)
def test_text_draw_offset_cut_off_rigth_1():
    s = Screen()
    s.set_dimensions(Rect(6, 1))
    c = _create_ctx(s)
    c.view_box = Box(1, 1, POSITION)
    c.draw_string_line("abc", POSITION)

    assert _render_ansi(s._strips) == "   a  "

def test_text_draw_offset_cut_off_right_2():
    s = Screen()
    s.set_dimensions(Rect(6, 1))
    c = _create_ctx(s)
    c.view_box = Box(2, 1, POSITION)
    c.draw_string_line("abc", POSITION)

    assert _render_ansi(s._strips) == "   ab "

def test_text_draw_offset_cut_off_right_3():
    s = Screen()
    s.set_dimensions(Rect(6, 1))
    c = _create_ctx(s)
    c.view_box = Box(3, 1, POSITION)
    c.draw_string_line("abc", POSITION)

    assert _render_ansi(s._strips) == "   abc"
