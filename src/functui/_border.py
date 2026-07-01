from typing import NamedTuple, Protocol
from dataclasses import dataclass
from functools import partial

from ._geometry import Coordinate, Box, Rect
from ._classes import Layout, Frame, min_size_expand, min_size_constant, WrapperNode
from ._common import static_box, vshrink, padding

class WeightMap(NamedTuple):
    top: int
    bottom: int
    left: int
    right: int


def overlay_weight_maps(*maps: WeightMap) -> WeightMap:
    return WeightMap(*(max(dir) for dir in zip(*maps))) # pick highest weights along cardinal direction


class _GetIntersection(Protocol):
    def __call__(self, weight_map: WeightMap, /) -> str | None:
        ...

def _get_default_intersection(weight_map: WeightMap, /):
    return INTERSECTION_MAP.get(weight_map, None)


@dataclass(frozen=True, eq=True)
class BorderStyle:
    """Data structure that represents a border, may be used in :obj:`border_custom`."""
    line_v: str
    line_h: str
    corner_tl: str
    corner_tr: str
    corner_br: str
    corner_bl: str

    # weight_map: WeightMap
    # get_intersection: GetIntersection

class BorderConnection(NamedTuple):
    position: Coordinate
    weight_map: WeightMap

INTERSECTION_MAP = {
    WeightMap(1, 1, 0, 1): "├",
    WeightMap(2, 1, 0, 1): "┝",
    WeightMap(1, 2, 0, 1): "┞",
    WeightMap(2, 2, 0, 1): "┟",
    WeightMap(1, 1, 0, 2): "┠",
    WeightMap(2, 1, 0, 2): "┡",
    WeightMap(1, 2, 0, 2): "┢",
    WeightMap(2, 2, 0, 2): "┣",
    WeightMap(3, 3, 0, 3): "╠",
    WeightMap(3, 3, 0, 1): "╟",
    WeightMap(1, 1, 0, 3): "╞",

    WeightMap(1, 1, 1, 0): "┤",
    WeightMap(2, 1, 1, 0): "┥",
    WeightMap(1, 2, 1, 0): "┦",
    WeightMap(2, 2, 1, 0): "┧",
    WeightMap(1, 1, 2, 0): "┨",
    WeightMap(2, 1, 2, 0): "┩",
    WeightMap(1, 2, 2, 0): "┪",
    WeightMap(2, 2, 2, 0): "┫",
    WeightMap(3, 3, 3, 0): "╣",
    WeightMap(3, 3, 1, 0): "╢",
    WeightMap(1, 1, 3, 0): "╡",

    WeightMap(0, 1, 1, 1): "┬",
    WeightMap(0, 1, 2, 1): "┭",
    WeightMap(0, 1, 1, 2): "┮",
    WeightMap(0, 1, 2, 2): "┯",
    WeightMap(0, 2, 1, 1): "┰",
    WeightMap(0, 2, 2, 1): "┱",
    WeightMap(0, 2, 1, 2): "┲",
    WeightMap(0, 2, 2, 2): "┳",
    WeightMap(0, 3, 3, 3): "╦",
    WeightMap(0, 1, 3, 3): "╤",
    WeightMap(0, 3, 1, 1): "╥",

    WeightMap(1, 0, 1, 1): "┴",
    WeightMap(1, 0, 2, 1): "┵",
    WeightMap(1, 0, 1, 2): "┶",
    WeightMap(1, 0, 2, 2): "┷",
    WeightMap(2, 0, 1, 1): "┸",
    WeightMap(2, 0, 2, 1): "┹",
    WeightMap(2, 0, 1, 2): "┺",
    WeightMap(2, 0, 2, 2): "┻",
    WeightMap(3, 0, 3, 3): "╩",
    WeightMap(3, 0, 1, 1): "╨",
    WeightMap(1, 0, 3, 3): "╧",

    WeightMap(1, 1, 1, 1): "┼",
    WeightMap(2, 1, 1, 1): "┽",
    WeightMap(1, 2, 1, 1): "┾",
    WeightMap(2, 2, 1, 1): "┿",
    WeightMap(1, 1, 2, 1): "╀",
    WeightMap(2, 1, 2, 1): "╁",
    WeightMap(1, 2, 2, 1): "╂",
    WeightMap(2, 2, 2, 1): "╃",
    WeightMap(1, 1, 1, 2): "╄",
    WeightMap(2, 1, 1, 2): "╅",
    WeightMap(1, 2, 1, 2): "╆",
    WeightMap(2, 2, 1, 2): "╇",
    WeightMap(1, 1, 2, 2): "╈",
    WeightMap(2, 1, 2, 2): "╉",
    WeightMap(1, 2, 2, 2): "╊",
    WeightMap(2, 2, 2, 2): "╋",
    WeightMap(3, 3, 3, 3): "╬",
    WeightMap(3, 3, 1, 1): "╫",
    WeightMap(1, 1, 3, 3): "╪",
}

BORDER_ROUNDED = BorderStyle(
    line_v="│",
    line_h="─",
    corner_tl="╭",
    corner_tr="╮",
    corner_bl="╰",
    corner_br="╯",
)
BORDER_REGULAR = BorderStyle(
    line_v="│",
    line_h="─",
    corner_tl="┌",
    corner_tr="┐",
    corner_bl="└",
    corner_br="┘",
)

BORDER_THICK = BorderStyle(
    line_v="┃",
    line_h="━",
    corner_tl="┏",
    corner_tr="┓",
    corner_bl="┗",
    corner_br="┛",
)

BORDER_DOUBLE = BorderStyle(
    line_v="║",
    line_h="═",
    corner_tl="╔",
    corner_tr="╗",
    corner_bl="╚",
    corner_br="╝",
)
BORDER_ASCII = BorderStyle(
    line_v="|",
    line_h="-",
    corner_tl="+",
    corner_tr="+",
    corner_bl="+",
    corner_br="+",
)
BORDER_DASHED = BorderStyle(
    line_v="╎",
    line_h="╌",
    corner_tl="┌",
    corner_tr="┐",
    corner_bl="└",
    corner_br="┘",
)

BORDER_THICK_DASHED = BorderStyle(
    line_v="╏",
    line_h="╍",
    corner_tl="┏",
    corner_tr="┓",
    corner_bl="┗",
    corner_br="┛",
)

BORDER_ROUNDED_DASHED = BorderStyle(
    line_v="╎",
    line_h="╌",
    corner_tl="╭",
    corner_tr="╮",
    corner_bl="╰",
    corner_br="╯",
)

def vbar_custom(char: str = "|"):
    """Vertical bar build with a custom character."""
    return Layout(
        func=vbar_custom,
        min_size=min_size_constant(Rect(1, 1)),
        render=partial(_vbar_render, char)
    )

def _vbar_render(char: str, frame: Frame, box: Box):
    frame.draw_line_v(fill=char, at=box.position, len=box.height)

def hbar_custom(char: str="-"):
    """Horizonatal bar build with a custom character."""
    return Layout(
        func=hbar_custom,
        min_size=min_size_constant(Rect(1, 1)),
        render=partial(_hbar_render, char)
    )

def _hbar_render(char: str, frame: Frame, box: Box):
    frame.draw_line_h(fill=char, at=box.position, len=box.width)

vbar = vbar_custom(BORDER_REGULAR.line_v)
"""Vertical bar."""
vbar_thick = vbar_custom(BORDER_THICK.line_v)
"""A thick vertical bar."""
vbar_double = vbar_custom(BORDER_DOUBLE.line_v)
"""A double vertical bar."""
vbar_ascii = vbar_custom(BORDER_ASCII.line_v)
"""An ascii vertical bar."""
hbar = hbar_custom(BORDER_REGULAR.line_h)
"""Horizontal bar."""
hbar_thick = hbar_custom(BORDER_THICK.line_h)
"""A thick horizontal bar."""
hbar_double = hbar_custom(BORDER_DOUBLE.line_h)
"""A double horizontal bar."""
hbar_ascii = hbar_custom(BORDER_REGULAR.line_h)
"""An ascii horizontal bar."""

def border_custom(style: BorderStyle) -> WrapperNode:
    """Puts a border around a layout in a custom style."""
    def _custom_border(child: Layout):
        return Layout(
            func=border_custom,
            min_size=min_size_expand(child.min_size, 2, 2),
            render=partial(_border_render, style, child),
        )
    return _custom_border


border = border_custom(style=BORDER_REGULAR)
"""Puts a border around a layout."""
border_rounded = border_custom(style=BORDER_ROUNDED)
"""Puts a rounded border around a layout."""
border_thick = border_custom(style=BORDER_THICK)
"""Puts a thick border around a layout."""
border_double = border_custom(style=BORDER_DOUBLE)
"""Puts a double border around a layout."""
border_ascii = border_custom(style=BORDER_ASCII)
"""Puts a border consisting of ascii characters around a layout."""
border_dashed = border_custom(style=BORDER_DASHED)
"""Puts a dashed border around a layout."""
border_rounded_dashed = border_custom(style=BORDER_ROUNDED_DASHED)
"""Puts a rounded dashed border around a layout."""
border_thick_dashed = border_custom(style=BORDER_THICK_DASHED)
"""Puts a rounded dashed border around a layout."""

def _border_render(style: BorderStyle, child: Layout, frame: Frame, box: Box):
    frame.draw_line_v(fill=style.line_v, at=box.position, len=box.height)
    frame.draw_line_h(fill=style.line_h, at=box.position, len=box.width)
    frame.draw_line_v(fill=style.line_v, at=box.position + Coordinate(box.width-1, 0), len=box.height)
    frame.draw_line_h(fill=style.line_h, at=box.position + Coordinate(0, box.height-1), len=box.width)

    frame.draw_pixel(fill=style.corner_tl, at=box.position + Coordinate(0, 0))
    frame.draw_pixel(fill=style.corner_tr, at=box.position + Coordinate(box.width-1, 0))
    frame.draw_pixel(fill=style.corner_br, at=box.position + Coordinate(box.width-1, box.height-1))
    frame.draw_pixel(fill=style.corner_bl, at=box.position + Coordinate(0, box.height-1))
    child.render(frame, box.resize(-1, -1, -1, -1))

def border_with_title(title: Layout, border_node=border):
    """Border with a title attached on top.

    Args:
        title: Layout to render on top.
        border_node: WrapperNode to put around child layout."""
    def _border_with_title(child: Layout):
        return static_box([
            border_node(child),
            vshrink(padding(0, 0, 1, 1)(title)),
        ])
    return _border_with_title
