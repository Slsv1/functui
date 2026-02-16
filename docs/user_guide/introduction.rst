Introduction
============

This page will teach you important concepts and terminology by going through some simple examples 

Basic Usage
-----------
A program rendering a simple layout.


.. testcode::

    from functui import Rect, layout_to_str
    from functui.common import *  # for border, center, text and bg_char

    layout = text("Bonjour") | border | center | bg_char(".")
    output = layout_to_str(layout, Rect(width=11, height=7))
    print(output)

Expected output:

.. testoutput::

    ...........
    ...........
    .┌───────┐.
    .│Bonjour│.
    .└───────┘.
    ...........
    ...........


:func:`~functui.common.text` :func:`~functui.common.border` :func:`~functui.common.center` and :func:`~functui.common.bg_char` are Nodes.
Nodes are just python functions.
Nodes are often called with the pipe `|` syntax. The example layout is identical to the following:

.. code-block:: py

    layout = bg_char(".")(center(border(text("Welcome to the functui introduction"))))


:func:`~functui.common.border` and :func:`~functui.common.center` are wrapper nodes. A node returns a :class:`~functui.classes.Layout` which can be expanded on by wrapper nodes. 
In the above example the text node returned a layout that got 'piped' into the border node.
The border node expanded the layout (by adding a border) and then returned a new layout.
But wrapper nodes have more functionality apart from adding visuals, they also limit their children's size.

.. important::

    By default layouts take up as much space as they can.
    Wrapper nodes limits their children's sizes and decide their position.

A good example of a wrapper node limiting their childrens size
is the center node.
First it limits its child to its minimum size,
and then centers it in the remaining space.
If the example code did not have the center node,
then nothing would be limiting the border and text from taking up all the space.

.. testcode::

    from functui import Rect, layout_to_str
    from functui.common import *

    # no center node this time

    layout = text("Bonjour") | border | bg_char(".")
    print(layout_to_str(layout, Rect(11, 7)))


Expected output:

.. testoutput::

    ┌─────────┐
    │Bonjour..│
    │.........│
    │.........│
    │.........│
    │.........│
    └─────────┘

Rendering
---------
To render a layout you can simply use the :func:`~functui.io.ansi.layout_to_str`
function with a :class:`~functui.classes.Rect` to specifiy dimensions.

.. seealso::

    All different output formats can be found in :doc:`io`.

Containers
----------

While rendering text with a border is fun, it is not very usefull for creating layouts unless you have containers than can manage the position and size of multiple children. A simple container node is a :func:`~functui.common.vbox`.

.. testcode::

    from functui import Rect, layout_to_str
    from functui.common import *

    layout = vbox([
        text("foo"),
        hbar(),
        text("bar"),
        text("buz") | border,
    ]) | border

    print(layout_to_str(layout, Rect(20, 9)))

Expected output:

.. testoutput::

    ┌──────────────────┐
    │foo               │
    │------------------│
    │bar               │
    │┌────────────────┐│
    ││buz             ││
    │└────────────────┘│
    │                  │
    └──────────────────┘    

A container's children are just regular nodes,
meaning that you can put wrapper nodes around them
(As we did with the border around the 'buz' text node).
We also used a :func:`~functui.common.hbar` node to create a horizonal rule.

Continuing on this trend of everything being nodes, containers are nodes themselved,
meaning that you can nest containers inside eachother.

.. testcode::

    from functui import Rect, layout_to_str
    from functui.common import *

    layout = vbox([
        text("foo"),
        hbox([text("bar"), vbar(), text("buz")]) | border,
    ]) | border

    print(layout_to_str(layout, Rect(20, 9)))

.. testoutput::

    ┌──────────────────┐
    │foo               │
    │┌────────────────┐│
    ││bar|buz         ││
    │└────────────────┘│
    │                  │
    │                  │
    │                  │
    └──────────────────┘

.. tip::

    As you may have noticed, the separator between bar, and buz nodes was created manualy.
    To do this automatically use :func:`~functui.classes.intersperse`.

Summary
-------
- **Node** - A function that returns a :obj:`~functui.classes.Layout`.
- **Wrapper Node** - A function that 'decorates' other layouts as well as manages their size. For example, a :func:`~functui.common.border`
- ``|`` - Operator used for structuring layouts without needing to write a lot of parentheses.
- **Container Node** - A wrapper node than manages the position and size of multiple children. For example, a :func:`~functui.common.vbox`.

What Now?
---------

If you want to just experiment and see what kind of layouts this library can create, check out the :doc:`nodes`.

If you look to add interactive elements (like keyboard and mouse interactions) start with looking at :doc:`elm`.

And of course don't forget about the examples available on GitHub in the ``/examples`` folder or :doc:`here in the docs <examples>`!

