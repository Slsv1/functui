from enum import Enum, IntEnum, Flag, auto
from typing import NamedTuple, Self
from dataclasses import dataclass
from functools import cache
import colorsys

COLOR4_TO_HEX = {
    0   :0x000000,
    1   :0x800000,
    2   :0x008000,
    3   :0x808000,
    4   :0x000080,
    5   :0x800080,
    6   :0x008080,
    7   :0xc0c0c0,

    8   :0x808080,
    9   :0xff0000,
    10  :0x00ff00,
    11  :0xffff00,
    12  :0x0000ff,
    13  :0xff00ff,
    14  :0x00ffff,
    15  :0xffffff,
}
XTERM256_DEFINED_COLORS_TO_HEX = {
    16  :0x000000,
    17  :0x00005f,
    18  :0x000087,
    19  :0x0000af,
    20  :0x0000d7,
    21  :0x0000ff,
    22  :0x005f00,
    23  :0x005f5f,
    24  :0x005f87,
    25  :0x005faf,
    26  :0x005fd7,
    27  :0x005fff,
    28  :0x008700,
    29  :0x00875f,
    30  :0x008787,
    31  :0x0087af,
    32  :0x0087d7,
    33  :0x0087ff,
    34  :0x00af00,
    35  :0x00af5f,
    36  :0x00af87,
    37  :0x00afaf,
    38  :0x00afd7,
    39  :0x00afff,
    40  :0x00d700,
    41  :0x00d75f,
    42  :0x00d787,
    43  :0x00d7af,
    44  :0x00d7d7,
    45  :0x00d7ff,
    46  :0x00ff00,
    47  :0x00ff5f,
    48  :0x00ff87,
    49  :0x00ffaf,
    50  :0x00ffd7,
    51  :0x00ffff,
    52  :0x5f0000,
    53  :0x5f005f,
    54  :0x5f0087,
    55  :0x5f00af,
    56  :0x5f00d7,
    57  :0x5f00ff,
    58  :0x5f5f00,
    59  :0x5f5f5f,
    60  :0x5f5f87,
    61  :0x5f5faf,
    62  :0x5f5fd7,
    63  :0x5f5fff,
    64  :0x5f8700,
    65  :0x5f875f,
    66  :0x5f8787,
    67  :0x5f87af,
    68  :0x5f87d7,
    69  :0x5f87ff,
    70  :0x5faf00,
    71  :0x5faf5f,
    72  :0x5faf87,
    73  :0x5fafaf,
    74  :0x5fafd7,
    75  :0x5fafff,
    76  :0x5fd700,
    77  :0x5fd75f,
    78  :0x5fd787,
    79  :0x5fd7af,
    80  :0x5fd7d7,
    81  :0x5fd7ff,
    82  :0x5fff00,
    83  :0x5fff5f,
    84  :0x5fff87,
    85  :0x5fffaf,
    86  :0x5fffd7,
    87  :0x5fffff,
    88  :0x870000,
    89  :0x87005f,
    90  :0x870087,
    91  :0x8700af,
    92  :0x8700d7,
    93  :0x8700ff,
    94  :0x875f00,
    95  :0x875f5f,
    96  :0x875f87,
    97  :0x875faf,
    98  :0x875fd7,
    99  :0x875fff,
    100 :0x878700,
    101 :0x87875f,
    102 :0x878787,
    103 :0x8787af,
    104 :0x8787d7,
    105 :0x8787ff,
    106 :0x87af00,
    107 :0x87af5f,
    108 :0x87af87,
    109 :0x87afaf,
    110 :0x87afd7,
    111 :0x87afff,
    112 :0x87d700,
    113 :0x87d75f,
    114 :0x87d787,
    115 :0x87d7af,
    116 :0x87d7d7,
    117 :0x87d7ff,
    118 :0x87ff00,
    119 :0x87ff5f,
    120 :0x87ff87,
    121 :0x87ffaf,
    122 :0x87ffd7,
    123 :0x87ffff,
    124 :0xaf0000,
    125 :0xaf005f,
    126 :0xaf0087,
    127 :0xaf00af,
    128 :0xaf00d7,
    129 :0xaf00ff,
    130 :0xaf5f00,
    131 :0xaf5f5f,
    132 :0xaf5f87,
    133 :0xaf5faf,
    134 :0xaf5fd7,
    135 :0xaf5fff,
    136 :0xaf8700,
    137 :0xaf875f,
    138 :0xaf8787,
    139 :0xaf87af,
    140 :0xaf87d7,
    141 :0xaf87ff,
    142 :0xafaf00,
    143 :0xafaf5f,
    144 :0xafaf87,
    145 :0xafafaf,
    146 :0xafafd7,
    147 :0xafafff,
    148 :0xafd700,
    149 :0xafd75f,
    150 :0xafd787,
    151 :0xafd7af,
    152 :0xafd7d7,
    153 :0xafd7ff,
    154 :0xafff00,
    155 :0xafff5f,
    156 :0xafff87,
    157 :0xafffaf,
    158 :0xafffd7,
    159 :0xafffff,
    160 :0xd70000,
    161 :0xd7005f,
    162 :0xd70087,
    163 :0xd700af,
    164 :0xd700d7,
    165 :0xd700ff,
    166 :0xd75f00,
    167 :0xd75f5f,
    168 :0xd75f87,
    169 :0xd75faf,
    170 :0xd75fd7,
    171 :0xd75fff,
    172 :0xd78700,
    173 :0xd7875f,
    174 :0xd78787,
    175 :0xd787af,
    176 :0xd787d7,
    177 :0xd787ff,
    178 :0xd7af00,
    179 :0xd7af5f,
    180 :0xd7af87,
    181 :0xd7afaf,
    182 :0xd7afd7,
    183 :0xd7afff,
    184 :0xd7d700,
    185 :0xd7d75f,
    186 :0xd7d787,
    187 :0xd7d7af,
    188 :0xd7d7d7,
    189 :0xd7d7ff,
    190 :0xd7ff00,
    191 :0xd7ff5f,
    192 :0xd7ff87,
    193 :0xd7ffaf,
    194 :0xd7ffd7,
    195 :0xd7ffff,
    196 :0xff0000,
    197 :0xff005f,
    198 :0xff0087,
    199 :0xff00af,
    200 :0xff00d7,
    201 :0xff00ff,
    202 :0xff5f00,
    203 :0xff5f5f,
    204 :0xff5f87,
    205 :0xff5faf,
    206 :0xff5fd7,
    207 :0xff5fff,
    208 :0xff8700,
    209 :0xff875f,
    210 :0xff8787,
    211 :0xff87af,
    212 :0xff87d7,
    213 :0xff87ff,
    214 :0xffaf00,
    215 :0xffaf5f,
    216 :0xffaf87,
    217 :0xffafaf,
    218 :0xffafd7,
    219 :0xffafff,
    220 :0xffd700,
    221 :0xffd75f,
    222 :0xffd787,
    223 :0xffd7af,
    224 :0xffd7d7,
    225 :0xffd7ff,
    226 :0xffff00,
    227 :0xffff5f,
    228 :0xffff87,
    229 :0xffffaf,
    230 :0xffffd7,
    231 :0xffffff,

    232 :0x080808,
    233 :0x121212,
    234 :0x1c1c1c,
    235 :0x262626,
    236 :0x303030,
    237 :0x3a3a3a,
    238 :0x444444,
    239 :0x4e4e4e,
    240 :0x585858,
    241 :0x626262,
    242 :0x6c6c6c,
    243 :0x767676,
    244 :0x808080,
    245 :0x8a8a8a,
    246 :0x949494,
    247 :0x9e9e9e,
    248 :0xa8a8a8,
    249 :0xb2b2b2,
    250 :0xbcbcbc,
    251 :0xc6c6c6,
    252 :0xd0d0d0,
    253 :0xdadada,
    254 :0xe4e4e4,
    255 :0xeeeeee,
}
XTERM256_TO_HEX = {**COLOR4_TO_HEX, **XTERM256_DEFINED_COLORS_TO_HEX}

HEX_TO_XTERM256_DEFINED_COLORS = {k: v for v, k in XTERM256_DEFINED_COLORS_TO_HEX.items()}

def xterm256_to_hex(color: int) -> int:
    return XTERM256_TO_HEX[color]

class Color4(IntEnum):
    """ANSI SGR codes for 4 bit colors

    Attributes:
        BLACK:
        RED:
        GREEN:
        YELLOW:
        BLUE:
        MAGENTA:
        CYAN:
        WHITE:
        RESET: Use terminal's default foreground or background color.
        BRIGHT_BLACK:
        BRIGHT_RED:
        BRIGHT_GREEN:
        BRIGHT_YELLOW:
        BRIGGT_BLUE:
        BRIGHT_MAGENTA:
        BRIGHT_CYAN:
        BRIGHT_WHITE:
    """
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7

    BRIGHT_BLACK = 8
    BRIGHT_RED = 9
    BRIGHT_GREEN = 10
    BRIGHT_YELLOW = 11
    BRIGHT_BLUE = 12
    BRIGHT_MAGENTA = 13
    BRIGHT_CYAN = 14
    BRIGHT_WHITE = 15

    RESET = -1

class ColorParseError(Exception): pass

# Some functuionality of this class has been copied over from the textual project.
# https://github.com/Textualize/textual/blob/main/src/textual/color.py
class Color(NamedTuple):
    """Represent a 24 bit color.

    Attributes:
        r: Red value, an integer from 0 to 255 inclusive.
        g: Green value, an integer from 0 to 255 inclusive.
        b: Blue value, an integer from 0 to 255 inclusive.
        a: Alpha value, a float from 0 to 1.0 inclusive.
    """
    r: int
    g: int
    b: int
    a: float = 1.0

    @classmethod
    def parse(cls, color: str):
        """Create a new color from a string.

        The following formats will be parsed:
         - ``#RRGGBB``
         - ``#RRGGBBAA``
         - ``rgb(R, G, B)`` where R, G, B are integers between 0 and 255
         - ``rgb(R, G, B, A)`` where A is a float between 0.0 and 1.0
        """
        color = color.strip()
        if color.startswith("#"): # parse hex
            if len(color) == 7:
                return cls(
                    int(color[1:3], 16),
                    int(color[3:5], 16),
                    int(color[5:7], 16),
                    1.0
                )
            elif len(color) == 9:
                return cls(
                    int(color[1:3], 16),
                    int(color[3:5], 16),
                    int(color[5:7], 16),
                    int(color[7:9], 16) / 255,
                )
            raise ColorParseError(f"Expected #rrggbb or #rrggbbaa, got '{color}'")

        elif color.startswith("rgb("):
            parts = [p.strip() for p in color[4:-1].split(",")]
            if len(parts) != 3:
                raise ColorParseError(f"Expected rgb(rrr, ggg, bbb), got '{color}'")

            return cls(
                int(parts[0]),
                int(parts[1]),
                int(parts[2]),
                1.0,
            )
        elif color.startswith("rgba("):
            parts = [p.strip() for p in color[5:-1].split(",")]
            if len(parts) != 4:
                raise ColorParseError(f"Expected rgba(rrr, ggg, bbb, a.a), got '{color}'")
            return cls(
                int(parts[0]),
                int(parts[1]),
                int(parts[2]),
                float(parts[3]),
            )
        raise ColorParseError(f"Invalid color format, got '{color}'")



    @property
    @cache
    def hex(self) -> int:
        """Convert to an integer represeting this colors hexadecimal value."""
        return (0 | self.r << 16 | self.g << 8 | self.b)

    @cache
    def to_nearest_8bit(self) -> int:
        distance_to_color = {_color_distance_fast(hex(k), self): v for k, v in HEX_TO_XTERM256_DEFINED_COLORS.items()}
        return distance_to_color[min(distance_to_color.keys())]

    @property
    @cache
    def hex_str(self) -> str:
        return f"#{self.hex:06x}"

    @property
    def normalized(self) -> tuple[float, float, float]:
        return (self.r / 255, self.g / 255, self.b / 255)

    @cache
    def overlay(self, other: Self) -> Self:
        r1, g1, b1, a1 = self
        r2, g2, b2, a2 = other

        return self.__class__(
            int(r1 + (r2 - r1) * a2),
            int(g1 + (g2 - g1) * a2),
            int(b1 + (b2 - b1) * a2),
            a1,
        )
    @property
    def brightness(self) -> float:
        """The human perceptual brightness.

        A value of 1 is returned for pure white, and 0 for pure black.
        Other colors lie on a gradient between the two extremes.
        """

        r, g, b = self.normalized
        brightness = (299 * r + 587 * g + 114 * b) / 1000
        return brightness

    def with_alpha(self, alpha: float, /) -> Self:
        r, g, b, _ = self
        return self.__class__(r, g, b, alpha)

    def distance_value_to(self, other: Self) -> int:
        """ignoring alpha"""
        a = self
        b = other
        return (a.r - b.r)**2 + (a.g - b.g)**2 + (a.b - b.b)**2


def _color_distance_fast(a: Color, b: Color) -> int:
    return (a.r - b.r)**2 + (a.g - b.g)**2 + (a.b - b.b)**2


def rgb(r: int, g: int, b: int, /):
    """Create a new :obj:`Color24` from rgb parameters."""
    return Color(r, g, b)

def rgba(r: int, g: int, b: int, a: float, /):
    """Create a new :obj:`Color24` from rgba parameters."""
    return Color(r, g, b, a)

def hsl(h: float, s: float, l: float, /):
    """Create a new :obj:`Color24` from hsl parameters."""
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return Color(int(r*255), int(g*255), int(b*255))

def hex(value: int, /):
    """Create a new :obj:`Color24` from a hexodecimal integer."""
    MASK = 0b11111111
    return Color((value >> 16) & MASK, (value >> 8) & MASK, value & MASK)

type TerminalColor = int | Color

# design requirements
# 
# color values
# brand colors
# background colors
#
# muted colors
# (darken and lighten colors?)
#
# widgets may link into theme, should update when change changes. () 


@dataclass
class ColorTheme:
    # color values
    # red: Color
    # yellow: Color
    # orange: Color
    # green: Color
    # blue: Color
    # cyan: Color
    # purple: Color
    # white: Color
    # black: Color
    #
    # primary: Color
    # secondary: Color
    # accent: Color
    #
    # foreground: Color
    # background: Color
    # surface: Color
    # panel: Color
    #
    # warning: Color
    # error: Color
    # success: Color
    #
    # # mutued versions
    # red_muted: Color
    # yellow_muted: Color
    # orange_muted: Color
    # green_muted: Color
    # blue_muted: Color
    # cyan_muted: Color
    # purple_muted: Color
    #
    # # white_muted: Color
    # # black_muted: Color
    #
    # primary_muted: Color
    # secondary_muted: Color
    # accent_muted: Color
    #
    # # foreground_muted: Color
    # # background_muted: Color
    # # surface_muted: Color
    # # panel_muted: Color
    #
    # warning_muted: Color
    # error_muted: Color
    # success_muted: Color

    def __init__(
        self,
        *,
        red: TerminalColor,
        yellow: TerminalColor,
        orange: TerminalColor,
        green: TerminalColor,
        blue: TerminalColor,
        cyan: TerminalColor,
        purple: TerminalColor,

        white: TerminalColor,
        black: TerminalColor,

        primary: TerminalColor | None = None,
        secondary: TerminalColor | None = None,
        accent: TerminalColor | None = None,

        foreground: TerminalColor | None = None,
        background: TerminalColor | None = None,
        surface: TerminalColor,
        panel: TerminalColor,

        warning: TerminalColor | None = None,
        error: TerminalColor | None = None,
        success: TerminalColor | None = None,
    ):
        background = background if background is not None else black

        def _create_muted(color: TerminalColor):
            # dont do anything if we are in ansi land
            if isinstance(color, int) or isinstance(background, int):
                return color

            return background.overlay(color.with_alpha(0.3))

        # plain colors
        self.red=red
        self.yellow=yellow
        self.orange=orange
        self.green=green
        self.blue=blue
        self.cyan=cyan
        self.purple=purple
        self.white=white
        self.black=black

        # foreground
        self.foreground=foreground if foreground is not None else white

        # backgrounds
        self.background=background
        self.surface=surface
        self.panel=panel

        # special
        self.primary=primary if primary is not None else blue
        self.secondary=secondary if secondary is not None else cyan
        self.accent=accent if accent is not None else purple
        self.warning=warning if warning is not None else orange
        self.error=error if error is not None else yellow
        self.success=success if success is not None else green

        # muted colors
        self.red_muted=_create_muted(red)
        self.yellow_muted=_create_muted(yellow)
        self.orange_muted=_create_muted(orange)
        self.green_muted=_create_muted(green)
        self.blue_muted=_create_muted(blue)
        self.cyan_muted=_create_muted(cyan)
        self.purple_muted=_create_muted(purple)

        # muted foreground
        self.foreground_muted=_create_muted(self.foreground)

        # muted special
        self.primary_muted=_create_muted(self.primary)
        self.secondary_muted=_create_muted(self.secondary)
        self.accent_muted=_create_muted(self.accent)
        self.warning_muted=_create_muted(self.warning)
        self.error_muted=_create_muted(self.error)
        self.success_muted=_create_muted(self.success)


DRACULA_COLOR_THEME = ColorTheme(
    cyan=Color.parse("#8be9fd"),
    green=Color.parse("#50fa7b"),
    orange=Color.parse("#ffb86c"),
    purple=Color.parse("#ff79c6"),
    blue=Color.parse("#bd93f9"),
    red=Color.parse("#ff5555"),
    yellow=Color.parse("#f1fa8c"),

    secondary=Color.parse("#6272a4"),

    white=Color.parse("#f8f8f2"),
    black=Color.parse("#282a36"),

    surface=Color.parse("#2b2e3b"),
    panel=Color.parse("#44475a"),
)

# "gruvbox": Theme(
#         name="gruvbox",
#         primary="#85A598",
#         secondary="#A89A85",
#         warning="#fe8019",
#         error="#fb4934",
#         success="#b8bb26",
#         accent="#fabd2f",
#         foreground="#fbf1c7",
#         background="#282828",
#         surface="#3c3836",
#         panel="#504945",
#         variables={
#             "block-cursor-foreground": "#fbf1c7",
#             "input-selection-background": "#689d6a40",
#             "button-color-foreground": "#282828",
#         },
#     ),
