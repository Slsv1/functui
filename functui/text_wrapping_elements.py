from functools import reduce, partial, lru_cache
from enum import Enum, auto
from typing import NamedTuple
from itertools import chain
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



def styled_adaptive_text(*string: _Span | str, justify=Justify.LEFT, terminator: str = "...", extend: str = "-"):
    segments = tuple(tuple(i) for i in _span_to_segments(_Span(string, style=Style())))
    def min_size(measure_text, available: Rect):
        lines = list(
            chain.from_iterable(
                wrap_line_default(line, available.width, measure_text) for line in segments
            )
        )
        return Rect(
            max(measure_text("".join(seg.text for seg in line)) for line in lines),
            len(lines)
        )
    return Node(
        func=styled_adaptive_text,
        min_size=min_size,
        render=partial(_styled_adaptive_text_render, segments, justify, terminator),
    )



@lru_cache(32)
def _styled_adaptive_text_render(segments: Iterable[Iterable[_Segment]], justify: Justify, terminator: str, frame: Frame, box: Box):
    res = Result()
    lines = list(
        chain.from_iterable(
            wrap_line_default(line, box.width, frame.measure_text) for line in segments
        )
    )
    for dy, line in enumerate(lines):
        dx = 0
        for segment in line:
            res.draw_string_line(frame.with_style(frame.default_style.combine(segment.style)), segment.text, box.offset + Coordinate(dx, dy))
            dx += frame.measure_text(segment.text)
    return res


# adaptive_text("hej", span("hej", fg=Color.RED), "hejsan guys\n")

def _split_by_spaces(s: str, style: Style):
    r = filter(lambda x: x!='',re.split(r'(\s+)', s))
    return [_Segment(t, style) for t in r]

def _span_to_segments(span: _Span) -> list[list[_Segment]]:
    out = [[]]
    curr_line = 0
    for t in span.text:
        if isinstance(t, str):
            lines = t.splitlines()
            if len(lines) == 1:
                out[curr_line].extend(_split_by_spaces(t, span.style))
                continue
            lines = iter(lines)
            last_elem = next(lines)
            out[curr_line].extend(_split_by_spaces(last_elem, span.style))
            for line in lines:
                curr_line += 1
                out.append(_split_by_spaces(line, span.style))
            continue

        child_res = _span_to_segments(
            _Span(
                text=t.text,
                style=span.style.combine(t.style)
            )
        )
        lines = iter(child_res)
        out[curr_line].extend(next(lines))
        for line in lines:
            curr_line += 1
            out.append(line)
    return out

def span(*text: str | _Span, style: Style):
    return _Span(text, style)

def wrap_line_default(segments: Iterable[_Segment], max_width: int, measure_text: MeasureTextFunc) -> list[list[_Segment]]:
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
            curr_len = 0 if text.isspace() else seg_len
            curr_line += 1
            continue

        out[curr_line].append(segment)
        curr_len += seg_len
    if out[-1] == []:
        del out[-1]
    return out

