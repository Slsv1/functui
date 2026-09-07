import pytest
from functui._rich_text import adaptive_text, split_by_tokens, wrap_line_keep_space, wrap_line_trim_ends, wrap_tokens_if_possible
from functui._geometry import Rect
from functui._common import text
from functui import render_simple
from wcwidth import wcswidth


def measure_text(s):
    return wcswidth(s)

def test_text_overflow():
    layout = text("hej")
    assert render_simple(layout, 3, 1) == "hej"

    layout = text("hej")
    assert render_simple(layout, 2, 1) == "h…"

    layout = text("hej")
    assert render_simple(layout, 1, 1) == "…"

    layout = text("hej")
    assert render_simple(layout, 0, 1) == ""

def test_split_by_token():
    gen = split_by_tokens(
        line="a bb. c",
        white_space_chars= (" ", ".")
    )

    # the list if a reference and gets reset every new next()
    assert next(gen) == ("a",  0, 1, False)   
    assert next(gen) == (" ",  1, 1, True)
    assert next(gen) == ("bb", 2, 2, False)
    assert next(gen) == (". ", 4, 2, True)   
    assert next(gen) == ("c",  6, 1, False)

def test_wrap_tokens_if_possible():
    gen = wrap_tokens_if_possible(
        split_by_tokens(
            line="too_long ok fine extremely_long     ",
            white_space_chars=(" ",)
        ),
        max_width=4,
    )

    assert next(gen) == ("too_", 0 , 4, False)
    assert next(gen) == ("long", 4 , 4, False)
    assert next(gen) == (" ",    8 , 1, True)
    assert next(gen) == ("ok",   9 , 2, False)
    assert next(gen) == (" ",    11, 1, True)
    assert next(gen) == ("fine", 12, 4, False)
    assert next(gen) == (" ",    16, 1, True)
    assert next(gen) == ("extr", 17, 4, False)
    assert next(gen) == ("emel", 21, 4, False)
    assert next(gen) == ("y_lo", 25, 4, False)
    assert next(gen) == ("ng"  , 29, 2, False)
    assert next(gen) == ("    ", 31, 4, True)
    assert next(gen) == (" ", 35, 1, True)

def test_wrap_line_trim_ends():
    gen = wrap_line_trim_ends("alpha bravo charlie delta", max_width=5, white_space_chars=(" ",))
    assert next(gen) == (("alpha", 0, 5, False),)
    assert next(gen) == (("bravo", 6, 5, False),)
    assert next(gen) == (("charl", 12, 5, False),)
    assert next(gen) == (("ie", 17, 2, False),)
    assert next(gen) == (("delta", 20, 5, False),)

# this behaviour is important so that when .splitlines() is called with \n\n the '' between the \n's gets counted
def test_wrap_line_trim_ends_keep_blank():
    gen = wrap_line_trim_ends(
        content='',
        white_space_chars=(' ',),
        max_width=100,
    )
    assert next(gen) == (("", 0, 0, True),)

def test_wrap_line_trim_ends_keep_blank_space():
    gen = wrap_line_trim_ends(
        content=' ',
        white_space_chars=(' ',),
        max_width=100,
    )
    assert next(gen) == ((" ", 0, 1, True),)


def test_wrap_line_keep_ends_keep_blank():
    gen = wrap_line_keep_space(
        content='',
        white_space_chars=(' ',),
        max_width=100,
    )
    assert next(gen) == (("", 0, 0, True),)


def test_adaptive_text_min_size_with_newlines():
    assert adaptive_text("aa\nbb\n\ncc").min_size(measure_text, Rect(9999, 9999))\
        == Rect(width=2, height=4)

def test_general_render():
    layout = adaptive_text("foo\nbar baz buz  \n\nqux")
    assert render_simple(layout, 7, 5) == "\n".join([
        "foo    ",
        "bar baz",
        "buz    ",
        "       ",
        "qux    ",
    ])


# def test_line_trim():
#     assert list(wrap_line("aaa  ", 3)) == [
#         (0, "aaa", 3)
#     ]
#
# def test_ignore_whitespace():
#     assert list(wrap_str("aaa bbb", 3)) == [
#         (0, "aaa", 3),
#         (4, "bbb", 3),
#     ]
#
# def test_token_clip():
#     assert list(wrap_str("abcdefg", 4)) ==[
#         (0, "abcd", 4)
#     ]
#
# def test_token_clip_and_wrap():
#     assert list(wrap_str("abcdefg hi", 4)) ==[
#         (0, "abcd", 4),
#         (8, "hi", 2)
#     ]


# def test_adaptive_text_wrapping_ignore_white_space():
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
#         "123457",
#     ])



