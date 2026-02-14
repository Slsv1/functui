from enum import Enum, auto
from dataclasses import dataclass

class ParserState(Enum):
    GROUND = auto()
    UTF_1_BYTE_LEFT = auto()
    UTF_2_BYTES_LEFT = auto()
    UTF_3_BYTES_LEFT = auto()
    ESC = auto()
    CSI = auto()
    OSC = auto()
    MAYBE_ST = auto() # string terminator


class RawInputType(Enum):
    CHAR = auto()
    DEL = auto()
    CSI = auto()
    OSC = auto()
    C0 = auto()

@dataclass
class RawInputEvent:
    data: str
    type: RawInputType

ESCAPE_BYTE = ord("\x1b")
class ByteParser:
    buffer: list[int] = []
    state: ParserState = ParserState.GROUND

    def feed(self, byte: int) -> RawInputEvent | None:
        match self.state:
            case ParserState.GROUND:
                if 0x00 <= byte <= 0x1F:
                    if byte == ESCAPE_BYTE:
                        self.buffer.append(byte)
                        self._change_state(ParserState.ESC)
                        return

                    data = chr(byte)
                    return RawInputEvent(data, RawInputType.C0)
                if byte==0x7F:
                    data = chr(byte)
                    return RawInputEvent(data, RawInputType.DEL)
                elif (byte >> 5) == 0b0000_0110: # utf, 2 bytes
                    self.buffer.append(byte)
                    self._change_state(ParserState.UTF_1_BYTE_LEFT)
                    return
                elif (byte >> 4) == 0b0000_1110: # utf, 2 bytes
                    self.buffer.append(byte)
                    self._change_state(ParserState.UTF_2_BYTES_LEFT)
                    return
                elif (byte >> 3) == 0b0001_1110: # utf, 2 bytes
                    self.buffer.append(byte)
                    self._change_state(ParserState.UTF_3_BYTES_LEFT)
                    return

                # ascii printable character
                # no need to clear buffer because nothing was put in.
                return RawInputEvent(chr(byte), RawInputType.CHAR)
            case ParserState.UTF_1_BYTE_LEFT:
                # if (byte >> 6) == 0b0000_0010:
                self.buffer.append(byte)
                char = bytearray(self.buffer).decode()
                self._change_state(ParserState.GROUND)
                return RawInputEvent(
                    char,
                    RawInputType.CHAR,
                )
                self._change_state(ParserState.GROUND)
            case ParserState.UTF_2_BYTES_LEFT:
                self.buffer.append(byte)
                self._change_state(ParserState.UTF_1_BYTE_LEFT)
                return
            case ParserState.UTF_3_BYTES_LEFT:
                self.buffer.append(byte)
                self._change_state(ParserState.UTF_2_BYTES_LEFT)
                return
            case ParserState.ESC:
                if byte == ord("["):
                    self.buffer.append(byte)
                    self._change_state(ParserState.CSI)
                    return
                if byte == ord("]"):
                    self.buffer.append(byte)
                    self._change_state(ParserState.OSC)
                    return
            case ParserState.OSC:
                if byte == 0x07: # BEL
                    self.buffer.append(byte)
                    data = bytearray(self.buffer).decode()
                    self._change_state(ParserState.GROUND)
                    return RawInputEvent(data, RawInputType.OSC) 
                if byte == ESCAPE_BYTE:
                    self._change_state(ParserState.MAYBE_ST)
                    self.buffer.append(byte)
                    return
                self.buffer.append(byte)
            case ParserState.MAYBE_ST:
                if byte == 0x5C: # is string terminator
                    self.buffer.append(byte)
                    data = bytearray(self.buffer).decode()
                    self._change_state(ParserState.GROUND)
                    return RawInputEvent(data, RawInputType.OSC)
                # was not string terminator, just data
                self._change_state(ParserState.OSC)
                self.buffer.append(byte)
                return
            case ParserState.CSI:
                if 0x30 <= byte <= 0x3F: # (ASCII 0–9:;<=>?)
                    # we are in parameter bytes, the escape code will continue
                    self.buffer.append(byte)
                    return
                self.buffer.append(byte)
                char = bytearray(self.buffer).decode()
                self._change_state(ParserState.GROUND)
                return RawInputEvent(char, RawInputType.CSI)


    def _change_state(self, new_state: ParserState) -> None:
        if new_state == ParserState.GROUND:
            self.buffer.clear()
        self.state = new_state
#
# Raw Input Parser
#
class RawInputParserState(Enum):
    GROUND = auto()
    PASTE = auto()

class RawInputParser:
    def __init__(self) -> None:
        self.state = RawInputParserState.GROUND
        self._paste_buffer: list[str] = []

    def feed(self, raw_event: RawInputEvent) -> InputEvent | None:
        match self.state:
            case RawInputParserState.GROUND:
                if raw_event.type == RawInputType.CHAR:
                    return InputEvent(key_event=raw_event.data)
                if raw_event.type == RawInputType.CSI:
                    if raw_event.data == "\x1b[200~": # bracketed paste start
                        self.state = RawInputParserState.PASTE
                        return
                    if raw_event.data.startswith("\x1b[<"): # mouse
                        first_sep_at = raw_event.data.find(";")
                        button_nr = raw_event.data[3:first_sep_at]
                        released = raw_event.data.endswith("m")
                        released_suffix = " released" if released else ""
                        prefix, x, y_and_suffix = raw_event.data.split(";", 3)
                        y = y_and_suffix[:-1]
                        data = "unknown"
                        if button_nr == "0":
                            data = "left mouse" + released_suffix
                        elif button_nr == "1":
                            data = "middle mouse" + released_suffix
                        elif button_nr == "2":
                            data = "right mouse" + released_suffix
                        elif button_nr in ("35", "34", "33", "32"): # mouse move
                            data = None
                        elif button_nr == "65":
                            data = "mouse wheel down"
                        elif button_nr == "64":
                            data = "mouse wheel up"

                        return InputEvent(key_event=data, mouse_position_event=Coordinate(int(x)-1, int(y)-1))
                if parsed_key := SUQUENCE_TO_KEY.get(raw_event.data, None):
                    return InputEvent(key_event=parsed_key)
                return InputEvent(key_event="unknown")
            case RawInputParserState.PASTE:
                if raw_event.type == RawInputType.CHAR:
                    self._paste_buffer.append(raw_event.data)
                    return
                if raw_event.type == RawInputType.CSI and raw_event.data == "\x1b[201~": # bracketed paste start
                    data = f"[{"".join(self._paste_buffer)}]"
                    self._paste_buffer.clear()
                    self.state = RawInputParserState.GROUND
                    return InputEvent(key_event=data)
