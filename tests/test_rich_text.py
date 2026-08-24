import pytest
from functui._rich_text import split_by_tokens
from wcwidth import wcswidth


def measure_text(s):
    return wcswidth(s)

def test_split_by_token():
    gen = split_by_tokens(
        line="a bb. c",
        white_space_chars= (" ", ".")
    )

    # the list if a reference and gets reset every new next()
    assert next(gen) == (["a"], 1, False)   
    assert next(gen) == ([" "], 1, True)
    assert next(gen) == (["b", "b"], 2, False)
    assert next(gen) == ([".", " "], 2, True)   
    assert next(gen) == (["c"], 1, False)

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



