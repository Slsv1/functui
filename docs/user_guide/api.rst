General Constants
-----------------
.. py:data:: functui.LOREM

    Dummy text.

.. autoclass:: functui.BgChars

.. autodata:: functui.DEFAULT_TEXT_INPUT_BINDINGS

.. py:data:: functui.DRACULA_COLOR_THEME

.. py:data:: functui.GRUVBOX_COLOR_THEME

.. py:data:: functui.NORD_COLOR_THEME

.. py:data:: functui.SOLARIZED_COLOR_THEME

.. py:data:: functui.COLOR_THEMES
    :type: dict[str, Theme]


General Data Types
------------------


.. autoclass:: functui.Box
   :members:

.. autoclass:: functui.Rect
   :members:

.. autoclass:: functui.Coordinate
   :members:

.. autotype:: functui.TerminalColor

.. autoclass:: functui.Color
   :members:

.. autoclass:: functui.Theme
   :members:

.. autoclass:: functui.Layout
   :members:

.. autoclass:: functui.WrapperNode

.. autoclass:: functui.Screen
   :members:

.. autoclass:: functui.InputEvent
   :members:

.. autoclass:: functui.StyleAttr
   :members:

.. autoclass:: functui.Allignment

Components
==========

NavState
--------

.. autoclass:: functui.NavState
   :members:

.. autoclass:: functui.Direction

.. autofunction:: functui.vnav

.. autofunction:: functui.hnav

.. autoclass:: functui.NavScrollableData
   :members:

.. autofunction:: functui.nav_parse_event

.. autoclass:: functui.NavAction

TextInput
---------

.. autoclass:: functui.TextInput
   :members:

.. autoclass:: functui.TextAction

.. autoclass:: functui.TextActionChar
   :members:

.. autoclass:: functui.TextActionPaste
   :members:

.. autoclass:: functui.TextInputStyle

.. autofunction:: functui.text_input_parse_event
