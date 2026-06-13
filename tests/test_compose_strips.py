from functui.classes import ComputedStyle, Strip, compose_strips
from wcwidth import wcswidth


def _create_strip(pos: int, string: str):
    return Strip(pos, string, ComputedStyle(), wcswidth(string))

def _to_string(gen):
    return "".join(i[1] for i in gen)

def test_basic_compose():
    gen = compose_strips([
        _create_strip(0, "aaaaaa"),
        _create_strip(2,   "bbb")
    ])

    assert _to_string(gen) == "aabbba"

def test_widechar_over_monospace():
    gen = compose_strips([
        _create_strip(0, "aaaaaa"),
        _create_strip(2,   "😀"  )
    ])

    assert _to_string(gen) == "aa😀aa"

def test_monospace_over_widechar_even():
    gen = compose_strips([
        _create_strip(0, "😀😀😀"),
        _create_strip(2,   "aa"  )
    ])

    assert _to_string(gen) == "😀aa😀"

def test_monospace_over_widechar_odd():
    gen = compose_strips([
        _create_strip(0, "😀😀😀"),
        _create_strip(1,  "aa"   )
    ])

    assert _to_string(gen) == " aa 😀"
