I/O
===

Functui has multiple modules of doing input and output.

.. seealso::

   :doc:`interactivity`

.. seealso::
    
    Generaly input functions will return an :obj:`~functui.classes.InputEvent` which stores the input in a special string format. That format is specified in :ref:`keycode-specification`.

:obj:`functui.io.raw`
---------------------

Recomended for all interactive applications. (keyboard and mouse).
Used the :obj:`functui.io.ansi` to render.

Input - ✅
~~~~~~~~~~

Full mouse and keyboard support.


Output - ✅
~~~~~~~~~~~

Displays the layout with ansi escape codes.

.. seealso::
    :func:`~functui.io.raw.terminal` and :ref:`examples_elm`


----

:obj:`functui.io.ansi`
----------------------

Recommended if you need functui just for rendering.

Input - ❌
~~~~~~~~~~

For very simple projects you may use python's build in :func:`input`.
Otherwise, there is no build in way to get a :obj:`functui.classes.InputEvent` with this io method. 


Output - ✅
~~~~~~~~~~~

Renders a layout as a string with ansi escape codes which are supported by virtually all terminals. Then you can simply just use the :func:`print` function to display that string.

Quirks
~~~~~~

- Output performance is not very good right now.


.. seealso::
    :func:`~functui.io.ansi.layout_to_str` and :func:`~functui.io.ansi.result_to_str` for output. And :ref:`example_elm_counter_app` example.

----


:obj:`functui.io.curses`
------------------------

Recommended for legacy interactive applications on unix.


Input - ✅
~~~~~~~~~~

Full mouse and keyboard support.


Output - ✅
~~~~~~~~~~~

Displays the layout in a curses window.


Quirks
~~~~~~

- Does not work on windows.
- Does not support :ref:`color24` (rgb colors)
- Only 256 unique foreground and background combinations may be used at a time.
- :obj:`~functui.classes.StyleAttr.STRIKE_THROUGH` style is not supported

.. seealso::
    :func:`~functui.io.curses.wrapper`, :func:`~functui.io.curses.get_input_event`, :func:`~functui.io.curses.draw_result` and :ref:`example_curses_elm_template` example.

----

:obj:`functui.io.html`
----------------------

Input - ❌
~~~~~~~~~~

No input support.


Output - ✅
~~~~~~~~~~~

Wraps the layout in a ``<pre>`` tag.


Quirks
~~~~~~

- :obj:`~functui.classes.StyleAttr.DIM` is not supported.
To display functui layouts on the web.

