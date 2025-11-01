from functools import reduce, partial, lru_cache, cache
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
class Span:
    text: tuple[str | Self, ...]
    style: Style


class Segment(NamedTuple):
    text: str
    style: Style
    length: int


@dataclass(frozen=True)
class Group:
    segments: tuple[Segment, ...]
    is_space: bool
    @cache
    def length(self):
        return sum(i.length for i in segments)
    def extend(self, seg: Segment):
        return self.__class__((*self.segments, seg), self.is_space)

    def split(self, max_width: int, measure_text: MeasureTextFunc) -> list[Self]:
        total_length = 0
        allowed_segments = []
        overflowing_segments = list(self.segments)
        for segment in self.segments:
            if total_length + segment.length <= max_width:
                total_length += segment.length
                allowed_segments.append(segment)
                del overflowing_segments[0]
                continue


            # handle overflowing segmend
            del overflowing_segments[0]
            allowed_letters = []
            overflowing_letters = list(segment.text)
            total_letter_length = 0

            for i, letter in enumerate(segment.text):
                letter_len = measure_text(letter)
                if total_length + total_letter_length + letter_len <= max_width:
                    allowed_letters.append(letter)
                    del overflowing_letters[0]
                    total_letter_length += letter_len
                    continue

            if allowed_letters:
                allowed_segments.append(
                    Segment("".join(allowed_letters), segment.style, total_letter_length)
                )
            overflowing_segments.append(
                Segment(
                    "".join(overflowing_letters),
                    segment.style,
                    segment.length - total_letter_length
                )
            )
            break

        if not overflowing_segments:
            return [self]
        return [
            Group(tuple(allowed_segments), self.is_space),
            Group(tuple(overflowing_segments), self.is_space)
        ]





text_wrap_func = Callable[[Iterable[Segment], int, MeasureTextFunc], Iterable[Iterable[Segment]]]
"""takes in a line. If line is too long it will be wrapped. New line characters have no effect on the outcome"""



def adaptive_text(*string: _Span | str, justify=Justify.LEFT, terminator: str = "...", extend: str = "-"):
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
        func=adaptive_text,
        min_size=min_size,
        render=partial(_adaptive_text_render, segments, justify, terminator),
    )



@lru_cache(32)
def _adaptive_text_render(segments: Iterable[Iterable[Segment]], justify: Justify, terminator: str, frame: Frame, box: Box):
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

def _split_by_spaces(s: str, style: Style, measure_text: MeasureTextFunc):
    r = filter(lambda x: x!='',re.split(r'(\s+)', s))
    return [Segment(t, style, measure_text(t)) for t in r]

def _append_segment_to_line(line: list[Group], seg: Segment):
    if len(line) and (seg.text.isspace() == line[-1].is_space):
        line[-1] = line[-1].extend(seg)
        return
    line.append(Group((seg,), seg.text.isspace()))

def _extend_line_with_segments(line: list[Group], segments: list[Segmen]):
    for s in segments:
        _append_segment_to_line(line, s)

def _span_to_lines(span: Span, measure_text: MeasureTextFunc) -> list[list[Group]]:
    out_lines = [[]]
    for t in span.text:
        if isinstance(t, str):
            lines = t.splitlines()
            if len(lines) == 1:
                _extend_line_with_segments(
                    out_lines[-1],
                    _split_by_spaces(t, span.style, measure_text)
                )
                continue

            lines = iter(lines)
            last_elem = next(lines)
            _extend_line_with_segments(
                out_lines[-1],
                _split_by_spaces(last_elem, span.style, measure_text)
            )
            for line in lines:
                out.append([])
                _extend_line_with_segments(
                    out_lines[-1],
                    _split_by_spaces(last_elem, span.style, measure_text)
                )
            continue

        child_res = _span_to_lines(
            Span(
                text=t.text,
                style=span.style.combine(t.style)
            ),
            measure_text
        )
        lines = iter(child_res)
        out_lines[-1].extend(next(lines))
        for line in lines:
            out_lines.append(line)
    return out_lines

def span(*text: str | _Span, style: Style):
    return Span(text, style)

def wrap_line_default(groups: Iterable[Group], max_width: int, measure_text: MeasureTextFunc) -> list[list[Group]]:
    out = [[]]
    curr_len = 0
    for group in groups:
        if group.length + curr_len > max_width:
            if curr_len == 0 and not group.is_space: # if word is longer than line, then split it

                # prefix = segment.text[:max_width]
                # postfix = segment.text[max_width:]
                # out[curr_line].append(Segment(prefix, segment.style))
                # segment = Segment(postfix, segment.style)
                pass
            # start new line, if it does not start with space
            out.append([] if group.is_space else [group])
            curr_len = 0 if group.isspace else group.length
        else:
            out[-1].append(segment)
            curr_len += group.length
    return out

