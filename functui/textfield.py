from enum import Enum, auto
from typing import NamedTuple, Self
from dataclasses import dataclass
from types import MappingProxyType
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

default_text_input_bindings = MappingProxyType({
    "escape": TextAction.SUBMIT,
    "enter": TextAction.SUBMIT,
    "backspace": TextAction.DELETE,
    "left": TextAction.CURSOR_LEFT,
    "right": TextAction.CURSOR_RIGHT
})
def create_text_input_event(key_event: str | None, bindings = default_text_input_bindings):
    if key_event is None:
        return
    if len(key_event)== 1:
        return TextActionChar(key_event)
    if key_event in bindings.keys():
        return bindings[key_event]



