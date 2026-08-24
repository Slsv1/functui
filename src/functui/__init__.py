# functui public api

from ._io import render_fit_terminal, render_simple, render_fit_screen
from ._xterm import open_terminal, TerminalIO, TerminalContext, TerminalFeatures, InputEvent

from ._geometry import Box, Coordinate, Rect

from ._nav import NavState, hnav, vnav, DEFAULT_NAV_BINDINGS, NavContainer, NavUpdateScrollable, nav_parse_event, NavScrollableData, NavAction
from ._border import BorderStyle, BORDER_DOUBLE, BORDER_REGULAR, BORDER_THICK, BORDER_ROUNDED

from ._classes import StyleRule, StyleAttr, ComputedStyle, NodeID
from ._classes import WrapperNode, Layout, Screen, intersperse, ResultData, BoxData, Frame

from ._color import Color, Color4, TerminalColor, ColorTheme, rgb, rgba, hsl, hex, BgChars
from ._color import COLOR_THEMES, DRACULA_COLOR_THEME, NORD_COLOR_THEME, GRUVBOX_COLOR_THEME, SOLARIZED_COLOR_THEME

from ._auto_load import VAutoLoad

from ._textfield import TextInput, DEFAULT_TEXT_INPUT_BINDINGS, text_input_parse_event, TextAction, TextActionPaste, TextActionChar
from ._rich_text import Allignment

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
    'render_simple',

    # geometry
    'Box',
    'Coordinate',
    'Rect',

    # nav
    "NavState",
    "NavContainer",
    "NavUpdateScrollable",
    "vnav",
    "hnav",
    "DEFAULT_NAV_BINDINGS",
    'NavAction',
    "NodeID",
    "NavScrollableData",
    "nav_parse_event",

    # autoload
    'VAutoLoad',

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
    'Frame',

    # color
    'ColorTheme',
    'Color',
    'Color4',
    'TerminalColor',
    'rgb',
    'rgba',
    'hsl',
    'hex',
    'BgChars',

    'DRACULA_COLOR_THEME',
    'NORD_COLOR_THEME',
    'SOLARIZED_COLOR_THEME',
    'GRUVBOX_COLOR_THEME',

    'COLOR_THEMES',


    # util
    'intersperse',
    'LOREM',

    # rich text
    'Allignment',

    # text input
    'TextInput',
    'text_input_parse_event',
    'DEFAULT_TEXT_INPUT_BINDINGS',
    'TextAction',
    'TextActionChar',
    'TextActionPaste',
)
