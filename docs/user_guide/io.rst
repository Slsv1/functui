Input/Output
============

On top of providing nodes for creating UI layouts functui also has tools to make your UIs reactive to user input.


Interactive Example
-------------------

Below follows a simple application that reacts to keyboard input.

.. code:: python

    from functui import open_terminal, render_fit_terminal, Screen
    from functui.nodes import *

    # application state
    screen = Screen()
    should_show_border = False

    with open_terminal() as term:
        while True: # application loop

            # render

            layout = text("press 'b' to toggle border")\
                | (border if should_show_border else empty)\
                | center

            result = render_fit_terminal(term, screen, layout)

            # wait

            event = term.wait_for_input()

            # update

            if event.key_event == "ctrl+c":
                break # exit program
            elif event.key_event == "b":
                should_show_border = not should_show_border

Example Explanation
-------------------


Structure
~~~~~~~~~

Functui was designed around the immideate mode ui philosophy, where the layout is rebuilt every frame (in contrast to the more conventional retained mode ui where the layout is retained between frames). Hence the application is build arond a ``while True`` loop where every iteration the layout variable is redefined to reflect the applications state.


Why the ``with`` block?
~~~~~~~~~~~~~~~~~~~~~~~


The ``with`` block is needed for the application to take control of the terminal and be able to wait for input. Once the ``with`` block is exited, the terminal is reset to normal.

.. tip:: 

    On top of allowing for input :func:`~functui.open_terminal` also changes some other terminal configuration, for example switching you to another terminal tab (formally known as the alternate buffer) to avoid ruining your scrollback history. What gets configured can be changed by passing a custom :class:`~functui.TerminalFeatures` object into :func:`~functui.open_terminal`

Why :obj:`~functui.Screen`?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :obj:`~functui.Screen` is the intermediate buffer to which a layout gets rendered to before being sent to the terminal. It is needed to keep some rendering data between frames for optimisation's sake.


What not :func:`~functui.render_simple`?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Here we use the :func:`~functui.render_fit_terminal` since it reuses the :obj:`~functio.Screen` instead of creating a new one every draw call as ``render_simple()``. 

.. tip::

    The :func:`~functui.render_fit_terminal` function is used to both render to the buffer and forward that data to the terminal, but these steps can also be done manually if greater control over the rendering pipeline is needed. Just look at the :func:`~functui.render_fit_terminal`s source code.

:func:`~functui.wait_for_input`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Input can be polled for using the :func:`~functui.wait_for_input` function. It returns an :obj:`~functui.InputEvent` object which may store a ``mouse_poisition_event`` and ``key_event``. Key events are represented using strings.

.. warning::

    Due to historical reasons some keyboard inputs you would expect to work do not. Notably, there is no support for ``alt+`` combinations and some ``ctrl+`` compinations do not work (``i`` ``j`` and ``m``). 

A simple example handling different key events:

.. code-block:: python

    from functui import open_terminal


    with open_terminal() as term:
        event = term.wait_for_input()

        # update

        # ctrl+ combination
        if event.key_event == "ctrl+c": 
            ...

        # no key event emited
        elif event.key_event is None: 
            ...

        # regular letter
        elif event.key_event == "b":
            ...

        # uppercase letter (shift+)
        elif event.key_event == "B":
            ...

        # space
        elif event.key_event == " ":
            ...

        # unicode character
        elif event.key_event == "ö":
            ...

        # special keys
        elif event.key_event in ("backspace", "enter", "escape"):
            ...

        # arrow keys
        elif event.key_event in ("up", "down", "left", "right"):
            ...

        # unknown key
        elif event.key_event == "unknown":
            ...

Result
~~~~~~
:func:`~functui.render_fit_terminal` returns a :obj:`~functui.ResultData` object. It stores some render metadata and where on the screen and how big nodes decorated with :obj:`~functui.nodes.hoverable` were. This data can be used to implement mouse support which is discussed in the next section.


