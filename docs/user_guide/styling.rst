Styling
=======

Styling in the terminal has historically been quite difficult. Due to terminals being very old, there have been added multiple ways of styling, without the ability to remove legacy styling options due to backwards compatability.

3 Color Systems
---------------

4 bit color
~~~~~~~~~~~
One consequence of terminal history is that there are three ways of doing colors. The oldest, and most widely supported way is the 4 bit colors. **Colors specified with this format render differently depending on terminal theme!** This color format is accessible with the :obj:`~functui.classes.Color4` enum. Below folows a chart with all colors available with this enum.

.. raw:: html

    <pre style="font-family:monospace">
    <span style="color:#ffffff; background-color:#000000">BLACK  </span> <span style="color:#000000; background-color:#808080">BRIGHT_BLACK  </span>   
    <span style="color:#ffffff; background-color:#800000">RED    </span> <span style="color:#000000; background-color:#ff0000">BRIGHT_RED    </span>   
    <span style="color:#ffffff; background-color:#008000">GREEN  </span> <span style="color:#000000; background-color:#00ff00">BRIGHT_GREEN  </span>   
    <span style="color:#ffffff; background-color:#808000">YELLOW </span> <span style="color:#000000; background-color:#ffff00">BRIGHT_YELLOW </span>   
    <span style="color:#ffffff; background-color:#000080">BLUE   </span> <span style="color:#000000; background-color:#0000ff">BRIGHT_BLUE   </span>   
    <span style="color:#ffffff; background-color:#800080">MAGENTA</span> <span style="color:#000000; background-color:#ff00ff">BRIGHT_MAGENTA</span>   
    <span style="color:#ffffff; background-color:#008080">CYAN   </span> <span style="color:#000000; background-color:#00ffff">BRIGHT_CYAN   </span>   
    <span style="color:#ffffff; background-color:#c0c0c0">WHITE  </span> <span style="color:#000000; background-color:#ffffff">BRIGHT_WHITE  </span>   
    <span style="color:#ffffff">RESET  </span>
    </pre>


.. important::

    ``Color4`` has a ``RESET`` attribute. It represents your terminal's default foreground or backround color.


XTERM-256
~~~~~~~~~

Another widely supported color format is XTERM-256 (8 bit colors) This format is also very widely supported. To access this format you just simply use an :obj:`int` anywhere a color is needed. Which integer coresponds to which color can be viewed in the figure below.

.. raw:: html

    <pre style="font-family:monospace">
    Regular and bright colors are rendered differently depending on terminal theme
    Regular:  <span style="color:#ffffff; background-color:#000000">   0 </span><span style="color:#ffffff; background-color:#800000">   1 </span><span style="color:#ffffff; background-color:#008000">   2 </span><span style="color:#ffffff; background-color:#808000">   3 </span><span style="color:#ffffff; background-color:#000080">   4 </span><span style="color:#ffffff; background-color:#800080">   5 </span><span style="color:#ffffff; background-color:#008080">   6 </span><span style="color:#ffffff; background-color:#c0c0c0">   7 </span>                                   
    Bright:   <span style="color:#000000; background-color:#808080">   8 </span><span style="color:#000000; background-color:#ff0000">   9 </span><span style="color:#000000; background-color:#00ff00">  10 </span><span style="color:#000000; background-color:#ffff00">  11 </span><span style="color:#000000; background-color:#0000ff">  12 </span><span style="color:#000000; background-color:#ff00ff">  13 </span><span style="color:#000000; background-color:#00ffff">  14 </span><span style="color:#000000; background-color:#ffffff">  15 </span>                                   

    Color Cube
    <span style="color:#ffffff; background-color:#000000">  16 </span><span style="color:#ffffff; background-color:#00005f">  17 </span><span style="color:#ffffff; background-color:#000087">  18 </span><span style="color:#ffffff; background-color:#0000af">  19 </span><span style="color:#ffffff; background-color:#0000d7">  20 </span><span style="color:#ffffff; background-color:#0000ff">  21 </span><span style="color:#ffffff; background-color:#005f00">  22 </span><span style="color:#ffffff; background-color:#005f5f">  23 </span><span style="color:#ffffff; background-color:#005f87">  24 </span><span style="color:#ffffff; background-color:#005faf">  25 </span><span style="color:#ffffff; background-color:#005fd7">  26 </span><span style="color:#ffffff; background-color:#005fff">  27 </span><span style="color:#ffffff; background-color:#008700">  28 </span><span style="color:#ffffff; background-color:#00875f">  29 </span><span style="color:#ffffff; background-color:#008787">  30 </span><span style="color:#ffffff; background-color:#0087af">  31 </span><span style="color:#ffffff; background-color:#0087d7">  32 </span><span style="color:#ffffff; background-color:#0087ff">  33 </span>
    <span style="color:#ffffff; background-color:#5f0000">  52 </span><span style="color:#ffffff; background-color:#5f005f">  53 </span><span style="color:#ffffff; background-color:#5f0087">  54 </span><span style="color:#ffffff; background-color:#5f00af">  55 </span><span style="color:#ffffff; background-color:#5f00d7">  56 </span><span style="color:#ffffff; background-color:#5f00ff">  57 </span><span style="color:#ffffff; background-color:#5f5f00">  58 </span><span style="color:#ffffff; background-color:#5f5f5f">  59 </span><span style="color:#ffffff; background-color:#5f5f87">  60 </span><span style="color:#ffffff; background-color:#5f5faf">  61 </span><span style="color:#ffffff; background-color:#5f5fd7">  62 </span><span style="color:#ffffff; background-color:#5f5fff">  63 </span><span style="color:#ffffff; background-color:#5f8700">  64 </span><span style="color:#ffffff; background-color:#5f875f">  65 </span><span style="color:#ffffff; background-color:#5f8787">  66 </span><span style="color:#ffffff; background-color:#5f87af">  67 </span><span style="color:#ffffff; background-color:#5f87d7">  68 </span><span style="color:#ffffff; background-color:#5f87ff">  69 </span>
    <span style="color:#ffffff; background-color:#870000">  88 </span><span style="color:#ffffff; background-color:#87005f">  89 </span><span style="color:#ffffff; background-color:#870087">  90 </span><span style="color:#ffffff; background-color:#8700af">  91 </span><span style="color:#ffffff; background-color:#8700d7">  92 </span><span style="color:#ffffff; background-color:#8700ff">  93 </span><span style="color:#ffffff; background-color:#875f00">  94 </span><span style="color:#ffffff; background-color:#875f5f">  95 </span><span style="color:#ffffff; background-color:#875f87">  96 </span><span style="color:#ffffff; background-color:#875faf">  97 </span><span style="color:#ffffff; background-color:#875fd7">  98 </span><span style="color:#ffffff; background-color:#875fff">  99 </span><span style="color:#ffffff; background-color:#878700"> 100 </span><span style="color:#ffffff; background-color:#87875f"> 101 </span><span style="color:#ffffff; background-color:#878787"> 102 </span><span style="color:#ffffff; background-color:#8787af"> 103 </span><span style="color:#ffffff; background-color:#8787d7"> 104 </span><span style="color:#ffffff; background-color:#8787ff"> 105 </span>
    <span style="color:#ffffff; background-color:#af0000"> 124 </span><span style="color:#ffffff; background-color:#af005f"> 125 </span><span style="color:#ffffff; background-color:#af0087"> 126 </span><span style="color:#ffffff; background-color:#af00af"> 127 </span><span style="color:#ffffff; background-color:#af00d7"> 128 </span><span style="color:#ffffff; background-color:#af00ff"> 129 </span><span style="color:#ffffff; background-color:#af5f00"> 130 </span><span style="color:#ffffff; background-color:#af5f5f"> 131 </span><span style="color:#ffffff; background-color:#af5f87"> 132 </span><span style="color:#ffffff; background-color:#af5faf"> 133 </span><span style="color:#ffffff; background-color:#af5fd7"> 134 </span><span style="color:#ffffff; background-color:#af5fff"> 135 </span><span style="color:#ffffff; background-color:#af8700"> 136 </span><span style="color:#ffffff; background-color:#af875f"> 137 </span><span style="color:#ffffff; background-color:#af8787"> 138 </span><span style="color:#ffffff; background-color:#af87af"> 139 </span><span style="color:#ffffff; background-color:#af87d7"> 140 </span><span style="color:#ffffff; background-color:#af87ff"> 141 </span>
    <span style="color:#ffffff; background-color:#d70000"> 160 </span><span style="color:#ffffff; background-color:#d7005f"> 161 </span><span style="color:#ffffff; background-color:#d70087"> 162 </span><span style="color:#ffffff; background-color:#d700af"> 163 </span><span style="color:#ffffff; background-color:#d700d7"> 164 </span><span style="color:#ffffff; background-color:#d700ff"> 165 </span><span style="color:#ffffff; background-color:#d75f00"> 166 </span><span style="color:#ffffff; background-color:#d75f5f"> 167 </span><span style="color:#ffffff; background-color:#d75f87"> 168 </span><span style="color:#ffffff; background-color:#d75faf"> 169 </span><span style="color:#ffffff; background-color:#d75fd7"> 170 </span><span style="color:#ffffff; background-color:#d75fff"> 171 </span><span style="color:#ffffff; background-color:#d78700"> 172 </span><span style="color:#ffffff; background-color:#d7875f"> 173 </span><span style="color:#ffffff; background-color:#d78787"> 174 </span><span style="color:#ffffff; background-color:#d787af"> 175 </span><span style="color:#ffffff; background-color:#d787d7"> 176 </span><span style="color:#ffffff; background-color:#d787ff"> 177 </span>
    <span style="color:#ffffff; background-color:#ff0000"> 196 </span><span style="color:#ffffff; background-color:#ff005f"> 197 </span><span style="color:#ffffff; background-color:#ff0087"> 198 </span><span style="color:#ffffff; background-color:#ff00af"> 199 </span><span style="color:#ffffff; background-color:#ff00d7"> 200 </span><span style="color:#ffffff; background-color:#ff00ff"> 201 </span><span style="color:#ffffff; background-color:#ff5f00"> 202 </span><span style="color:#ffffff; background-color:#ff5f5f"> 203 </span><span style="color:#ffffff; background-color:#ff5f87"> 204 </span><span style="color:#ffffff; background-color:#ff5faf"> 205 </span><span style="color:#ffffff; background-color:#ff5fd7"> 206 </span><span style="color:#ffffff; background-color:#ff5fff"> 207 </span><span style="color:#ffffff; background-color:#ff8700"> 208 </span><span style="color:#ffffff; background-color:#ff875f"> 209 </span><span style="color:#ffffff; background-color:#ff8787"> 210 </span><span style="color:#ffffff; background-color:#ff87af"> 211 </span><span style="color:#ffffff; background-color:#ff87d7"> 212 </span><span style="color:#ffffff; background-color:#ff87ff"> 213 </span>
    <span style="color:#000000; background-color:#00af00">  34 </span><span style="color:#000000; background-color:#00af5f">  35 </span><span style="color:#000000; background-color:#00af87">  36 </span><span style="color:#000000; background-color:#00afaf">  37 </span><span style="color:#000000; background-color:#00afd7">  38 </span><span style="color:#000000; background-color:#00afff">  39 </span><span style="color:#000000; background-color:#00d700">  40 </span><span style="color:#000000; background-color:#00d75f">  41 </span><span style="color:#000000; background-color:#00d787">  42 </span><span style="color:#000000; background-color:#00d7af">  43 </span><span style="color:#000000; background-color:#00d7d7">  44 </span><span style="color:#000000; background-color:#00d7ff">  45 </span><span style="color:#000000; background-color:#00ff00">  46 </span><span style="color:#000000; background-color:#00ff5f">  47 </span><span style="color:#000000; background-color:#00ff87">  48 </span><span style="color:#000000; background-color:#00ffaf">  49 </span><span style="color:#000000; background-color:#00ffd7">  50 </span><span style="color:#000000; background-color:#00ffff">  51 </span>
    <span style="color:#000000; background-color:#5faf00">  70 </span><span style="color:#000000; background-color:#5faf5f">  71 </span><span style="color:#000000; background-color:#5faf87">  72 </span><span style="color:#000000; background-color:#5fafaf">  73 </span><span style="color:#000000; background-color:#5fafd7">  74 </span><span style="color:#000000; background-color:#5fafff">  75 </span><span style="color:#000000; background-color:#5fd700">  76 </span><span style="color:#000000; background-color:#5fd75f">  77 </span><span style="color:#000000; background-color:#5fd787">  78 </span><span style="color:#000000; background-color:#5fd7af">  79 </span><span style="color:#000000; background-color:#5fd7d7">  80 </span><span style="color:#000000; background-color:#5fd7ff">  81 </span><span style="color:#000000; background-color:#5fff00">  82 </span><span style="color:#000000; background-color:#5fff5f">  83 </span><span style="color:#000000; background-color:#5fff87">  84 </span><span style="color:#000000; background-color:#5fffaf">  85 </span><span style="color:#000000; background-color:#5fffd7">  86 </span><span style="color:#000000; background-color:#5fffff">  87 </span>
    <span style="color:#000000; background-color:#87af00"> 106 </span><span style="color:#000000; background-color:#87af5f"> 107 </span><span style="color:#000000; background-color:#87af87"> 108 </span><span style="color:#000000; background-color:#87afaf"> 109 </span><span style="color:#000000; background-color:#87afd7"> 110 </span><span style="color:#000000; background-color:#87afff"> 111 </span><span style="color:#000000; background-color:#87d700"> 112 </span><span style="color:#000000; background-color:#87d75f"> 113 </span><span style="color:#000000; background-color:#87d787"> 114 </span><span style="color:#000000; background-color:#87d7af"> 115 </span><span style="color:#000000; background-color:#87d7d7"> 116 </span><span style="color:#000000; background-color:#87d7ff"> 117 </span><span style="color:#000000; background-color:#87ff00"> 118 </span><span style="color:#000000; background-color:#87ff5f"> 119 </span><span style="color:#000000; background-color:#87ff87"> 120 </span><span style="color:#000000; background-color:#87ffaf"> 121 </span><span style="color:#000000; background-color:#87ffd7"> 122 </span><span style="color:#000000; background-color:#87ffff"> 123 </span>
    <span style="color:#000000; background-color:#afaf00"> 142 </span><span style="color:#000000; background-color:#afaf5f"> 143 </span><span style="color:#000000; background-color:#afaf87"> 144 </span><span style="color:#000000; background-color:#afafaf"> 145 </span><span style="color:#000000; background-color:#afafd7"> 146 </span><span style="color:#000000; background-color:#afafff"> 147 </span><span style="color:#000000; background-color:#afd700"> 148 </span><span style="color:#000000; background-color:#afd75f"> 149 </span><span style="color:#000000; background-color:#afd787"> 150 </span><span style="color:#000000; background-color:#afd7af"> 151 </span><span style="color:#000000; background-color:#afd7d7"> 152 </span><span style="color:#000000; background-color:#afd7ff"> 153 </span><span style="color:#000000; background-color:#afff00"> 154 </span><span style="color:#000000; background-color:#afff5f"> 155 </span><span style="color:#000000; background-color:#afff87"> 156 </span><span style="color:#000000; background-color:#afffaf"> 157 </span><span style="color:#000000; background-color:#afffd7"> 158 </span><span style="color:#000000; background-color:#afffff"> 159 </span>
    <span style="color:#000000; background-color:#d7af00"> 178 </span><span style="color:#000000; background-color:#d7af5f"> 179 </span><span style="color:#000000; background-color:#d7af87"> 180 </span><span style="color:#000000; background-color:#d7afaf"> 181 </span><span style="color:#000000; background-color:#d7afd7"> 182 </span><span style="color:#000000; background-color:#d7afff"> 183 </span><span style="color:#000000; background-color:#d7d700"> 184 </span><span style="color:#000000; background-color:#d7d75f"> 185 </span><span style="color:#000000; background-color:#d7d787"> 186 </span><span style="color:#000000; background-color:#d7d7af"> 187 </span><span style="color:#000000; background-color:#d7d7d7"> 188 </span><span style="color:#000000; background-color:#d7d7ff"> 189 </span><span style="color:#000000; background-color:#d7ff00"> 190 </span><span style="color:#000000; background-color:#d7ff5f"> 191 </span><span style="color:#000000; background-color:#d7ff87"> 192 </span><span style="color:#000000; background-color:#d7ffaf"> 193 </span><span style="color:#000000; background-color:#d7ffd7"> 194 </span><span style="color:#000000; background-color:#d7ffff"> 195 </span>
    <span style="color:#000000; background-color:#ffaf00"> 214 </span><span style="color:#000000; background-color:#ffaf5f"> 215 </span><span style="color:#000000; background-color:#ffaf87"> 216 </span><span style="color:#000000; background-color:#ffafaf"> 217 </span><span style="color:#000000; background-color:#ffafd7"> 218 </span><span style="color:#000000; background-color:#ffafff"> 219 </span><span style="color:#000000; background-color:#ffd700"> 220 </span><span style="color:#000000; background-color:#ffd75f"> 221 </span><span style="color:#000000; background-color:#ffd787"> 222 </span><span style="color:#000000; background-color:#ffd7af"> 223 </span><span style="color:#000000; background-color:#ffd7d7"> 224 </span><span style="color:#000000; background-color:#ffd7ff"> 225 </span><span style="color:#000000; background-color:#ffff00"> 226 </span><span style="color:#000000; background-color:#ffff5f"> 227 </span><span style="color:#000000; background-color:#ffff87"> 228 </span><span style="color:#000000; background-color:#ffffaf"> 229 </span><span style="color:#000000; background-color:#ffffd7"> 230 </span><span style="color:#000000; background-color:#ffffff"> 231 </span>

    Color ramps, black and white intentionaly excluded
    <span style="color:#ffffff; background-color:#080808"> 232 </span><span style="color:#ffffff; background-color:#121212"> 233 </span><span style="color:#ffffff; background-color:#1c1c1c"> 234 </span><span style="color:#ffffff; background-color:#262626"> 235 </span><span style="color:#ffffff; background-color:#303030"> 236 </span><span style="color:#ffffff; background-color:#3a3a3a"> 237 </span><span style="color:#ffffff; background-color:#444444"> 238 </span><span style="color:#ffffff; background-color:#4e4e4e"> 239 </span><span style="color:#ffffff; background-color:#585858"> 240 </span><span style="color:#ffffff; background-color:#626262"> 241 </span><span style="color:#ffffff; background-color:#6c6c6c"> 242 </span><span style="color:#ffffff; background-color:#767676"> 243 </span>
    <span style="color:#000000; background-color:#808080"> 244 </span><span style="color:#000000; background-color:#8a8a8a"> 245 </span><span style="color:#000000; background-color:#949494"> 246 </span><span style="color:#000000; background-color:#9e9e9e"> 247 </span><span style="color:#000000; background-color:#a8a8a8"> 248 </span><span style="color:#000000; background-color:#b2b2b2"> 249 </span><span style="color:#000000; background-color:#bcbcbc"> 250 </span><span style="color:#000000; background-color:#c6c6c6"> 251 </span><span style="color:#000000; background-color:#d0d0d0"> 252 </span><span style="color:#000000; background-color:#dadada"> 253 </span><span style="color:#000000; background-color:#e4e4e4"> 254 </span><span style="color:#000000; background-color:#eeeeee"> 255 </span>
    </pre>


.. tip::

   Colors represented by integers 0 through 15 are exactly the same colors as in :obj:`~functui.classes.Color4` enum (except ``RESET``). That enum is actually an :obj:`~enum.IntEnum` which means that it's members are treated as integers. (``RESET`` member is represented as -1)

True Color
~~~~~~~~~~

Lastly, there is true color (24 bit or rgb color). This color format can be accessed either via :obj:`~functui.classes.rgb` or :obj:`~functui.classes.hex` functuion that create a :obj:`~functui.classes.Color24` object that actully stores the color. This is the color format that the support is somewhat lacking. Most notably, the curses renderer does not support it.



Color Downgrading
-----------------

If you are using a color format that is not supported by the renderer (or terminal), it will be automatically downgraded to a supported format, with the new colors trying to match the original as closely as possible.

Styling elements
----------------

Functui uses :obj:`~functui.classes.StyleRule` objects to represent styles rules. These objects contains a forground and background color as well as a bunch of :obj:`~functui.classes.StyleAttr` flags to represent style attributes like bold or italic. Color can be represented either by an :obj:`int` (for 4 and 8 bit colors) or a :obj:`~functui.classes.Color24` (for 24 bit colors). To use a style rule on a layout you can use :obj:`~functui.common.push_rule`.

.. code-block:: py

    from functui.classes import *
    from functui.common import *
    from functui.io.ansi import layout_to_str

    style_rule = StyleRule(
        fg=Color4.BRIGHT_YELLOW,
        bg=rgb(10, 134, 143),
        add_attrs=StyleAttr.ITALIC | StyleAttr.BOLD
        # StyleAttr is a flag which means you
        # can use | to combine muliple attributes.
    )

    # use style on a layout
    layout = text("styled_text") | push_rule(style_rule) | border

    print(layout_to_str(layout, Rect(20, 3)))


Expected Output:

.. raw:: html

    <pre style="font-family:monospace">
    ┌──────────────────┐
    │<b><i><span style="color:#ffff00; background-color:#0a868f">styled_text</b></i></span>       │
    └──────────────────┘
    </pre>

.. important::
    As you may notice, only the text was styled even though technically the text node is taking up all of the available space inside the border. This is due to styles being applied only to "printed" characters, rather than the whole area a node takes up. To apply style to the whole node, use :obj:`~functui.common.bg_fill`.

    .. code-block:: py

        from functui.classes import *
        from functui.common import *
        from functui.io.ansi import layout_to_str

        style_rule = StyleRule(
            fg=Color4.BRIGHT_YELLOW,
            bg=rgb(10, 134, 143),
            add_attrs=StyleAttr.ITALIC | StyleAttr.BOLD
            # StyleAttr is a flag which means you
            # can use | to combine muliple attributes.
        )

        # use style on a layout
        layout = text("styled_text") | push_rule(style_rule) | border

        print(layout_to_str(layout, Rect(20, 3)))

    Expected Output:

    .. raw:: html

        <pre style="font-family:monospace">
        ┌──────────────────┐
        │<b><i><span style="color:#ffff00; background-color:#0a868f">styled_text       </b></i></span>│
        └──────────────────┘
        </pre>


``rule_*``
~~~~~~~~~~

In some cases though, this syntax of defining style rules can be quite tedious, especially if you only want to define a few style attributes. For those cases, there are numerous `rule_*` constants and functions.

.. code-block:: py


    from functui.classes import *
    from functui.common import *

    style_rule = rule_fg(Color4.RED) | rule_bold | rule_italic

    # much less visual noise when defining styles inline
    layout = text("foo") | styled(border, rule_fg(Color4.RED))



Convenient Styling Nodes
~~~~~~~~~~~~~~~~~~~~~~~~

Finaly, it's not always that you want to create a new style rule. Especially when it comes to quick prototyping, there are cases when you just want to apply one style and don't need the ability to reuse it. For those cases use :obj:`~functui.common.fg` and :obj:`~functui.common.bg` wrapper nodes for adding color to foreground and background respectively.
To apply styles to a layout there are wrapper nodes that are named as style attributes. For example :obj:`~functui.common.bold` and :obj:`~functui.common.italic`.


.. code-block:: py

    from functui import Rect, layout_to_str, Color4
    from functui.common import *

    layout = text("This text is red and bold") | fg(Color4.RED) | bold | border
    print(layout_to_str(layout, Rect(30, 3)))

Expected output:

.. raw:: html

    <pre style="font-family:monospace">
    ┌────────────────────────────┐
    │<b><span style="color:#800000">This text is red and bold</b></span>   │
    └────────────────────────────┘
    </pre>


``styled``
~~~~~~~~~~

Notice how these wrapper nodes style all of their descendants with the specified style.
If you want to style only certain wrapper nodes (for example a border), you can use :obj:`~functui.common.styled` to wrap nodes you want to style.

.. code-block:: py

    from functui import Rect, layout_to_str, rule_fg, rgb
    from functui.common import *

    style_rule = rule_fg(rgb(0, 255, 255))

    layout = text("This text is not styled.\nBut the border around it is.")\
        | styled(border, style_rule)

    print(layout_to_str(layout, Rect(30, 4)))


Expected output:

.. raw:: html

    <pre style="font-family:monospace">
    <span style="color:#00ffff">┌────────────────────────────┐
    │</span>This text is not styled.    <span style="color:#00ffff">│
    │</span>But the border around it is.<span style="color:#00ffff">│
    └────────────────────────────┘</span>
    </pre>

Rich Text
---------

Sometimes there may be a need for multiple styles in the same paragraph. This can be done with the :obj:`~functui.rich_text.rich_text` node or :obj:`~functui.rich_text.adaptive_text` if you also want that paragraph to be responsive to screen size changes. To style only a part of the paragraph, wrap that part in a :obj:`~functui.rich_text.span` and specify a :obj:`~functui.classes.style_rule`.

.. code-block:: py

    from functui.classes import *
    from functui.common import *
    from functui.rich_text import adaptive_text, rich_text, span
    from functui.io.ansi import layout_to_str


    layout = adaptive_text(
        "Some of this ",
        span("text", rule=rule_fg(Color4.BRIGHT_RED)),
        " will be ",
        span("styled. ", rule=rule_italic),
        span(
            "Also, it is possible to ",
            span("nest",rule=rule_fg(Color4.BRIGHT_BLACK) | rule_bold),
            " spans!",
            rule=rule_bg(Color4.BLUE)
        )
    ) | border

    print(layout_to_str(layout, Rect(20, 10)))

Expected Output:

.. raw:: html

    <pre style="font-family:monospace">
    ┌──────────────────┐
    │Some of this <span style="color:#ff0000">text</span> │
    │will be <i>styled. </i>  │
    │<span style="background-color:#000080">Also, it is </span>      │
    │<span style="background-color:#000080">possible to </span><b><span style="color:#808080; background-color:#000080">nest</b></span><span style="background-color:#000080"> </span> │
    │<span style="background-color:#000080">spans!</span>            │
    │                  │
    │                  │
    │                  │
    └──────────────────┘
    </pre>
