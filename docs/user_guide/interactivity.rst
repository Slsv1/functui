Interactivity
=============

This page will teach you how to make your application react to user input.

Picking an I/O Method
~~~~~~~~~~~~~~~~~~~~~
To enable interactivity, you need some way to get input from the user. Functui has build in support for multiple ways of gatting input, but if you don't have any strong preferences it is strongly recommended to use the :obj:`functui.io.raw` module which is the in-house solution for cross-platform input and output. The rest of this page will assume that you are using that module, but even if you are not, there are still much to take away from this page.

.. seealso::
    You can get an overview over all I/O methods in the :doc:`io` document.

Using :obj:`functui.io.raw` for Input
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before you start polling for input, it is a good idea to do some terminal configuration. For example, hiding the mouse cursor, enabling mouse events, disabling line wrapping, enabling xterm escape codes on windows, etc. This can be done with the :obj:`~functui.io.raw.terminal` function that returns a context manager that can be used with a ``with`` statement.

.. code-block:: python

    from functui.io.raw import terminal
    
    with terminal() as term:
        # once inside the `with` block, we may wait for input.
        event = term.block_untill_input()
    
    # once we leave the `with` block, all terminal configuration gets reset.

A context manager is used here so that when your application exits, all of the terminal configuration is reverted automatically.

As demonstrated in the above example, the :meth:`~functui.io.raw.TerminalIO.block_untill_input` method is used to get input. That method returns an :obj:`~functui.classes.InputEvent` object, which is best explained with the API documentation below.

.. autoclass:: functui.classes.InputEvent
    :noindex:
    :members:

The ``mouse_position_event`` is just a coordinate representing the position of the mouse. ``key_event`` returns a string that represents user's input, for example ``"ctrl+c"``, ``"a"`` or ``"left mouse"```. The noteble thing here is that many modifier key combinations are not supported due to terminal wierdness. For example ``ctrl+i`` is missing because it emmits the same control code as when pressing ``tab``. Or even worse ``alt+`` combinations are not supported at all due to needing to rely on timings to distinguish them from pressing ``esc`` followed by some other key. All of those input quirks are documented in the :doc:`keycodes` document.

Rendering
~~~~~~~~~

When it comes to rendering an interactive application, functui takes the most stupidly simple approach, namely redrawing the whole application every frame (also known as "immidiate mode" ui).

This approach may seem wastefull, which it may be to some extent, but the pros of this approach vastly outweigh the cons. Firstly a lot of ui's require redrawing everything every frame anyway, think of the system profiler htop. Secondly, even if you don't redraw every frame, functui's node's rendering functions are cached, meaning given the same layout structure, the rendering function won't need to calculate everything again.

But most importantly, immidiate mode ui simplifies your code, by *a lot*! Since your layout gets redrawn every frame, it becomes a direct representation of your program's state. No need to worry about updating the ui when you change some variable, your ui will reflect the variable's state automatically! And with immidiate mode ui, there is no need to use callbacks or implement reactive programming patterns since there just isn't anything to react to.

The Elm Architecture
~~~~~~~~~~~~~~~~~~~~

Now when we know that we will be redrawing the ui every frame, structuring the application becomes simple. A common software architecture for immidate mode ui is "the elm architecture" which separates your program into three parts which all have a unique responsibility.

- **The Model** A class that contains all of your programs mutable state. It is recommended to implements it with the :obj:`~dataclasses.dataclass` decorator to avoid writing boilerplate code.

.. code-block:: python

    from dataclasses import dataclass
    from functui.nav import NavState

    @dataclass
    class Model:
        nav: NavState =  NavState() # for keyboard and mouse navigation (more on that later)
        foo: int
        bar: str
        ... # and other variables you need in your program


- **The View Function** - A function that renders the layout based on the model's state. Here it is important that it does not change anything about the model. This way, your rendering code is separated from your logic which makes your program much simpler.

.. code-block:: python

   def view(m: Model):
       layout = text(str(m.foo)) | border
       return layout

- **The Update Function** - A function that does all the logic and changes the model.

.. code-block:: python

   def update(m: Model, event: InputEvent):
       if event.key_event == "ctrl+k"
           ... # do something

Then the update and view functions are called every frame to run your applications. Normally calling those function is the library's responsibility, but with elm architecture being so simple, funtio leave connecting everything up to you.
 

.. code-block:: python
    
    from functui.io.raw import terminal

    m = Model()

    def view(m: Model):
        return text("hello world")

    def update(m: Model, event: InputEvent):
        ...
        

    with terminal() as term:
        while True:
            # render and fit terminal
            res = layout_to_result(view(m), term.get_terminal_size())
            term.display_result(res)

            # wait for input
            event = term.block_untill_input()

            # update
            if event.key_event == "ctrl+c":
                break # exit program
            update(event, res, m)




