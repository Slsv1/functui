Keyboard and Mouse
==================

On top of creating layouts, functui also can handle terminals to enable getting character input and querreing for terminal size.


A simple keyboard input example

.. code:: python

    from functui import open_terminal

    with open_terminal() as term:
        event = term.wait_for_input()

        # usage: (key events are stored as strings)

        if event.key_event == "ctrl+c":
            ...
        elif event.key_event == "[":
            ...
        elif event.key_event == "a":
            ...
        elif event.key_event == "backspace":
            ...


Notice the ``with`` block, it is needed for the application to take control of the terminal and be able to wait for input. Once the ``with`` block is exited, the terminal is reset to normal.

Also on top of just allowing for input :func:`functui.open_terminal` also changes some other terminal configuration, for example switching you to another terminal tab (formally known as the alternate buffer) to avoid ruining your scrollback history. What gets configuraed can be changed by passing a custom :class:`functui.TerminalFeatures` object into :func:`functui.open_terminal`

.. warning::

    Due to historical reasons some keyboard inputs you would expect to work do not. Notably, there is no support for ``alt+`` combinations and some ``ctrl+`` compinations do not work (``i`` ``j`` and ``m``). 

Mouse
-----


