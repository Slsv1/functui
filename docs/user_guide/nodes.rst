Nodes
=====

Interactive
-----------

.. autofunction:: functui.nodes.hoverable
.. autofunction:: functui.nodes.view_text_input

.. important::

    Most interactive nodes are methods of stateful components and are not just pure functions like all of the nodes in this document.
    Components that provide or are used by interactive nodes:

    - :obj:`functui.NavState`
    - :obj:`functui.TextInput`



Utility
-------

.. autofunction:: functui.nodes.combine
.. autofunction:: functui.nodes.empty
.. autofunction:: functui.nodes.nothing

Containers
----------

.. autofunction:: functui.nodes.hbox
.. autofunction:: functui.nodes.vbox
.. autofunction:: functui.nodes.hbox_flex
.. autofunction:: functui.nodes.vbox_flex
.. autofunction:: functui.nodes.vbox_flex_wrap
.. autofunction:: functui.nodes.static_box

Sizing
------

.. autofunction:: functui.nodes.center
.. autofunction:: functui.nodes.hcenter
.. autofunction:: functui.nodes.vcenter
.. autofunction:: functui.nodes.padding
.. autofunction:: functui.nodes.hpadding
.. autofunction:: functui.nodes.shrink
.. autofunction:: functui.nodes.hshrink
.. autofunction:: functui.nodes.vshrink
.. autofunction:: functui.nodes.constrain
.. autofunction:: functui.nodes.floating

Borders
-------

.. autofunction:: functui.nodes.border
.. autofunction:: functui.nodes.border_rounded
.. autofunction:: functui.nodes.border_dashed
.. autofunction:: functui.nodes.border_rounded_dashed
.. autofunction:: functui.nodes.border_thick
.. autofunction:: functui.nodes.border_thick_dashed
.. autofunction:: functui.nodes.border_double
.. autofunction:: functui.nodes.border_ascii
.. autofunction:: functui.nodes.border_custom


Styling
-------


.. autofunction:: functui.nodes.style
.. autofunction:: functui.nodes.styled
.. autofunction:: functui.nodes.styled_bg
.. autofunction:: functui.nodes.styled_fg
.. autofunction:: functui.nodes.bg_char
.. autofunction:: functui.nodes.bg_fill

Attributes
~~~~~~~~~~

.. code-block:: py

    from functui import render_simple, Color4, rgb
    from functui.nodes import text, border, vbox, fg, bg,\
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

    print(render_simple(layout, 20, 12))

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

.. autofunction:: functui.nodes.fg
.. autofunction:: functui.nodes.bg
.. autofunction:: functui.nodes.underline
.. autofunction:: functui.nodes.italic
.. autofunction:: functui.nodes.dim
.. autofunction:: functui.nodes.bold
.. autofunction:: functui.nodes.blink
.. autofunction:: functui.nodes.strike_through
.. autofunction:: functui.nodes.reverse

Content
-------

.. autofunction:: functui.nodes.text
.. autofunction:: functui.nodes.adaptive_text
.. autofunction:: functui.nodes.hguage

Bars
----

.. py:data:: functui.nodes.vbar
.. py:data:: functui.nodes.vbar_thick
.. py:data:: functui.nodes.vbar_double
.. py:data:: functui.nodes.vbar_ascii
.. autofunction:: functui.nodes.vbar_custom

.. py:data:: functui.nodes.hbar
.. py:data:: functui.nodes.hbar_thick
.. py:data:: functui.nodes.hbar_double
.. py:data:: functui.nodes.hbar_ascii
.. autofunction:: functui.nodes.hbar_custom
