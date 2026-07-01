from enum import Enum, auto
import itertools
from typing import Generator, Iterable, NamedTuple, Self
from dataclasses import dataclass, field
from types import MappingProxyType
from warnings import warn

from functui._geometry import Coordinate
from functui._nav import NavState
from functui._classes import StyleAttr, StyleRule, measure_char, measure_text
from functui._rich_text import Span, span

class TextActionChar(NamedTuple):
    char: str

class TextAction(Enum):
    SUBMIT = auto()
    DELETE_CHAR = auto()
    DELETE_LINE = auto()
    DELETE_WORD_BEFORE_CURSOR = auto()
    NEW_LINE = auto()

    CURSOR_LEFT = auto()
    CURSOR_RIGHT = auto()
    CURSOR_UP = auto()
    CURSOR_DOWN = auto()
    CURSOR_JUMP_LINE_START = auto()
    CURSOR_JUMP_LINE_END = auto()

    SELECT_THOUGH_MOUSE = auto()

class TextFormat(Enum):
    DEFAULT = auto()
    CURSOR = auto()

DEFAULT_TEXT_INPUT_BINDINGS = MappingProxyType({
    "escape": TextAction.SUBMIT,
    "enter": TextAction.NEW_LINE,
    "backspace": TextAction.DELETE_CHAR,
    "left mouse": TextAction.SELECT_THOUGH_MOUSE,

    # cursor
    "left": TextAction.CURSOR_LEFT,
    "right": TextAction.CURSOR_RIGHT,
    "up": TextAction.CURSOR_UP,
    "down": TextAction.CURSOR_DOWN,

    "ctrl+a": TextAction.CURSOR_JUMP_LINE_START,
    "ctrl+e": TextAction.CURSOR_JUMP_LINE_END,
    "ctrl+u": TextAction.DELETE_LINE,
    "ctrl+w": TextAction.DELETE_WORD_BEFORE_CURSOR,
})

def create_text_input_event(key_event: str | None, bindings = DEFAULT_TEXT_INPUT_BINDINGS):
    if key_event is None:
        return
    if len(key_event)== 1:
        return TextActionChar(key_event)
    if key_event in bindings.keys():
        return bindings[key_event]

class WrappedLineSegment(NamedTuple):
    start_at: int
    content: str

def line_wrap_no_newlines(line: str, max: int) -> Generator[WrappedLineSegment]:
    if line == "":
        yield WrappedLineSegment(start_at=0, content="")
    curr_line = []
    dx = 0
    last_line_ended_at_index = 0

    for index, letter in enumerate(line):
        letter_width = measure_char(letter)

        # wrap to next line
        if letter_width + dx > max:
            yield WrappedLineSegment(
                start_at=last_line_ended_at_index,
                content="".join(curr_line)
            )
            last_line_ended_at_index = index
            curr_line.clear()
            dx = 0

        curr_line.append(letter)
        dx += letter_width

    if curr_line:
        yield WrappedLineSegment(
            start_at=last_line_ended_at_index,
            content="".join(curr_line)
        )

def _select_through_mouse(
    relative_mouse_pos: Coordinate,
    wrapped_lines: Iterable[Iterable[WrappedLineSegment]]
) -> None | tuple[int, int]:

    dy = 0
    for line_i, segments in enumerate(wrapped_lines):
        for cursor_index_offset, line_segment in segments:

            if dy != relative_mouse_pos.y:
                dy += 1
                continue

            dx = 0
            char_i = 0
            for char_i, char in enumerate(line_segment):
                dx += measure_char(char)

                if Coordinate(dx, dy) == relative_mouse_pos:
                    return (line_i, cursor_index_offset + char_i + 1)
            # even if we click of the line, then select at end of line
            return (line_i, cursor_index_offset + char_i + 1)

@dataclass
class TextInput:
    lines: list[str]
    cursor_index: int = 0
    cursor_line: int = 0
    submitted: int = False
    _wrapped_lines: list[list[WrappedLineSegment]] = field(default_factory=list)

    # maybe nav_data instead for nav, node_id?
    def update(self, action: TextAction | TextActionChar | None, nav: NavState, node_id):

        # create _wrapped_lines

        if self.submitted:
            return

        curr_line = self.lines[self.cursor_line]
        match action:
            case TextAction.SELECT_THOUGH_MOUSE: # set cursor_line and pos to approprita place
                if nav.result_data is not None and nav.is_hovered(node_id):
                    box_data = nav.result_data.box_data[node_id]

                    # defined in local space
                    mouse_pos = nav.mouse_position - box_data.box.position
                    res = _select_through_mouse(mouse_pos, self._wrapped_lines)
                    if res is not None:
                        self.cursor_line, self.cursor_index = res

            case TextAction.SUBMIT:
                self.submitted = True

            case TextAction.CURSOR_RIGHT:
                if self.cursor_index != len(curr_line):
                    self.cursor_index += 1

            case TextAction.CURSOR_LEFT:
                if self.cursor_index != 0:
                    self.cursor_index -= 1

            case TextAction.CURSOR_DOWN:
                if self.cursor_line < len(self.lines) -1:
                    self.cursor_line += 1

                # adjust corsor pos if out of bounds
                new_line = self.lines[self.cursor_line]
                if self.cursor_index >= len(new_line):
                    self.cursor_index = len(new_line)

            case TextAction.CURSOR_UP:
                if self.cursor_line != 0:
                    self.cursor_line -= 1

                # adjust corsor pos if out of bounds
                new_line = self.lines[self.cursor_line]
                if self.cursor_index >= len(new_line):
                    self.cursor_index = len(new_line)

            case TextAction.DELETE_CHAR:
                if self.cursor_index != 0 and len(curr_line):
                    self.lines[self.cursor_line] = "".join([curr_line[:self.cursor_index-1], curr_line[self.cursor_index:]])
                    self.cursor_index -= 1

            case TextAction.DELETE_LINE:
                self.lines[self.cursor_line] = ""
                self.cursor_index = 0

            case TextAction.NEW_LINE:

                self.lines.insert(self.cursor_line+1, "")
                self.cursor_line += 1

        if isinstance(action, TextActionChar):
            if action.char == "\n":
                raise AssertionError("lol")

            # add to current line, unless newline_char
            self.lines[self.cursor_line] = "".join([curr_line[:self.cursor_index], action.char, curr_line[self.cursor_index:]])
            self.cursor_index += 1

        if nav.result_data is not None and node_id in nav.result_data.box_data:
            width = nav.result_data.box_data[node_id].box.width
            self._wrapped_lines.clear()
            for line in self.lines:
                self._wrapped_lines.append(list(line_wrap_no_newlines(line, width)))

    def _get_cursor_visual_position(self) -> Coordinate:
        y = x = 0

        for i in range(0, self.cursor_line):
            segments = self._wrapped_lines[i]
            y += len(segments)

        if self.cursor_line < len(self._wrapped_lines):
            line = self._wrapped_lines[self.cursor_line]
        else:
            return Coordinate(0, 0)

        for i, segment in enumerate(line):
            if (i+1 != len(line))\
                and (next_segment := line[i+1])\
                and (next_segment.start_at < self.cursor_index):
                continue

            x += measure_text(segment.content[segment.start_at:self.cursor_index])
            break
        return Coordinate(x, y)

    @property
    def cursor_visual_offset(self):
        return self._get_cursor_visual_position()

    def view_lines(self) -> Generator[tuple[tuple[TextFormat, str], ...]]:
        x, y = self.cursor_visual_offset

        dy = 0
        for line in self._wrapped_lines:
            for segment in line:
                if dy != y:
                    yield ((TextFormat.DEFAULT, segment.content),)

                    dy += 1
                    continue

                content = segment.content
                if measure_text(content) == x:
                    content += " "


                yield (
                    (TextFormat.DEFAULT, content[:x]),
                    (TextFormat.CURSOR, content[x]),
                    (TextFormat.DEFAULT, content[x+1:]),
                )
                dy += 1

    # def view_as_span(self, cursor_style: StyleRule=StyleRule(add_attrs=StyleAttr.REVERSE)) -> Span:
    #     curr_line = self.lines[self.cursor_line]
    #
    #     if self.cursor_pos == len(curr_line):
    #         curr_line += " "
    #
    #     return span(
    #         v[:self.cursor_pos],
    #         span(v[self.cursor_pos], rule=cursor_style),
    #         v[self.cursor_pos+1:],
    #         rule=StyleRule()
    #     )
