from functui.classes import hex, Color24, rgb

def test_rgb_to_hex():
    v = rgb(50, 100, 200)
    assert v.hex == 0x3264c8


def test_hex_to_rgb():
    v = hex(0x3264c8)
    assert (v.r, v.g, v.b) == (50, 100, 200)

def test_rgb_to_hex_str():
    v = rgb(50, 100, 200)
    assert v.hex_str == "#3264c8"
