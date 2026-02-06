The Elm Architecture
====================

Functui does not force any design patterns on you and lets you structure your application how you please.
But if you don't have an exact idea of how to structure you application it is strongly recommended to use the elm architecture.

The elm architecture separates you program into three parts:

- **The Model**
    A data class that includes all of your programmes mutable state.

- **View Function**
    A pure function who's purpose is to convert the model into a renderable UI.

- **Update Function**
    Update the model based on user input.

Below follows a very simple example of the elm architecture being used for a coutner app.

.. code-block:: py

    from dataclasses import dataclass
    from functui.common import *
    from functui import layout_to_str, Rect, Layout

    import os

    # To avoid writing boilerplate use a dataclass that is included
    # in pythons standart library.
    @dataclass
    class Model():
        counter: int = 0

    def update(input: str, m: Model):
        if input == "i":
            m.counter += 1
        elif input == "d":
            m.counter -= 1

    def view(m: Model) -> Layout:
        layout = text(str(m.counter)) | center | border
        return layout

    m = Model()

    # Event loop.
    while True:
        # first clear terminal and draw
        os.system('cls' if os.name == 'nt' else 'clear')
        print(layout_to_str(layout=view(m), dimensions=Rect(11, 3)))

        # then get input
        i = input()
        if i == "exit":
            break # exit program

        # then update
        update(i, m)

