from functui.common import text, border, vbox, _border_render, _text_render, _vbox_render
from functui.text_wrapping import span, adaptive_text, _adaptive_text_render
from functui.classes import layout_to_result, Rect, StyleRule, Color4

def text_cach_text():
    _text_render.cache_clear()
    layout = text("hej")
    layout_to_result(Rect(10, 10), layout)
    assert _text_render.cache_info().hits == 0
    assert _text_render.cache_info().misses == 1
    assert _text_render.cache_info().currsize == 1

    layout = text("hej")
    layout_to_result(Rect(10, 10), layout)
    assert _text_render.cache_info().hits == 1
    assert _text_render.cache_info().misses == 1
    assert _text_render.cache_info().currsize == 1

def test_basic_cache():
    _border_render.cache_clear()
    _text_render.cache_clear()
    layout = text("hej") | border

    layout_to_result(Rect(10, 10), layout)
    assert _border_render.cache_info().hits == 0
    assert _border_render.cache_info().misses == 1
    assert _border_render.cache_info().currsize == 1
    assert _text_render.cache_info().hits == 0
    assert _text_render.cache_info().misses == 1
    assert _text_render.cache_info().currsize == 1

    layout = text("hej") | border
    print(_border_render.cache_parameters())
    layout_to_result(Rect(10, 10), layout)
    assert _border_render.cache_info().hits == 1
    assert _border_render.cache_info().misses == 1
    assert _border_render.cache_info().currsize == 1
    # text render still the same because of border
    assert _text_render.cache_info().hits == 0
    assert _text_render.cache_info().misses == 1
    assert _text_render.cache_info().currsize == 1

def test_cache_vbox():
    _text_render.cache_clear()
    _vbox_render.cache_clear()

    layout = vbox([text("hej"), text("hej")])
    layout_to_result(Rect(10, 10), layout)
    assert _vbox_render.cache_info().hits == 0
    assert _vbox_render.cache_info().misses == 1
    assert _vbox_render.cache_info().currsize == 1
    assert _text_render.cache_info().hits == 0
    assert _text_render.cache_info().misses == 2
    assert _text_render.cache_info().currsize == 2

    layout = vbox([text("hej"), text("hej")])
    layout_to_result(Rect(10, 10), layout)
    assert _vbox_render.cache_info().hits == 1
    assert _vbox_render.cache_info().misses == 1
    assert _vbox_render.cache_info().currsize == 1
    assert _text_render.cache_info().hits == 0
    assert _text_render.cache_info().misses == 2
    assert _text_render.cache_info().currsize == 2

    # slightly different layout
    layout = vbox([text("hej"), text("foo")])
    layout_to_result(Rect(10, 10), layout)
    assert _vbox_render.cache_info().hits == 1
    assert _vbox_render.cache_info().misses == 2
    assert _vbox_render.cache_info().currsize == 2
    assert _text_render.cache_info().hits == 1
    assert _text_render.cache_info().misses == 3
    assert _text_render.cache_info().currsize == 3

def test_cache_adaptive_text():
    _adaptive_text_render.cache_clear()
    layout = adaptive_text("hej", span("mig", rule=StyleRule()))

    layout_to_result(Rect(10, 10), layout)
    assert _adaptive_text_render.cache_info().hits == 0
    assert _adaptive_text_render.cache_info().misses == 1
    assert _adaptive_text_render.cache_info().currsize == 1

    layout = adaptive_text("hej", span("mig", rule=StyleRule()))
    layout_to_result(Rect(10, 10), layout)
    assert _adaptive_text_render.cache_info().hits == 1
    assert _adaptive_text_render.cache_info().misses == 1
    assert _adaptive_text_render.cache_info().currsize == 1

    layout = adaptive_text("hej", span("mig", rule=StyleRule(fg=Color4.BLACK)))
    layout_to_result(Rect(10, 10), layout)
    assert _adaptive_text_render.cache_info().hits == 1
    assert _adaptive_text_render.cache_info().misses == 2
    assert _adaptive_text_render.cache_info().currsize == 2


