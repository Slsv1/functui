import pytest
# from functui.ansirender import layout_to_str
from functui import Rect, layout_to_str, Style
from functui.classes import Color
from functui.text_wrapping import _span_to_lines, Segment, Span, wrap_line_default, Group
from wcwidth import wcswidth


def measure_text(s):
    return wcswidth(s)


def test_group_split_overflow_with_break():
    s1 = Style()
    s2 = Style(fg=Color.BLUE)
    assert Group((Segment("a", s1, 1), Segment("bc", s2, 2)), False)\
        .split(2, measure_text)\
        ==[
        Group((Segment("a", s1, 1), Segment("b", s2, 1)), False),
        Group((Segment("c", s2, 1),), False)
    ]

def test_group_split_overflow_with_break_and_trailing_group():
    s1 = Style()
    s2 = Style(fg=Color.BLUE)
    assert _to_group_with_segments(("abc", s1), ("d", s2))\
        .split(2, measure_text)\
        ==[
        _to_group_with_segments(("ab", s1)),
        _to_group_with_segments(("c", s1), ("d", s2))
    ]

def test_group_split_no_overflow():
    s1 = Style()
    s2 = Style(fg=Color.BLUE)
    assert Group((Segment("a", s1, 1), Segment("bc", s2, 2)), False)\
        .split(3, measure_text)\
        ==[
        Group((Segment("a", s1, 1), Segment("bc", s2, 2)), False),
    ]


def test_group_split_overflow_no_break():
    s1 = Style()
    s2 = Style(fg=Color.BLUE)
    assert Group((Segment("ab", s1, 2), Segment("cd", s2, 2)), False)\
        .split(2, measure_text)\
        ==[
        Group((Segment("ab", s1, 2),), False),
        Group((Segment("cd", s2, 2),), False),
    ]


def test_span_to_lines():
    s1 = Style()
    s2 = Style(fg=Color.BLUE)
    assert _span_to_lines(
        Span(
            (
                "hej ",
                Span(
                    ("blue",),
                    s2
                ),
                "hi"
            ),
            s1
        ),
        measure_text,
    ) == [[
        Group((Segment("hej", s1, 3),), False),
        Group((Segment(" ", s1, 1),), True),
        Group((Segment("blue", s2, 4), Segment("hi", s1, 2)), False)
    ]]


def test_span_to_lines_join():
    s1 = Style()
    s2 = Style(fg=Color.BLUE)
    assert _span_to_lines(
        Span(
            (
                Span(("hej",),s1),
                Span(("blue",),s2),
            ),
            s1
        ),
        measure_text,
    ) == [[
        Group((Segment("hej", s1, 3),Segment("blue", s2, 4)), False),
    ]]


def _to_group(string:str, style:Style):
    return Group((Segment(string, style, measure_text(string)),), string.isspace())

def _to_group_with_segments(*segments: tuple[str, Style]):
    return Group(
        tuple(Segment(string, style, measure_text(string)) for string, style in segments),
        segments[-1][0].isspace()
    )


def test_span_to_segments_with_newline():
    s1 = Style()
    s2 = Style(fg=Color.BLUE)
    assert _span_to_lines(
        Span(
            (
                "hej \nmig2 ",
                Span(
                    ("blue",),
                    s2
                )
            ),
            s1
        ),
        measure_text
    ) == [
        [_to_group("hej", s1), _to_group(" ", s1)],
        [_to_group("mig2", s1), _to_group(" ", s1), _to_group("blue", s2)]
    ]


def test_span_to_segments_with_multilple_newlines():
    s1 = Style()
    assert _span_to_lines(
        Span(
            (
                "hej \n\n\nhej2",
            ),
            s1
        ),
        measure_text
    ) == [
        [_to_group("hej", s1), _to_group(" ", s1)],
        [],
        [],
        [_to_group("hej2", s1)]
    ]


def test_wrap_line_default_trim():
    s = Style()
    assert wrap_line_default(
        [_to_group(" ", s),_to_group("aaa", s), _to_group(" ", s)],
        3,
        measure_text
    ) == [[_to_group("aaa", s)]]


def test_wrap_line_default_wrap_and_remove_whitespace():
    s = Style()
    assert wrap_line_default(
        [_to_group("aaa", s), _to_group(" ", s), _to_group("bbb", s)],
        3,
        measure_text
    ) == [
        [_to_group("aaa", s)],
        [_to_group("bbb", s)]
    ]


def test_wrap_line_default_word_too_long():
    s = Style()
    assert wrap_line_default(
        [_to_group("abcdefg", s)],
        4,
        measure_text
    ) == [
        [_to_group_with_segments(("abc", s), ("-", s))],
        [_to_group("defg", s)]
    ]
def test_wrap_line_default_word_too_long_take_up_3_lines():
    s = Style()
    assert wrap_line_default(
        [_to_group("abcdefgh", s)],
        4,
        measure_text
    ) == [
        [_to_group_with_segments(("abc", s), ("-", s))],
        [_to_group_with_segments(("def", s), ("-", s))],
        [_to_group("gh", s)]
    ]
def test_wrap_line_default_word_too_long_and_segment_after():
    s = Style()
    assert wrap_line_default(
        [_to_group_with_segments(("abcdefgh", s), ("jj", s))],
        4,
        measure_text
    ) == [
        [_to_group_with_segments(("abc", s), ("-", s))],
        [_to_group_with_segments(("def", s), ("-", s))],
        [_to_group_with_segments(("gh", s), ("jj", s))]
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
