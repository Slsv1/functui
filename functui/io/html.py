from ..classes import Layout, Rect, StyleAttr, ComputedStyle, ResultCreatedWith, Screen, Result, Color4, Color24, hex, layout_to_result
from ..color_data import xterm256_to_hex
from typing import NamedTuple

HTML_ESCAPES = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
}
class HTMLTags(NamedTuple):
    open: str
    closed: str

# def hex_int_to_string

def style_to_tag(style: ComputedStyle) -> HTMLTags:
    tags_open = []
    tags_closed = []
    if StyleAttr.BOLD in style.attrs:
        tags_open.append("b")
        tags_closed.append("b")
    if StyleAttr.ITALIC in style.attrs:
        tags_open.append("i")
        tags_closed.append("i")
    if StyleAttr.STRIKE_THROUGH in style.attrs:
        tags_open.append("strike")
        tags_closed.append("strike")
    if StyleAttr.UNDERLINE in style.attrs:
        tags_open.append("u")
        tags_closed.append("u")

    style_attributes = []
    if style.fg != Color4.RESET:
        if isinstance(style.fg, int):
            color = hex(xterm256_to_hex(style.fg))
        else:
            color = style.fg
        style_attributes.append(f"color:{color.hex_str}")

    if style.bg != Color4.RESET:
        if isinstance(style.bg, int):
            color = hex(xterm256_to_hex(style.bg))
        else:
            color = style.bg
        style_attributes.append(f"background-color:{color.hex_str}")

    if style_attributes:
        tags_open.append(f"span style=\"{"; ".join(style_attributes)}\"")
        tags_closed.append("span")
    return HTMLTags(
        open="".join(f"<{i}>" for i in tags_open),
        closed="".join(f"</{i}>" for i in tags_closed)
    )


def result_to_html_str(result: Result):
    data = result.try_data(ResultCreatedWith)
    if data is None:
        raise AssertionError("Result has no ResultCreatedWith data. If possible please use get_result() function to get a result.")
    screen = Screen(data.screen_size.width, data.screen_size.height)
    screen.apply_draw_commands(data.measure_text_func, result.get_commands())

    curr_style = ComputedStyle()
    curr_tags = style_to_tag(curr_style)
    out = [curr_tags.open]
    for line in screen.split_by_lines():
        for pixel in line:
            if pixel.style != curr_style:
                out.append(curr_tags.closed)
                curr_style = pixel.style
                curr_tags = style_to_tag(curr_style)
                out.append(curr_tags.open)
            if pixel.char in HTML_ESCAPES:
                out.append(HTML_ESCAPES[pixel.char])
            else:
                out.append(pixel.char)
        out.append("\n")

    out = out[:-1] # -1 to remove the \n on the end
    out.append(curr_tags.closed)
    return f"<pre style=\"font-family:monospace\">\n{"".join(out)}\n</pre>"

def layout_to_html_str(layout: Layout, dimensions: Rect):
    return result_to_html_str(layout_to_result(layout, dimensions))
