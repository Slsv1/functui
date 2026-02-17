Interactivity
=============

This page will teach you how to get user input and make your application react to it.

Picking an I/O Method
~~~~~~~~~~~~~~~~~~~~~
To enable interactivity, you need some way to get input from the user.
Functui has built in support for multiple ways of getting input,
but if you don't have any strong preferences it is strongly recommended to use the :obj:`functui.io.raw` module which is the in-house solution for cross-platform input and output. The rest of this page will assume that you are using that module, but even if you are not, there are still much to take away from this page.

.. seealso::
    You can get an overview over all I/O methods in the :doc:`io` document.

Using :obj:`functui.io.raw` for Input
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before you start polling for input, it is a good idea to do some terminal configuration. For example, hiding the mouse cursor, enabling mouse events, disabling line wrapping, enabling xterm escape codes on windows, etc. This can be done with the :obj:`~functui.io.raw.terminal` function that returns a context manager that can be used with a ``with`` statement.

.. code-block:: python

    from functui.io.raw import terminal
    
    with terminal() as term:
        # once inside the `with` block, we may wait for input.
        event = term.block_until_input()
    
    # once we leave the `with` block, all terminal configuration gets reset.

A context manager is used here so that when your application exits, all of the terminal configuration is reverted automatically.

As demonstrated in the above example, the :meth:`~functui.io.raw.TerminalIO.block_until_input` method is used to get input. That method returns an :obj:`~functui.classes.InputEvent` object, which is best explained with the API documentation below.

.. autoclass:: functui.classes.InputEvent
    :noindex:
    :members:

The ``mouse_position_event`` is just a coordinate representing the position of the mouse. ``key_event`` returns a string that represents user's input, for example ``"ctrl+c"``, ``"a"`` or ``"left mouse"```. The noteble thing here is that many modifier key combinations are not supported due to terminal wierdness. For example ``ctrl+i`` is missing because it emmits the same control code as when pressing ``tab``. Or even worse ``alt+`` combinations are not supported at all due to needing to rely on timings to distinguish them from pressing ``esc`` followed by some other key. All of those input quirks are documented in the :doc:`keycodes` document.

Rendering
~~~~~~~~~

When it comes to rendering an interactive application, functui takes the most stupidly simple approach, namely redrawing the whole application every frame (also known as "immidiate mode" ui).

This approach may seem wastefull, which it may be to some extent, but the pros of this approach vastly outweigh the cons. Firstly a lot of ui's require redrawing everything every frame anyway, think of the system profiler htop. Secondly, even if you don't redraw every frame, functui's node's rendering functions are cached, meaning given the same layout structure, the rendering function won't need to calculate everything again.

But most importantly, immidiate mode ui simplifies your code, by *a lot*! Since your layout gets redrawn every frame, it becomes a direct representation of your program's state. No need to worry about updating the ui when you change some variable, your ui will reflect the variable's state automatically! And with immidiate mode ui, there is no need to use callbacks or implement reactive programming patterns since there just isn't anything to react to.

.. _apply_immidiate_mode:

Applying the Immidiate Mode Approach
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now when we know that we will be redrawing the ui every frame, structuring the application becomes easy. We can put the application rendering code into a while loop and just re-render everytime we get some input.
Also we can use :func:`~functui.io.raw.TerminalIO.get_terminal_size` method to make the layout respond to terminal size and use :func:`~functui.io.raw.TerminalIO.display_to_result` to render the layout.

.. code-block:: python

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
                break # exit program
    
.. tip::
    As you may have noticed, we used :func:`~functui.classes.layout_to_result` instead of :func:`~functui.io.ansi.layout_to_str` which was taught in the introduction.
    The former function returns a :obj:`~functui.classes.Result` object which contains all the draw commands required to render the layout.
    This intermidiate step (converting to result and then rendering instead of just rendering) is very usefull because the ``Result``
    object can stora additional data apart from draw commands. For example, the size and position of nodes, which is needed to implement mouse hover and such.
            

The Elm Architecture
~~~~~~~~~~~~~~~~~~~~

The above example turns out to be very similar to "the elm architecture" which is a common software architecture pattern for immidiate mode ui's, and is the recommened way to structure your functui applications. 
The elm architectures separates your program into three parts which all have a unique responsibility.

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

Then the update and view functions are called every frame to run your application.
Putting it all toghether looks something like this:
 

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
            event = term.block_until_input()

            # update
            if event.key_event == "ctrl+c":
                break # exit program
            update(event, res, m)


.. tip::

    The elm architecture is really similar to the example under the :ref:`apply_immidiate_mode` section. It is encouraged to look for the differences between those two examples.

Mouse and Keyboard Navigation?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that you know how to get user input and how to structure you're code, the time has come to work with actuall widgets like buttons, scrollable lists etc. Those are enabled by the :obj:`functui.nav` module discussed in the next document.


