Cheat Sheet
===========

Containers
----------


:func:`~functui.common.vbox`
~~~~~~~~~~~~~~~~~~~~~~~~~~~

    >>> from functui import Rect, layout_to_str
    >>> from functui.common import vbox, text, border
    >>> layout = vbox([
    ...     text("hello") | border,
    ...     text("hej") | border,
    ...     text("bonjour") | border,
    ... ]) | border
    >>> print(layout_to_str(layout, Rect(20, 13)))
    ┌──────────────────┐
    │┌────────────────┐│
    ││hello           ││
    │└────────────────┘│
    │┌────────────────┐│
    ││hej             ││
    │└────────────────┘│
    │┌────────────────┐│
    ││bonjour         ││
    │└────────────────┘│
    │                  │
    │                  │
    └──────────────────┘



:func:`~functui.common.hbox`
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default usage:
    >>> from functui import Rect, layout_to_str
    >>> from functui.common import hbox, text, border
    >>> layout = hbox([
    ...     text("hello") | border,
    ...     text("hej") | border,
    ...     text("bonjour") | border,
    ... ]) | border
    >>> print(layout_to_str(layout, Rect(30, 7)))
    ┌────────────────────────────┐
    │┌─────┐┌───┐┌───────┐       │
    ││hello││hej││bonjour│       │
    ││     ││   ││       │       │
    ││     ││   ││       │       │
    │└─────┘└───┘└───────┘       │
    └────────────────────────────┘

.. tip::

   If you don't want children to take up container's full height, use :func:`functui.common.shrink_y` for hbox and :func:`functui.common.shrink_x` for vbox

        >>> from functui import Rect, layout_to_str
        >>> from functui.common import hbox, text, border, shrink, shrink_y
        >>> layout = hbox([
        ...     text("hello") | border | shrink_y,
        ...     text("hej") | border | shrink_y,
        ...     text("bonjour") | border | shrink_y,
        ... ]) | border
        >>> print(layout_to_str(layout, Rect(30, 10)))
        ┌────────────────────────────┐
        │┌─────┐┌───┐┌───────┐       │
        ││hello││hej││bonjour│       │
        │└─────┘└───┘└───────┘       │
        │                            │
        │                            │
        │                            │
        │                            │
        │                            │
        └────────────────────────────┘


:func:`~functui.flex.hbox_flex`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default usage
    >>> from functui import Rect, layout_to_str
    >>> from functui.common import border, text
    >>> from functui.flex import flex, hbox_flex, flex_custom
    >>> layout = hbox_flex([
    ...     text("Flex.") | border | flex,
    ...     text("No flex.") | border,
    ... ]) | border
    >>> print(layout_to_str(layout, Rect(40, 5)))
    ┌──────────────────────────────────────┐
    │┌──────────────────────────┐┌────────┐│
    ││Flex.                     ││No flex.││
    │└──────────────────────────┘└────────┘│
    └──────────────────────────────────────┘

Usage with flex_custom grow argument:
    >>> layout = hbox_flex([
    ...     text("grow 1") | border | flex_custom(grow=1),
    ...     text("grow 2") | border | flex_custom(grow=2),
    ...     text("grow 1") | border | flex, # flex same as flex_custom(1)
    ... ]) | border
    >>> print(layout_to_str(layout, Rect(40, 5)))
    ┌──────────────────────────────────────┐
    │┌───────┐┌─────────────────┐┌────────┐│
    ││grow 1 ││grow 2           ││grow 1  ││
    │└───────┘└─────────────────┘└────────┘│
    └──────────────────────────────────────┘

Usage with flex_custom grow and basis arguments:
    >>> layout = hbox_flex([
    ...     text("basis and grow") | border | flex_custom(grow=1, basis=True),
    ...     text("grow") | border | flex, # flex is same as flex_custom(grow=1)
    ... ]) | border
    >>> print(layout_to_str(layout, Rect(40, 5)))
    ┌──────────────────────────────────────┐
    │┌─────────────────────────┐┌─────────┐│
    ││basis and grow           ││grow     ││
    │└─────────────────────────┘└─────────┘│
    └──────────────────────────────────────┘

:func:`~functui.flex.vbox_flex`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Same as ``hbox_flex`` but arranges it's children vertically, lika a ``vbox``.

:func:`~functui.common.static_box`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Don't arrange children in any way and allows overlapping.

    >>> from functui import Rect, layout_to_str
    >>> from functui.common import *
    >>> layout = static_box([
    ...     text("first") | border | shrink,
    ...     text("second") | border | shrink | offset(1, 2)
    ... ]) | border
    >>> print(layout_to_str(layout, Rect(10, 8)))
    ┌────────┐
    │┌─────┐ │
    ││first│ │
    │└┌──────│
    │ │second│
    │ └──────│
    │        │
    └────────┘


Styling
-------

:func:`~functui.common.fg`, :func:`~functui.common.bg`, :func:`~functui.common.bold`, :func:`~functui.common.italic`...
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: py

    from functui import Rect, layout_to_str, Color4, rgb
    from functui.common import text, border, vbox, fg, bg,\
        bold, underline, italic, reverse, dim

    layout = vbox([
        # use terminals default theme
        text("blue foreground") | fg(Color4.BLUE),
        text("red backround") | bg(Color4.RED),

        # use rgb
        text("orange backround") | bg(rgb(200, 120, 000)),

        # styles
        text("bold") | bold,
        text("italic") | italic,
        text("underline") | underline,
        text("reverse") | reverse,
        text("dim") | dim,

        # multiple
        text("multiple styles")
            | bold
            | underline
            | fg(rgb(100, 100, 200))
            | bg(rgb(0, 0, 100))
    ]) | border

    print(layout_to_str(layout, Rect(20, 12)))

.. raw:: html

    <pre style="font-family:monospace">
    ┌──────────────────┐
    │<span style="color:#000080">blue foreground</span>   │
    │<span style="background-color:#800000">red backround</span>     │
    │<span style="background-color:#c87800">orange backround</span>  │
    │<b>bold</b>              │
    │<i>italic</i>            │
    │<u>underline</u>         │
    │reverse           │
    │dim               │
    │<b><u><span style="color:#6464c8; background-color:#000064">multiple styles</b></u></span>   │
    │                  │
    └──────────────────┘
    </pre>

:obj:`~functui.classes.StyleRule`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: py

    from functui import *  # for Rect, StyleRule, StyleAttr, Color4 and rgb
    from functui.common import *  # for text, push_rule and border
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

Style Whole Node, Not Just Text
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default behaviour:

.. code-block:: py

    from functui import Rect, layout_to_str, Color4
    from functui.common import text, border, vbox, bg

    layout = text("hej") | bg(Color4.GREEN) | border
    print(layout_to_str(layout, Rect(20, 5)))


.. raw:: html

    <pre style="font-family:monospace">
    ┌──────────────────┐
    │<span style="background-color:#008000">hej</span>               │
    │                  │
    │                  │
    └──────────────────┘
    </pre>

With :func:`functui.common.bg_fill`:

.. code-block:: py

    from functui import Rect, layout_to_str, Color4
    from functui.common import text, border, vbox, bg, bg_fill

    layout = text("hej") | bg_fill |  bg(Color4.GREEN) | border
    print(layout_to_str(layout, Rect(20, 5)))


.. raw:: html

    <pre style="font-family:monospace">
    ┌──────────────────┐
    │<span style="background-color:#008000">hej               </span>│
    │<span style="background-color:#008000">                  </span>│
    │<span style="background-color:#008000">                  </span>│
    └──────────────────┘
    </pre>

Borders
~~~~~~~

    >>> from functui import Rect, layout_to_str
    >>> from functui.common import * # for borders, vbox and text
    >>> from functui.flex import hbox_flex_wrap
    >>> custom_border_style = BorderStyle( line_h=".", line_v=":", corner_bl="%",
    ...                                   corner_tl="%", corner_br="%", corner_tr="%",)
    >>> layout = hbox_flex_wrap([
    ...     text("border") | border,
    ...     text("border_rounded") | border_rounded,
    ...     text("border_thick") | border_thick,
    ...     text("border_ascii") | border_ascii,
    ...     text("border_double") | border_double,
    ...     text("border_with_title") | border_with_title(text("[title]") | center),
    ...     text("custom_border") | custom_border(custom_border_style),
    ... ]) | border
    >>> print(layout_to_str(layout, Rect(60, 8)))
    ┌──────────────────────────────────────────────────────────┐
    │┌──────┐╭──────────────╮┏━━━━━━━━━━━━┓+------------+      │
    ││border││border_rounded│┃border_thick┃|border_ascii|      │
    │└──────┘╰──────────────╯┗━━━━━━━━━━━━┛+------------+      │
    │╔═════════════╗┌─────[title]─────┐%.............%         │
    │║border_double║│border_with_title│:custom_border:         │
    │╚═════════════╝└─────────────────┘%.............%         │
    └──────────────────────────────────────────────────────────┘

:func:`~functui.common.shrink`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    >>> from functui import Rect, layout_to_str
    >>> from functui.common import *
    >>> from functui.flex import hbox_flex, flex
    >>> layout = hbox_flex([ # hbox_flex used to give all children equal space
    ...     text("no shrink") | border | border_dashed | flex,
    ...     text("shrink") | border | shrink | border_dashed | flex,
    ...     text("shrink_y") | border | shrink_y | border_dashed | flex,
    ...     text("shrink_x") | border | shrink_x | border_dashed | flex,
    ... ])
    >>> print(layout_to_str(layout, Rect(70, 10)))
    ┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐
    ╎┌─────────────┐╎╎┌──────┐       ╎╎┌──────────────┐╎╎┌────────┐      ╎
    ╎│no shrink    │╎╎│shrink│       ╎╎│shrink_y      │╎╎│shrink_x│      ╎
    ╎│             │╎╎└──────┘       ╎╎└──────────────┘╎╎│        │      ╎
    ╎│             │╎╎               ╎╎                ╎╎│        │      ╎
    ╎│             │╎╎               ╎╎                ╎╎│        │      ╎
    ╎│             │╎╎               ╎╎                ╎╎│        │      ╎
    ╎│             │╎╎               ╎╎                ╎╎│        │      ╎
    ╎└─────────────┘╎╎               ╎╎                ╎╎└────────┘      ╎
    └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘

:func:`~functui.common.padding`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    >>> from functui import Rect, layout_to_str
    >>> from functui.common import *
    >>> from functui.flex import hbox_flex, flex
    >>> layout = hbox_flex([ # hbox_flex used to give all children equal space
    ...     text("no padding") | border | border_dashed | flex,
    ...     text("padding") | border | padding | border_dashed | flex,
    ...     text("custom_padding\ntop=0\nbottom=1\nleft=2\nright=3")
    ...         | border | custom_padding(0, 1, 2, 3) | border_dashed | flex,
    ... ])
    >>> print(layout_to_str(layout, Rect(70, 10)))
    ┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐
    ╎┌───────────────────┐╎╎ ┌─────────────────┐ ╎╎  ┌───────────────┐   ╎
    ╎│no padding         │╎╎ │padding          │ ╎╎  │custom_padding │   ╎
    ╎│                   │╎╎ │                 │ ╎╎  │top=0          │   ╎
    ╎│                   │╎╎ │                 │ ╎╎  │bottom=1       │   ╎
    ╎│                   │╎╎ │                 │ ╎╎  │left=2         │   ╎
    ╎│                   │╎╎ │                 │ ╎╎  │right=3        │   ╎
    ╎│                   │╎╎ │                 │ ╎╎  └───────────────┘   ╎
    ╎└───────────────────┘╎╎ └─────────────────┘ ╎╎                      ╎
    └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘

:func:`~functui.common.center`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    >>> from functui import Rect, layout_to_str
    >>> from functui.common import *
    >>> from functui.flex import hbox_flex, flex
    >>> layout = hbox_flex([ # hbox_flex used to give all children equal space
    ...     text("no center") | border | border_dashed | flex,
    ...     text("center") | border | center | border_dashed | flex,
    ...     text("center_x") | border | center_x | border_dashed | flex,
    ...     text("center_y") | border | center_y | border_dashed | flex,
    ... ])
    >>> print(layout_to_str(layout, Rect(70, 10)))
    ┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐
    ╎┌─────────────┐╎╎               ╎╎   ┌────────┐   ╎╎                ╎
    ╎│no center    │╎╎               ╎╎   │center_x│   ╎╎                ╎
    ╎│             │╎╎               ╎╎   │        │   ╎╎                ╎
    ╎│             │╎╎    ┌──────┐   ╎╎   │        │   ╎╎┌──────────────┐╎
    ╎│             │╎╎    │center│   ╎╎   │        │   ╎╎│center_y      │╎
    ╎│             │╎╎    └──────┘   ╎╎   │        │   ╎╎└──────────────┘╎
    ╎│             │╎╎               ╎╎   │        │   ╎╎                ╎
    ╎└─────────────┘╎╎               ╎╎   └────────┘   ╎╎                ╎
    └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘

:func:`~functui.common.clamp_width` and :func:`~functui.common.clamp_height`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

>>> from functui import Rect, layout_to_str
>>> from functui.common import *
>>> from functui.flex import hbox_flex, flex
>>> 
>>> def title(s):
...     return border_with_title(text(s) | center, border_dashed)
>>> 
>>> TEXT = "lorem ipsum\nlorem ipsum\nlorem ipsum"
>>> layout = hbox_flex([ # hbox_flex used to give all children equal space
...     text(TEXT) | border | title("no clamp") | flex,
...     text(TEXT) | border | clamp_height(3) | title("clamp_height(3)") | flex,
...     text(TEXT) | border | clamp_width(6) | title("clamp_width(6)") | flex,
... ])
>>> print(layout_to_str(layout, Rect(70, 10)))
┌╌╌╌╌╌╌╌no clamp╌╌╌╌╌╌┐┌╌╌╌clamp_height(3)╌╌╌┐┌╌╌╌╌clamp_width(6)╌╌╌╌┐
╎┌───────────────────┐╎╎┌───────────────────┐╎╎┌────┐                ╎
╎│lorem ipsum        │╎╎│lorem ipsum        │╎╎│lore│                ╎
╎│lorem ipsum        │╎╎└───────────────────┘╎╎│lore│                ╎
╎│lorem ipsum        │╎╎                     ╎╎│lore│                ╎
╎│                   │╎╎                     ╎╎│    │                ╎
╎│                   │╎╎                     ╎╎│    │                ╎
╎│                   │╎╎                     ╎╎│    │                ╎
╎└───────────────────┘╎╎                     ╎╎└────┘                ╎
└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘

:func:`~functui.common.offset`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

>>> from functui import Rect, layout_to_str
>>> from functui.common import *
>>> from functui.flex import hbox_flex, flex
>>> layout = hbox_flex([ # hbox_flex used to give all children equal space
...     text("no offset") | border | shrink | border_dashed | flex,
...     text("offset(x=1, y=2)")
...         | border | shrink | offset(1, 2) | border_dashed | flex,
...     text("offset(x=-1, y=0)")
...         | border | shrink | offset(-1, 0) | border_dashed | flex,
... ])
>>> print(layout_to_str(layout, Rect(70, 10)))
┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐
╎┌─────────┐          ╎╎                     ╎┌─────────────────┐    ╎
╎│no offset│          ╎╎                     ╎│offset(x=-1, y=0)│    ╎
╎└─────────┘          ╎╎ ┌────────────────┐  ╎└─────────────────┘    ╎
╎                     ╎╎ │offset(x=1, y=2)│  ╎╎                      ╎
╎                     ╎╎ └────────────────┘  ╎╎                      ╎
╎                     ╎╎                     ╎╎                      ╎
╎                     ╎╎                     ╎╎                      ╎
╎                     ╎╎                     ╎╎                      ╎
└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘

:func:`~functui.common.min_width` and :func:`~functui.common.min_height`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


>>> from functui import Rect, layout_to_str
>>> from functui.common import *
>>> from functui.flex import hbox_flex, flex
>>> 
>>> def title(s):
...     return border_with_title(text(s) | center, border_dashed)
>>> 
>>> TEXT = "lorem ipsum\nlorem ipsum\nlorem ipsum"
>>> layout = hbox_flex([ # hbox_flex used to give all children equal space
...     text(TEXT) | border | shrink | title("default") | flex,
...     text(TEXT) | border | min_width(16) | shrink | title("min_width(16)") | flex,
...     text(TEXT) | border | min_height(7) | shrink | title("min_height(7)") | flex,
... ])
>>> print(layout_to_str(layout, Rect(70, 10)))
┌╌╌╌╌╌╌╌default╌╌╌╌╌╌╌┐┌╌╌╌╌min_width(10)╌╌╌╌┐┌╌╌╌╌╌min_height(6)╌╌╌╌┐
╎┌───────────┐        ╎╎┌──────────────┐     ╎╎┌───────────┐         ╎
╎│lorem ipsum│        ╎╎│lorem ipsum   │     ╎╎│lorem ipsum│         ╎
╎│lorem ipsum│        ╎╎│lorem ipsum   │     ╎╎│lorem ipsum│         ╎
╎│lorem ipsum│        ╎╎│lorem ipsum   │     ╎╎│lorem ipsum│         ╎
╎└───────────┘        ╎╎└──────────────┘     ╎╎│           │         ╎
╎                     ╎╎                     ╎╎│           │         ╎
╎                     ╎╎                     ╎╎└───────────┘         ╎
╎                     ╎╎                     ╎╎                      ╎
└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘

.. note::

   It is safe to set min_width/height to a value that is less than content size.



Input
-----

Minimal Setup
~~~~~~~~~~~~~

.. code-block:: python

    from functui.io.raw import terminal

    with terminal() as term:
        while True:
            layout = ...

            # render
            res = layout_to_result(layout, term.get_terminal_size())
            term.display_result(res)

            # wait for input
            event = term.block_until_input()

            # update (do something with input)
            if event.key_event == "ctrl+c":
                break # exit program by breaking out of the loop

