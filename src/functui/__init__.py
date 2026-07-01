# functui public api

from ._io import render_fit_terminal, render_ansi, render_fit_screen
from ._xterm import open_terminal, TerminalIO, TerminalContext, TerminalFeatures, InputEvent

from ._geometry import Box, Coordinate, Rect

from ._nav import NavState, hnav, vnav, DEFAULT_NAV_BINDINGS, NavContainer
from ._border import BorderStyle, BORDER_DOUBLE, BORDER_REGULAR, BORDER_THICK, BORDER_ROUNDED

from ._classes import StyleRule, StyleAttr, ComputedStyle, NodeID
from ._classes import WrapperNode, Layout, Screen, intersperse, ResultData, BoxData

from ._color import Color, Color4, TerminalColor, ColorTheme, rgb, rgba, hsl, hex
from ._color import DRACULA_COLOR_THEME

LOREM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

__all__ = (
    # io
    'InputEvent',
    'TerminalIO',
    'TerminalContext',
    'TerminalFeatures',
    'open_terminal',
    'render_fit_terminal',
    'render_fit_screen',
    'render_ansi',

    # geometry
    'Box',
    'Coordinate',
    'Rect',

    # nav
    "NavState",
    "NavContainer",
    "vnav",
    "hnav",
    "DEFAULT_NAV_BINDINGS",
    "NodeID",

    # border
    'BorderStyle',

    'BORDER_DOUBLE',
    'BORDER_REGULAR',
    'BORDER_ROUNDED',
    'BORDER_THICK',

    # core classes
    'Layout',
    'Screen',
    'WrapperNode',
    'ResultData',
    'BoxData',
    'StyleRule',
    'ComputedStyle',
    'StyleAttr',

    # color
    'ColorTheme',
    'Color',
    'Color4',
    'TerminalColor',
    'rgb',
    'rgba',
    'hsl',
    'hex',

    'DRACULA_COLOR_THEME',

    # util
    'intersperse',
    'LOREM',
)
