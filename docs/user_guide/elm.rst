The Elm Architecture
====================


Functui does not force any design patterns on you and lets you structure your application how you please.
But if you don't have an exact idea of how to structure you application it is strongly recommended to use the elm architecture.

.. seealso::

    :ref:`examples_elm`

The elm architecture separates you program into three parts:

- **The Model**
    A data class that includes all of your programmes mutable state.

- **View Function**
    A pure function who's purpose is to convert the model into a renderable UI.

- **Update Function**
    Update the model based on user input.

Below follows a very simple example of the elm architecture being used for a coutner app.

.. literalinclude:: ../../examples/ansi_elm_counter_app.py

