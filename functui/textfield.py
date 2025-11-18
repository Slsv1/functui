from enum import Enum, auto
from typing import NamedTuple, Self
from dataclasses import dataclass
import curses

class TextActionChar(NamedTuple):
    char: str

class TextAction(Enum):
    NONE = auto()
    SUBMIT = auto()
    DELETE = auto()
    CURSOR_LEFT = auto()
    CURSOR_RIGHT = auto()

def start_text_input(starting_text: str = ""):
    return TextInput(starting_text, len(starting_text))

@dataclass(frozen=True, eq=True)
class TextInput():
    value: str = ""
    cursor_pos: int = 0
    submited: bool = False
    def update(self, action: TextAction | TextActionChar) -> Self:
        if self.submited:
            return self
        new_cursor_pos = self.cursor_pos
        new_acc = self.value
        new_submited = False
        match action:
            case TextAction.CURSOR_LEFT:
                if new_cursor_pos != 0:
                    new_cursor_pos -= 1
            case TextAction.CURSOR_RIGHT:
                if new_cursor_pos != len(self.value):
                    new_cursor_pos += 1
            case TextAction.DELETE:
                if new_cursor_pos != 0 and len(self.value):
                    new_cursor_pos -= 1
                    new_acc = "".join([self.value[:self.cursor_pos-1], self.value[self.cursor_pos:]])
            case TextAction.SUBMIT:
                new_submited = True
        if isinstance(action, TextActionChar):
            new_acc = "".join([self.value[:new_cursor_pos], action.char, self.value[new_cursor_pos:]])
            new_cursor_pos += 1

        return self.__class__(
            new_acc,
            new_cursor_pos,
            new_submited, 
        )

def blessed_text_input_action(val) -> TextAction | TextActionChar:
    if not val.is_sequence:
        return TextActionChar(val)
    match val.code:
        case curses.KEY_EXIT:
            return TextAction.SUBMIT
        case curses.KEY_BACKSPACE:
            return TextAction.DELETE
        case _:
            return TextAction.NONE
