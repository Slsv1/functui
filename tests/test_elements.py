import pytest
# from functui.ansirender import layout_to_str
from functui import Rect, layout_to_str
from functui.default_elements import adaptive_text, _split_by_lines_remove_surrounding_space
from wcwidth import wcswidth

measure_text = lambda s: wcswidth(s)
def test_adaptive_text_wrapping_remove_white_space():
    layout = adaptive_text("12345   12 456 123")
    assert layout_to_str(layout, Rect(6, 3)) == "\n".join([
        "12345 ",
        "12 456",
        "123   ",
    ])

def test_adaptive_text_wrapping_word():
    layout = adaptive_text("1234567")
    assert layout_to_str(layout, Rect(6, 2)) == "\n".join([
        "12345-",
        "67    ",
    ])
def test_adaptive_text_wrapping_word_multiple():
    layout = adaptive_text("1234567")
    assert layout_to_str(layout, Rect(3, 2)) == "\n".join([
        "12-",
        "34-",
        "567",
    ])
def test_adaptive_text_terminator():
    layout = adaptive_text("1234 12345 123")
    assert layout_to_str(layout, Rect(4, 2)) == "\n".join([
        "1234",
        "1...",
    ])

def test_split_by_lines_respect_newlines():
    assert _split_by_lines_remove_surrounding_space(measure_text, 7, "foo\nhej bar") == [
        "foo",
        "hej bar"
    ]

def test_split_by_lines_word():
    assert _split_by_lines_remove_surrounding_space(measure_text, 7, "foo\nhej bar") == [
        "foo",
        "hej bar"
    ]
