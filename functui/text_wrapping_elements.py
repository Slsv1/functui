from functools import reduce, partial, lru_cache
from enum import Enum, auto
from typing import NamedTuple
import re
import math

from .classes import *


class Justify(Enum):
    LEFT = auto()
    CENTER = auto()
    RIGHT = auto()

@dataclass
class _Span:
    text: tuple[str | Self, ...]
    style: Style

class _Segment(NamedTuple):
    text: str
    style: Style

type text_wrap_func = Callable[[Iterable[_Segment], int, MeasureTextFunc], Iterable[Iterable[_Segment]]]
"""takes in a line. If line is too long it will be wrapped. New line characters have no effect on the outcome"""



# def styled_adaptive_text(*string: _StyledStr | str, justify=Justify.LEFT, terminator: str = "...", extend: str = "-"):
#     segments = _span_to_segments(_Span(string, style=Style()))
#     def min_size(measure_text, available: Rect):
#         lines = _split_by_lines_and_add_spaces(measure_text, available.width, words)
#         return Rect(
#             max(measure_text(i) for i in lines),
#             len(lines)
#         )
#     return Node(
#         func=styled_adaptive_text,
#         min_size=min_size,
#         render=partial(_styled_adaptive_text_render, words, justify, terminator),
#     )



# @lru_cache(LRU_MAX_SIZE)
# def _styled_adaptive_text_render(span: _Span, justify: Justify, terminator: str ,frame: Frame, box: Box):
#     ...
# adaptive_text("hej", span("hej", fg=Color.RED), "hejsan guys\n")

def _span_to_segments(span: _Span) -> list[list[_Segment]]:
    out = []
    curr_line = []
    for t in span.text:
        if isinstance(t, str):
            lines = t.splitlines()
            if len(lines) == 1:
                curr_line.append(_Segment(t, span.style))
                continue
            lines = iter(lines)
            last_elem = next(lines)
            curr_line.append(_Segment(last_elem, span.style))
            for line in lines:
                out.append(curr_line)
                curr_line.clear()
                curr_line.append(_Segment(line, span.style))
            continue

        out.extend(
            _span_to_segments(
                _Span(
                    text=t.text,
                    style=span.style.combine(t.style)
                )
            )
        )
    return out

def _wrap_line(segments: Iterable[_Segment], max_width: int, measure_text: MeasureTextFunc):
    out = [[]]
    curr_len = 0
    curr_line = 0
    for segment in segments:
        text = segment.text

        # ignore prefix spaces
        if curr_len == 0 and text.isspace():
            continue
        seg_len = measure_text(text)
        if seg_len + curr_len > max_width:
            if curr_len == 0: # if word is longer than line, then split it
                prefix = segment.text[:max_width]
                postfix = segment.text[max_width:]
                out[curr_line].append(_Segment(prefix, segment.style))
                segment = _Segment(postfix, segment.style)

            # start new line
            out.append([] if text.isspace() else [segment])
            curr_len = 0
            curr_line += 1
            continue
        out[curr_line].append(segment)
