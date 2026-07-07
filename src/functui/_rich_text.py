from functools import reduce, partial, lru_cache, cache
from enum import Enum, auto
from typing import NamedTuple, Iterable, Self, Callable, Generator
from dataclasses import dataclass
from itertools import chain
import re
import math


from functui._classes import StyleRule, MeasureTextFunc, Frame, Layout, measure_char
from functui._geometry import Box, Rect, Coordinate


# This is a mess, but if it works, dont fix it.

class Allignment(Enum):
    """Text Justification.

    Attributes:
        LEFT:
        CENTER:
        RIGHT:
    """
    LEFT = auto()
    CENTER = auto()
    RIGHT = auto()
    # JUSTIFIED = auto()


@dataclass(frozen=True)
class TokenWrapRules:
    illigal_start_chars: tuple[str, ...]
    illigal_end_chars: tuple[str, ...]

@dataclass(frozen=True)
class TextWrapConfig:
    soft_hyphen: str = "-"
    white_space_chars: str = " "



type Token = tuple[str, int, bool]
type TokenGenerator = Generator[tuple[list[str], int, bool]]
def split_by_tokens(line: str, white_space_chars: tuple[str, ...]) -> TokenGenerator:
    """split line by tokens
    Return value consists of: token data, token width, is token whitespace"""

    if len(line) == 0:
        yield ([""], 0, True)

    token_is_whitespace = line[0] in white_space_chars
    token = []
    token_width = 0

    for char in line:
        char_width = measure_char(char)

        # next token
        if token_is_whitespace != (char in white_space_chars):
            yield (token, token_width, token_is_whitespace)
            # set new token data
            token_width = 0
            token.clear()
            token_is_whitespace = not token_is_whitespace

        # add char to token
        token.append(char)
        token_width += char_width

    if token:
        yield(token, token_width, token_is_whitespace)

def wrap_tokens(token_gen: TokenGenerator, max_width: int):
    next_token = next(token_gen)

    while True:
        token_data, token_width, token_is_whitespace = next_token

        # single token too long for line, then wrap
        if token_width > max_width: 
            end, width = _find_fit_str(token_data, max_width)

            token_start = token_data[:end]

            yield (token_start, width, token_is_whitespace)

            token_end = token_data[end:]
            next_token = (token_end, token_width-width, token_is_whitespace)

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
def wrap_line(
    content: str,
    max_width: int,
    white_space_chars: tuple[str, ...] = (" ",)
) -> Generator[tuple[int, str, int]]:

    if max_width == 0 or len(content) == 0:
        yield (0, "", 0)
        return

    line_start_at_index = 0
    next_start_at_index = 0
    line = []
    line_width = 0

    for token in wrap_tokens(split_by_tokens(content, white_space_chars), max_width):
        token_data, token_width, token_is_whitespace = token

        next_start_at_index += len(token_data)

        # wrap line
        if token_width + line_width > max_width:
            token_str = "".join(line)

            yield (line_start_at_index, token_str, line_width)

            line_start_at_index = next_start_at_index
            line.clear()
            line_width = 0

            # discard whitespace tokens
            if token_is_whitespace:
                continue

        # add token to line
        line_width += token_width
        line.extend(token_data)


    if line:
        yield(line_start_at_index, "".join(line), line_width)

def wrap_str(
    content: str,
    max_width: int,
    white_space_chars: tuple[str, ...] = (" ",)
) -> Generator[tuple[int, str, int]]:
    for line in content.splitlines(keepends=True):
        yield from wrap_line(line, max_width, white_space_chars)



def _adaptive_text_render(
    string: str,
    allignment: Allignment,
    white_space_chars: tuple[str, ...],
    frame: Frame,
    box: Box
):
    for dy, (_, line, line_width) in enumerate(wrap_str(string, box.width, white_space_chars)):
        if dy == box.height:
            break
        dx = 0

        if allignment == Allignment.RIGHT:
            dx = box.width - line_width
        elif allignment == Allignment.CENTER:
            dx = (box.width - line_width) // 2

        frame.draw_string_line(line, box.position + Coordinate(dx, dy))

def adaptive_text(
        string: str, / , *,
        allignment=Allignment.LEFT,
        white_space_chars: tuple[str, ...] = (" ",)
):
    """A data node for text that can be wrapped."""
    def min_size(measure_text, available: Rect):
        lines = list(wrap_str(string, available.width))

        return Rect(
            max((measure_text(line[1]) for line in lines), default=0),
            len(lines)
        )

    return Layout(
        func=adaptive_text,
        min_size=min_size,
        render=partial(_adaptive_text_render, string, allignment, white_space_chars),
    )


if __name__ == '__main__':
    from functui import open_terminal, Screen, NavState, LOREM, render_fit_terminal, Color4, Allignment
    from functui.nodes import *

    I_AM_A_CAT = "吾輩は猫である。名前はまだ無い。"

    with open_terminal() as term:
        nav = NavState()
        scr = Screen()
        while True:
            layout = nav.vsplit(
                node_id="split",
                left=vbox([
                    text("LEFT") | fg(Color4.BLUE),
                    adaptive_text(I_AM_A_CAT * 20),
                    text("RIGHT") | fg(Color4.BLUE),
                    adaptive_text(LOREM, allignment=Allignment.RIGHT),
                    text("CENTER") | fg(Color4.BLUE),
                    adaptive_text(LOREM, allignment=Allignment.CENTER),
                ]),
                right=adaptive_text("<-- this can be dragged") | vcenter
            ) | border
            result = render_fit_terminal(term, scr, layout)
            event = term.block_until_input()

            if event.key_event == "ctrl+c":
                break
            nav.update(result, event, mouse_position=event.mouse_position_event)

            
