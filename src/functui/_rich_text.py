from functools import reduce, partial, lru_cache, cache
from enum import Enum, auto
import itertools
from typing import NamedTuple, Iterable, Self, Callable, Generator, Sequence
from dataclasses import dataclass
from itertools import chain
import re
import math


from functui._classes import StyleRule, MeasureTextFunc, Frame, Layout, even_divide, measure_char
from functui._geometry import Box, Rect, Coordinate


# This is a mess, but if it works, dont break it it.
# Not as much anymore though!

class Allignment(Enum):
    """Text Justification.

    Used by :func:`functui.nodes.adaptive_text`

    Attributes:
        LEFT:
        CENTER:
        RIGHT:
        JUSTIFIED:
    """
    LEFT = auto()
    CENTER = auto()
    RIGHT = auto()
    JUSTIFIED = auto()


# TODO: maybe someday
# @dataclass(frozen=True)
# class TokenWrapRules:
#     illigal_start_chars: tuple[str, ...]
#     illigal_end_chars: tuple[str, ...]




type Token = tuple[str, int, int, bool]
"""content, start_at, width, is_space"""

def split_by_tokens(line: str, white_space_chars: tuple[str, ...]) -> Generator[Token]:

    if len(line) == 0: return

    token_is_whitespace = line[0] in white_space_chars
    token = []
    token_width = 0
    token_start_at =0

    for index, char in enumerate(line):
        char_width = measure_char(char)

        # next token
        if token_is_whitespace != (char in white_space_chars):
            yield ("".join(token), token_start_at, token_width, token_is_whitespace)

            # set new token data
            token_width = 0
            token.clear()
            token_is_whitespace = not token_is_whitespace
            token_start_at = index

        # add char to token
        token.append(char)
        token_width += char_width

    if token:
        yield("".join(token), token_start_at, token_width, token_is_whitespace)

def wrap_tokens_if_possible(token_gen: Generator[Token], max_width: int) -> Generator[Token]:
    # TODO TODO TODO: this is hacky
    if max_width <= 1:
        yield from token_gen
        return

    next_token = next(token_gen)

    while True:
        token_data, token_start_at, token_width, token_is_whitespace = next_token

        # single token too long for line, then wrap
        if token_width > max_width: 
            end, width = _find_fit_str(token_data, max_width)

            token_start = token_data[:end]

            yield (token_start, token_start_at, width, token_is_whitespace)

            token_end = token_data[end:]
            next_token = (token_end, token_start_at + len(token_start), token_width-width, token_is_whitespace)

        else:
            yield next_token

            try:
                next_token = next(token_gen)
            except StopIteration:
                return


def _find_fit_str(text: str | list[str], max_width: int) -> tuple[int, int]:
    width = 0

    for i, char in enumerate(text):
        char_width = measure_char(char)
        if width + char_width > max_width:
            return i, width
        width += char_width

    return len(text), width


# int is start at index
def wrap_line_keep_space(
    content: str,
    max_width: int,
    white_space_chars: tuple[str, ...] = (" ",),
) -> Generator[tuple[Token, ...]]:
    if max_width == 0 or len(content) == 0: return
    line = []
    line_width = 0
    for token in wrap_tokens_if_possible(split_by_tokens(content, white_space_chars), max_width):
        _, _, token_width, _ = token
        # wrap line
        if token_width + line_width > max_width:
            yield tuple(line)
            line.clear()
            line_width = 0
        # add token to line
        line_width += token_width
        line.append(token)
    if line:
        yield tuple(line)

def wrap_line_trim_ends(
    content: str,
    max_width: int,
    white_space_chars: tuple[str, ...] = (" ",),
) -> Generator[tuple[Token, ...]]:
    if max_width == 0 or len(content) == 0: return
    line = []
    line_width = 0
    for token in wrap_tokens_if_possible(split_by_tokens(content, white_space_chars), max_width):
        _, _, token_width, token_is_whitespace = token
        # wrap line
        if token_width + line_width > max_width:
            # white space
            if line and line[-1][3]:
                line = line[:-1]

            yield tuple(line)
            line.clear()
            line_width = 0
            if token_is_whitespace:
                continue
        # add token to line
        line_width += token_width
        line.append(token)
    if line:
        yield tuple(line)

def token_sum(line: Iterable[Token]):
    return sum(i[2] for i in line)

def merge_tokens(line: Iterable[Token]):
    return "".join(i[0] for i in line)

def justify_tokens(line: Sequence[Token], to_fill: int) -> Generator[Token]:
    rations = even_divide(to_fill, len(line) - 1)

    for i, token in enumerate(line[:-1]):
        yield token
        space_len = rations[i]
        yield (" "*space_len, token[1],space_len, True)
    yield line[-1]

def _adaptive_text_render(
    lines: tuple[str, ...],
    allignment: Allignment,
    trim_ends: bool,
    white_space_chars: tuple[str, ...],
    frame: Frame,
    box: Box
):
    wrap_line = wrap_line_trim_ends if trim_ends else wrap_line_keep_space
    for line_i, line in enumerate(lines):
        for wrapped_line_i, wrapped_line in enumerate(wrap_line(line, box.width, white_space_chars)):
            line_width = token_sum(wrapped_line)
            dy = line_i + wrapped_line_i

            if dy == box.height:
                break

            if allignment == Allignment.RIGHT:
                dx = box.width - line_width
                frame.draw_string_line(merge_tokens(wrapped_line), box.position + Coordinate(dx, dy))
                continue

            if allignment == Allignment.CENTER:
                dx = (box.width - line_width) // 2
                frame.draw_string_line(merge_tokens(wrapped_line), box.position + Coordinate(dx, dy))
                continue

            if allignment == Allignment.JUSTIFIED and len(wrapped_line) > 1: # allignment == Allignment.JUSTIFIED:
                left_over = box.width - line_width
                wrapped_line = justify_tokens(wrapped_line, left_over)

            dx = 0
            frame.draw_string_line(merge_tokens(wrapped_line), box.position + Coordinate(dx, dy))

def adaptive_text(
        string: str, / , *,
        allignment = Allignment.LEFT,
        trim_ends = True,
        white_space_chars: tuple[str, ...] = (" ",)
):
    """A data node for text that can be wrapped."""
    lines = tuple(string.splitlines())

    wrap_line = wrap_line_trim_ends if trim_ends else wrap_line_keep_space

    def min_size(measure_text, available: Rect):
        lines_of_tokens = list(itertools.chain.from_iterable(
            wrap_line(line, available.width, white_space_chars) for line in lines
        ))

        return Rect(
            max((token_sum(line) for line in lines_of_tokens), default=0),
            len(lines_of_tokens)
        )

    return Layout(
        func=adaptive_text,
        min_size=min_size,
        render=partial(_adaptive_text_render, lines, allignment, trim_ends, white_space_chars),
    )


if __name__ == '__main__':
    from functui import open_terminal, Screen, NavState, LOREM, render_fit_terminal, Color4, Allignment, NavUpdateScrollable
    from functui.nodes import *

    I_AM_A_CAT = "吾輩は猫である。名前はまだ無い。" * 20

    with open_terminal() as term:
        nav = NavState()
        scr = Screen()
        while True:
            layout = nav.vsplit(
                node_id="split",
                left=hbox_flex([vbox([
                    text("LEFT") | fg(Color4.BLUE),
                    adaptive_text(LOREM, allignment=Allignment.LEFT) | hpadding,
                    text("RIGHT") | fg(Color4.BLUE),
                    adaptive_text(LOREM, allignment=Allignment.RIGHT) | hpadding,
                    text("CENTER") | fg(Color4.BLUE),
                    adaptive_text(LOREM, allignment=Allignment.CENTER) | hpadding,
                    text("JUSTIFIED") | fg(Color4.BLUE),
                    adaptive_text(LOREM, allignment=Allignment.JUSTIFIED) | hpadding,
                    text("LEFT WIDE") | fg(Color4.BLUE),
                    adaptive_text(I_AM_A_CAT) | hpadding,
                    text("RIGHT WIDE") | fg(Color4.BLUE),
                    adaptive_text(I_AM_A_CAT, allignment=Allignment.RIGHT) | hpadding,
                    text("CENTER WIDE") | fg(Color4.BLUE),
                    adaptive_text(I_AM_A_CAT, allignment=Allignment.CENTER) | hpadding,
                    text("JUSTIFIED WIDE") | fg(Color4.BLUE),
                    adaptive_text(I_AM_A_CAT, allignment=Allignment.JUSTIFIED) | hpadding,
                ])  | nav.vscrollable("hej")| flex, nav.vscroll_bar("hej", hide_if_unnecessary=True)]),
                right=adaptive_text("<-- this can be dragged") | vcenter
            ) | border

            result = render_fit_terminal(term, scr, layout)
            event = term.wait_for_input()
            nav_cmds = []

            if event.key_event == "ctrl+c":
                break
            elif event.key_event == "j" and (scroll_data := nav.try_scrollable_data("hej")):
                nav_cmds.append(NavUpdateScrollable("hej", scroll_data.at_y + 1))
            elif event.key_event == "k" and (scroll_data := nav.try_scrollable_data("hej")):
                nav_cmds.append(NavUpdateScrollable("hej", scroll_data.at_y - 1))

            nav.update(result, event, commands=nav_cmds)
