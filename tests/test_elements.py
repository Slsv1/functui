import pytest
# from functui.ansirender import layout_to_str
from functui import Rect, layout_to_str, Style
# from functui.default_elements import adaptive_text, _wrap_segments
from functui.classes import Color
from functui.text_wrapping_elements import _span_to_segments, _Segment, _Span, wrap_line_default
from wcwidth import wcswidth

measure_text = lambda s: wcswidth(s)

def test_span_to_segments():
    s1 = Style()
    s2 = Style(fg=Color.BLUE)
    assert _span_to_segments(
        _Span(
            (
                "hej ",
                _Span(
                    ("blue",),
                    s2
                ),
                "hi"
            ),
            s1
        )
    ) == [[_Segment("hej", s1), _Segment(" ", s1), _Segment("blue", s2), _Segment("hi", s1)]]

def test_span_to_segments_with_newline():
    s1 = Style()
    s2 = Style(fg=Color.BLUE)
    assert _span_to_segments(
        _Span(
            (
                "hej \nhej2 ",
                _Span(
                    ("blue",),
                    s2
                )
            ),
            s1
        )
    ) == [
        [_Segment("hej", s1), _Segment(" ", s1)],
        [_Segment("hej2", s1), _Segment(" ", s1), _Segment("blue", s2)]
    ]
def test_span_to_segments_with_multilple_newlines():
    s1 = Style()
    assert _span_to_segments(
        _Span(
            (
                "hej \n\n\nhej2",
            ),
            s1
        )
    ) == [
        [_Segment("hej", s1), _Segment(" ", s1)],
        [],
        [],
        [_Segment("hej2", s1)]
    ]

def test_wrap_line_default_trim():
    s = Style()
    assert wrap_line_default(
        [_Segment(" ", s),_Segment("aaa", s), _Segment(" ", s)],
        3,
        measure_text
    ) == [[_Segment("aaa", s)]]

def test_wrap_line_default_works():
    s = Style()
    assert wrap_line_default(
        [_Segment("aaa", s), _Segment(" ", s), _Segment("bbb", s)],
        3,
        measure_text
    ) == [
        [_Segment("aaa", s)],
        [_Segment("bbb", s)]
    ]



# def test_adaptive_text_wrapping_remove_white_space():
#     layout = adaptive_text("12345   12 456 123")
#     assert layout_to_str(layout, Rect(6, 3)) == "\n".join([
#         "12345 ",
#         "12 456",
#         "123   ",
#     ])
#
# def test_adaptive_text_wrapping_word():
#     layout = adaptive_text("1234567")
#     assert layout_to_str(layout, Rect(6, 2)) == "\n".join([
#         "12345-",
#         "67    ",
#     ])
#
# def test_adaptive_text_wrapping_word_multiple():
#     layout = adaptive_text("1234567")
#     assert layout_to_str(layout, Rect(3, 2)) == "\n".join([
#         "12-",
#         "34-",
#         "567",
#     ])
# def test_adaptive_text_terminator():
#     layout = adaptive_text("1234 12345 123")
#     assert layout_to_str(layout, Rect(4, 2)) == "\n".join([
#         "1234",
#         "1...",
#     ])
#
