from enum import Enum, auto
from functools import partial
import itertools
from typing import Callable, Generator, Iterable, NamedTuple, Self
from dataclasses import dataclass, field
from types import MappingProxyType
from warnings import warn

from functui._geometry import Coordinate
from functui._nav import NavState
from functui._classes import NodeID, StyleAttr, StyleRule, clamp, measure_char, measure_text
from functui._rich_text import Span, span
from functui._xterm import InputEvent
from functui._common import vbox, text, hbox, style, hoverable, empty

class TextActionChar(NamedTuple):
    char: str

class TextActionPaste(NamedTuple):
    content: str

class TextAction(Enum):
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

class TextInputStyle(Enum):
    DEFAULT = auto()
    CURSOR = auto()

DEFAULT_TEXT_INPUT_BINDINGS = MappingProxyType({
    "enter": TextAction.NEW_LINE,
    "left mouse": TextAction.SELECT_THOUGH_MOUSE,

    # cursor
    "left": TextAction.CURSOR_LEFT,
    "right": TextAction.CURSOR_RIGHT,
    "up": TextAction.CURSOR_UP,
    "down": TextAction.CURSOR_DOWN,

    "ctrl+a": TextAction.CURSOR_JUMP_LINE_START,
    "ctrl+e": TextAction.CURSOR_JUMP_LINE_END,

    # deletion
    "backspace": TextAction.DELETE_CHAR,
    "ctrl+u": TextAction.DELETE_LINE,
    "ctrl+w": TextAction.DELETE_WORD_BEFORE_CURSOR,
})

def text_input_parse_event(bindings: MappingProxyType[str, TextAction], event: InputEvent):
    if event.key_event is None:
        return
    if len(event.key_event)== 1:
        return TextActionChar(event.key_event)
    if event.is_bracketed_paste:
        return TextActionPaste(event.key_event[1:-1])
    if event.key_event in bindings.keys():
        return bindings[event.key_event]

def _select_through_mouse(
    relative_mouse_pos: Coordinate,
    lines: Iterable[str]
) -> None | tuple[int, int]:

    for line_i, line in enumerate(lines):
        if line_i != relative_mouse_pos.y:
            continue

        dx = 0
        char_i = 0
        for char_i, char in enumerate(line):
            char_width = measure_char(char)
            if dx == relative_mouse_pos.x or dx+char_width-1 == relative_mouse_pos.x:
                return (line_i, char_i)

            dx += char_width
        # even if we click of the line, then select at end of line
        return (line_i, char_i + 1)

@dataclass
class TextInput:
    lines: list[str]
    node_id: NodeID | None = None
    cursor_index: int = 0
    cursor_line: int = 0

    @property
    def cursor_clamped_index(self):
        return clamp(self.cursor_index, 0, len(self.lines[self.cursor_line]))

    # maybe nav_data instead for nav, node_id?
    def update[T](
        self,
        event: T,
        nav: NavState,
        parse_event_func: Callable[[T], TextAction | TextActionPaste | TextActionChar | None]\
         = partial(text_input_parse_event, DEFAULT_TEXT_INPUT_BINDINGS)
    ):
        action = parse_event_func(event)

        curr_line = self.lines[self.cursor_line]
        match action:
            case TextAction.SELECT_THOUGH_MOUSE: # set cursor_line and pos to approprita place
                if nav.result_data is not None and nav.is_hovered(self.node_id):
                    box_data = nav.result_data.box_data[self.node_id]

                    # defined in local space
                    mouse_pos = nav.mouse_position - box_data.box.position
                    res = _select_through_mouse(mouse_pos, self.lines)
                    if res is not None:
                        self.cursor_line, self.cursor_index = res

            case TextAction.DELETE_WORD_BEFORE_CURSOR:
                self.cursor_index = self.cursor_clamped_index
                right = curr_line[self.cursor_index:]

                left = curr_line[:self.cursor_index]
                left = left.rstrip(" ")

                if (split_at := left.rfind(" ")) != -1:
                    left = left[:split_at+1]
                    self.lines[self.cursor_line] =  left + right
                    self.cursor_index = len(left)
                else:
                    self.lines[self.cursor_line] = right
                    self.cursor_index = 0

            case TextAction.CURSOR_RIGHT:
                if self.cursor_index < len(curr_line):
                    self.cursor_index += 1

            case TextAction.CURSOR_LEFT:
                self.cursor_index = self.cursor_clamped_index

                if self.cursor_index != 0:
                    self.cursor_index -= 1

            case TextAction.CURSOR_DOWN:
                if self.cursor_line < len(self.lines) -1:
                    self.cursor_line += 1

            case TextAction.CURSOR_UP:
                if self.cursor_line != 0:
                    self.cursor_line -= 1

            case TextAction.DELETE_CHAR:
                self.cursor_index = self.cursor_clamped_index

                if self.cursor_index != 0 and len(curr_line):
                    self.lines[self.cursor_line] = "".join([curr_line[:self.cursor_index-1], curr_line[self.cursor_index:]])
                    self.cursor_index -= 1
                elif len(self.lines) > 1:
                    del self.lines[self.cursor_line]
                    self.cursor_line += 0 if self.cursor_line == 0 else -1
                    self.cursor_index = len(self.lines[self.cursor_line])

            case TextAction.DELETE_LINE:
                self.lines[self.cursor_line] = ""
                self.cursor_index = 0

            case TextAction.CURSOR_JUMP_LINE_END:
                self.cursor_index = len(curr_line)

            case TextAction.CURSOR_JUMP_LINE_START:
                self.cursor_index = 0

            case TextAction.NEW_LINE:
                if self.cursor_index < len(curr_line):
                    self.lines[self.cursor_line] = curr_line[:self.cursor_index]
                    self.lines.insert(self.cursor_line+1, curr_line[self.cursor_index:])
                    self.cursor_line += 1
                    self.cursor_index = 0
                else:
                    self.lines.insert(self.cursor_line+1, "")
                    self.cursor_line += 1

        if isinstance(action, TextActionChar):
            if action.char == "\n":
                raise AssertionError("lol")

            # add to current line, unless newline_char
            self.cursor_index = self.cursor_clamped_index

            self.lines[self.cursor_line] = "".join([
                curr_line[:self.cursor_index],
                action.char,
                curr_line[self.cursor_index:]]
            )
            self.cursor_index += 1
        elif isinstance(action, TextActionPaste):
            # just in case, ramove all \n
            content = action.content.replace("\n", "")

            self.cursor_index = self.cursor_clamped_index
            self.lines[self.cursor_line] = "".join([
                curr_line[:self.cursor_index],
                content,
                curr_line[self.cursor_index + len(content):]]
            )
            self.cursor_index += len(content)


    def _get_cursor_visual_position(self) -> Coordinate:
        y = self.cursor_line
        line = self.lines[self.cursor_line]
        x = measure_text(line[0:self.cursor_clamped_index])
        return Coordinate(x, y)

    @property
    def cursor_visual_offset(self):
        return self._get_cursor_visual_position()

    def view_lines(self) -> Generator[tuple[tuple[TextInputStyle, str], ...]]:
        x, y = self.cursor_visual_offset

        for dy, content in enumerate(self.lines):
            if dy != y:
                yield ((TextInputStyle.DEFAULT, content),)
                continue

            if measure_text(content) == x:
                content += " "


            # find where to cut for cursor
            dx = 0
            x_index = 0
            for x_index, char in enumerate(content):
                char_width = measure_char(char)
                if dx >= x: break
                dx += char_width

            yield (
                (TextInputStyle.DEFAULT, content[:x_index]),
                (TextInputStyle.CURSOR, content[x_index]),
                (TextInputStyle.DEFAULT, content[x_index+1:]),
            )

def view_text_input(text_in: TextInput, cursor_style = StyleRule(add_attrs=StyleAttr.REVERSE)):
    return vbox([
        text(l[0][1]) if len(l) == 1 else hbox([
            text(t[1]) if t[0] == TextInputStyle.DEFAULT else text(t[1]) | style(cursor_style) for t in l
        ]) for l in text_in.view_lines()
    ]) | (hoverable(text_in.node_id) if text_in.node_id is not None else empty)
