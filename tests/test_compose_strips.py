from functui import ComputedStyle
from functui._classes import Strip, compose_strips
from wcwidth import wcswidth


def _create_strip(pos: int, string: str):
    return Strip.from_widechar_string(pos, string, ComputedStyle(), wcswidth(string))

def _to_string(gen):
    return "".join(i[1] for i in gen)

def test_basic_compose():
    gen = compose_strips([
        _create_strip(0, "aaaaaa"),
        _create_strip(2,   "bbb")
    ])

    assert _to_string(gen) == "aabbba"

def test_compose_go_down_in_depth():
    gen = compose_strips([
        _create_strip(0, "aaaaaa"),
        _create_strip(4,     "bb"),
        _create_strip(0, "cc"    )
    ])

    assert _to_string(gen) == "ccaabb"

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

    assert _to_string(gen) ==  "😀a 😀" # current wierd behaviour
    #assert _to_string(gen) == " aa 😀" # preferred behaviour

def test_widechar_over_widechar_even():
    gen = compose_strips([
        _create_strip(0, "😀😀😀"),
        _create_strip(2,   "👍"  )
    ])

    assert _to_string(gen) ==  "😀👍😀"

def test_widechar_over_widechar_odd():
    gen = compose_strips([
        _create_strip(0, "😀😀😀"),
        _create_strip(1,  "👍"   )
    ])

    assert _to_string(gen) ==  "😀  😀" # current wierd behaviour
    #assert _to_string(gen) == " 👍 😀" # preferred behavious



