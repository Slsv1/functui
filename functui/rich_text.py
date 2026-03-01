from functools import reduce, partial, lru_cache, cache
from enum import Enum, auto
from typing import NamedTuple, Iterable, Self, Callable
from dataclasses import dataclass
from itertools import chain
import re
import math


from .classes import *


# This is a mess, but if it works, dont fix it.

class Justify(Enum):
    """Text Justification.

    Attributes:
        LEFT:
        CENTER:
        RIGHT:
    """
    LEFT = auto()
    CENTER = auto()
    RIGHT = auto()


@dataclass(frozen=True)
class Span:
    text: tuple[str | Self, ...]
    rule: StyleRule


class Segment(NamedTuple):
    text: str
    rule: StyleRule
    length: int


@dataclass(frozen=True, eq=True)
class Group:
    """Represents a connected span of text, like a word or a space."""
    segments: tuple[Segment, ...]
    is_space: bool
    @property
    def length(self):
        return sum(i.length for i in self.segments)

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
                    Segment("".join(allowed_letters), segment.rule, total_letter_length)
                )
            overflowing_segments.insert(
                0, 
                Segment(
                    "".join(overflowing_letters),
                    segment.rule,
                    segment.length - total_letter_length
                )
            )
            break

        if not overflowing_segments:
            return [self]
        return [
            self.__class__(tuple(allowed_segments), self.is_space),
            self.__class__(tuple(overflowing_segments), self.is_space)
        ]


TextWrapFunc = Callable[[Iterable[Segment], int, MeasureTextFunc], Iterable[Iterable[Segment]]]
"""takes in a line. If line is too long it will be wrapped. New line characters have no effect on the outcome"""


def rich_text(*string: Span | str):
    """A data node for text that can be styled.

    Args:
        *string:
            The text content. Parts of content can be wrapped in a :obj:`span` for styling.
    """
    span = Span(string, rule=StyleRule())
    def min_size(measure_text, available: Rect):
        groups = tuple(tuple(i) for i in _span_to_lines(span, measure_text))
        return Rect(
            max((sum(group.length for group in line) for line in groups), default=0),
            len(groups)
        )
    return Layout(
        func=rich_text,
        min_size=min_size,
        render=partial(_rich_text_render, span),
    )

@lru_cache(LRU_MAX_SIZE)
def _rich_text_render(span: Span, frame: Frame, box: Box):
    if box.width <= 4:
        return Result()

    lines = _span_to_lines(span, frame.measure_text)
    res = Result()

    for dy, line in enumerate(lines):
        if dy == box.height:
            break
        dx = 0
        for segment in chain.from_iterable(g.segments for g in line):
            frame.with_style(frame.default_style.apply_rule(segment.rule)).draw_string_line(
                segment.text, box.position + Coordinate(dx, dy)
            )
            dx += frame.measure_text(segment.text)
    return res

def adaptive_text(*string: Span | str, justify=Justify.LEFT, soft_hyphen: str = "-"):
    """A data node for text that can be wrapped and styled.

    Args:
        *string:
            The text content. Parts of content can be wrapped in a :obj:`span` for styling.
        justify:
            Text justification.
        soft_hyphen:
            Display to signal a word being wrapped between to line.
    """
    span = Span(string, rule=StyleRule())
    def min_size(measure_text, available: Rect):
        groups = tuple(tuple(i) for i in _span_to_lines(span, measure_text))
        # longest_word = max(i.length for i in chain.from_iterable((l for l in groups)))
        lines = list(
            chain.from_iterable(
                wrap_line_default(line, available.width, measure_text, soft_hyphen) for line in groups
            )
        )
        return Rect(
            max((sum(group.length for group in line) for line in lines), default=0),
            len(lines)
        )
    return Layout(
        func=adaptive_text,
        min_size=min_size,
        render=partial(_adaptive_text_render, span, justify, soft_hyphen),
    )



@lru_cache(LRU_MAX_SIZE)
def _adaptive_text_render(span: Span, justify: Justify, soft_hyphen: str, frame: Frame, box: Box):
    if box.width <= 1:
        return Result()

    groups = _span_to_lines(span, frame.measure_text)
    res = Result()
    lines = list(
        chain.from_iterable(
            wrap_line_default(line, box.width, frame.measure_text, soft_hyphen) for line in groups
        )
    )
    for dy, line in enumerate(lines):
        if dy == box.height:
            break
        dx = 0
        if justify == Justify.RIGHT:
            dx = box.width - sum(i.length for i in line)
        elif justify == Justify.CENTER:
            dx = (box.width - sum(i.length for i in line)) // 2
        for segment in chain.from_iterable(g.segments for g in line):
            frame.with_style(frame.default_style.apply_rule(segment.rule)).draw_string_line(
                segment.text, box.position + Coordinate(dx, dy)
            )
            dx += frame.measure_text(segment.text)
    return res


# adaptive_text("hej", span("hej", fg=Color.RED), "hejsan guys\n")
@cache
def _split_by_spaces(s: str, rule: StyleRule, measure_text: MeasureTextFunc):
    r = filter(lambda x: x!='',re.split(r'(\s+)', s))
    return [Segment(t, rule, measure_text(t)) for t in r]

def _append_segment_to_line(line: list[Group], seg: Segment):
    if len(line) and (seg.text.isspace() == line[-1].is_space):
        line[-1] = line[-1].extend(seg)
        return
    line.append(Group((seg,), seg.text.isspace()))

def _extend_line_with_segments(line: list[Group], segments: list[Segment]):
    for s in segments:
        _append_segment_to_line(line, s)

@cache
def _span_to_lines(span: Span, measure_text: MeasureTextFunc) -> list[list[Group]]:
    out_lines = [[]]
    for t in span.text:
        if isinstance(t, str):
            lines = t.splitlines()
            if len(lines) <= 1:
                _extend_line_with_segments(
                    out_lines[-1],
                    _split_by_spaces(t, span.rule, measure_text)
                )
                continue
            # elif len(lines) == 0:
            #     return [[]]

            lines_iter = iter(lines)
            last_elem = next(lines_iter)
            _extend_line_with_segments(
                out_lines[-1],
                _split_by_spaces(last_elem, span.rule, measure_text)
            )
            for line in lines_iter:
                out_lines.append([])
                _extend_line_with_segments(
                    out_lines[-1],
                    _split_by_spaces(line, span.rule, measure_text)
                )
            continue

        child_res = _span_to_lines(
            Span(
                text=t.text,
                rule=span.rule | t.rule
            ),
            measure_text
        )
        child_lines_iter = iter(child_res)
        first_child_line = next(child_lines_iter)
        first_child_group = first_child_line[0]
        _extend_line_with_segments(
            out_lines[-1],
            list(first_child_group.segments)
        )
        out_lines[-1].extend(first_child_line[1:])
        for line in child_lines_iter:
            out_lines.append(line)
    return out_lines

def span(*text: str | Span, rule: StyleRule):
    """Style a text segment in an :obj:`adaptive_text` node."""
    return Span(text, rule)

def _wrap_word(
    group: Group,
    out: list[list[Group]],
    max_width: int,
    continuation_str_width: int,
    continuation_str: str,
    measure_text: MeasureTextFunc
):
    prefix, left_over = group.split(max_width - continuation_str_width, measure_text)
    # if nothing fits
    if len(prefix.segments) == 0:
        return # dont even try
    segments = (*prefix.segments, Segment(
        continuation_str, 
        prefix.segments[-1].rule,
        continuation_str_width
    ))
    prefix = Group(segments, False)
    out[-1].append(prefix)
    if left_over.length > max_width:
        out.append([])
        _wrap_word(
            left_over,
            out,
            max_width,
            continuation_str_width,
            continuation_str,
            measure_text
        )
        return
    out.append([left_over])


def wrap_line_default(line: Iterable[Group], max_width: int, measure_text: MeasureTextFunc, continuation_str: str="-") -> list[list[Group]]:
    continuation_str_width = measure_text(continuation_str)
    out = [[]]
    curr_len = 0
    for group in line:
        # ignore trailing space
        if group.is_space and curr_len == 0:
            continue

        if group.length + curr_len > max_width:
            if curr_len == 0 and not group.is_space: # if word is longer than line, then split it
                _wrap_word(
                    group,
                    out,
                    max_width,
                    continuation_str_width,
                    continuation_str,
                    measure_text
                )
                
                curr_len = out[-1][-1].length if len(out[-1]) else 0
                continue
            # start new line, if it does not start with space
            out.append([] if group.is_space else [group])
            curr_len = 0 if group.is_space else group.length
            continue

        out[-1].append(group)
        curr_len += group.length

    return out if not out[-1] == [] else out[:-1]
