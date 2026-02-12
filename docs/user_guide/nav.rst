Keyboard and Mouse
==================

.. important::

    This page assumes that you have already a way to get a :obj:`~functui.classes.InputEvent`. If that's not the case, check out :doc:`io`.


.. seealso::

    :ref:`examples_elm`

Functui has the :obj:`functui.nav` module which provides the :obj:`~functui.nav.NavState` class and multiple nodes to allow interactivity.

:obj:`~functui.nav.NavState`
----------------------------

The NavState class is an immutable representation of all state related to keyboard navigation and mouse interactivity. Usually an app needs only one ``NavState`` instance. A ``NavState`` object has an :meth:`~functui.nav.NavState.update` method that needs to be call every time user has submitted some input. (For example a key press or a mouse position change). The ``update()`` method returns a new ``NavState`` object that represents the updated state based on input.

The whole signature of the update method is as follows:

.. code-block:: py

    def update(
        self,
        res: Result,
        action: NavAction | None = None,
        nav_data: list[InteractibleID] = field(default_factory=list),
        mouse_position: Coordinate | None = None,
    ):


As you may see the update method has the obvious ``mouse_positon`` argument, but the purpouse of the others can be unclear. Below follows an explanation of how to provide those other arguments and why they are needed.

``action``
~~~~~~~~~~

This is essantially just the user input, but converted to a :obj:`~functui.nav.NavAction` value. You can convert user input stored in an :obj:`~functui.classes.InputEvent` to an ``NavAction`` by using the :obj:`~functui.nav.DEFAULT_NAV_BINDINGS` dictionary. All possible actions are listed below.


.. autoclass:: functui.nav.NavAction
   :no-index:

.. tip::

    This pattern where an update method takes in an action is not unique to ``NavState``. This pattern allows decoupeling how user input is represented from the update method. In other words, with this pattern, the update method does not need to parse user input, this responsibility is deligated to other parts of the program which follows the single responsibility principle.


``res``
~~~~~~~

The result produced from rendering a :obj:`~functui.classes.Layout`. ``NavState`` needs the result in order to know where on the screen certain nodes were rendered. This data is used to check if the mouse position is inside any (for example) buttons or scrollable areas. More on this topic will follow, but in short you use the :func:`~functui.nav.interaction_area` wrapper node to mark nodes as interactible.

.. seealso::

   :func:`~functui.classes.layout_to_result`

``nav_data``
~~~~~~~~~~~~
The keyboard navigation tree. This is discussed in the next section.

Keyboard Navigation
-------------------

To facilitate keyboard navigation, you need to create a tree of :obj:`~functui.nav.InteractibleID` s. Note that this tree is created separatly from the renderable ui tree. To create a simple container that can be vertically navigated through (by pressing up and down) use an ``InteractibleID`` as a container and create children with the :meth:`~functui.nav.InteractibleID.child` method.

To detect if an interactible is active you can use the :meth:`~functui.nav.NavState.is_active` method after the ``update`` method was called.

To detect if an interactible is selected (was active and then enter was pressed) you can use :meth:`~functui.nav.NavState.is_selected` method.

.. testcode:: py

    from functui.nav import InteractibleID, NavState, NavAction, ROOT_VERTICAL

    selectable_1 = ROOT_VERTICAL.child(0)
    selectable_2 = ROOT_VERTICAL.child(1)
    selectable_3 = ROOT_VERTICAL.child(2)
    nav_tree = [selectable_1, selectable_2, selectable_3]

    nav = NavState()

    # at first nothing is active, so navigation in any direction
    # will activate the first item in tree.
    nav = nav.update(nav_tree=nav_tree, action=NavAction.NAV_UP)

    # use .is_active method to test if an interactible is active
    assert nav.is_active(selectable_1)

    # use .is_selected method to test if an interactible is selected()
    nav = nav.update(nav_tree=nav_tree, action=NavAction.SELECT_VIE_KEYBOARD)
    assert nav.is_active(selectable_2)

    nav = nav.update(nav_tree=nav_tree, action=NavAction.NAV_DOWN)
    assert nav.is_active(selectable_2)


You can also nest containers and specify their navigation direction.

.. testcode:: py

    from functui.nav import InteractibleID, NavState, NavAction, ROOT_VERTICAL, Direction

    root = ROOT_VERTICAL

    # directiot=Direction.HORIZONTAL means navigating by
    # NavAction.NAV_LEFT and NavAction.NAV_RIGHT
    inner_container = root.child(0, direction=Direction.HORIZONTAL)
    inner_child_1 = inner_container.child(0)
    inner_child_2 = inner_container.child(1)
    outer_child_1 = root.child(1)

    # the above create a tree that looks something like this
    # x-------------------------------x
    # |x-----------------------------x|
    # || inner_child_1 inner_child_2 ||
    # |x-----------------------------x|
    # | outer_child_1                 |
    # x-------------------------------x

    nav_tree = [inner_child_1, inner_child_2, outer_child_1]

    nav = NavState()

    # just activate keyboard navigation.
    nav = nav.update(nav_tree=nav_tree, action=NavAction.NAV_DOWN)
    assert nav.is_active(inner_child_1)

    nav = nav.update(nav_tree=nav_tree, action=NavAction.NAV_RIGHT)
    assert nav.is_active(inner_child_2)

    nav = nav.update(nav_tree=nav_tree, action=NavAction.NAV_DOWN)
    assert nav.is_active(outer_child_1)


Mouse Detection
---------------

Mouse detection can be performed with an :func:`~functui.nav.interaction_area` wrapper node.

To detect if mouse is hovering over an interactible use the :meth:`~functui.nav.NavState.is_hover` method.

Unlike keyboard navigation, selection is split into two stages. :meth:`~functui.nav.NavState.is_held_down` method returns ``True`` while left click is held down. When left click is relased :meth:`~functui.nav.NavState.is_selected` returns true. This behaviour is usefull for implementing buttons that get highlighted when you hold left click and have ability to be canceled if you move your mouse away.



NavData and The Elm Architecture
--------------------------------

To allow for keyboard and mouse interactivity with the elm architecture set :obj:`~functui.nav.NavAction` as an attribute in your model. 

.. code-block:: py

    @dataclass
    class Model:
         nav: NavData
         ...


Then in the update function update ``NavData`` before doing any other logic. This is so that you can use methods like :meth:`~functui.nav.NavAction.is_selected` and not be a frame behind.

.. code-block:: py
    
    def update(input: InputEvent, res: Result, m: Model):
        action = None
        if input.key_event in default_nav_bindings:
            action = default_nav_bindings[input.key_event]

        m.nav = m.nav.update(
            res=res,
            action=action, 
            nav_tree=[...],
            mouse_position=input.mouse_position_event
        )

        # Put your update code here

        # for example, if a button is pressed do something
        if m.nav.is_selected(...):
            ...

Below follows a template you can copy for elm applications that allows for interactivity.

.. literalinclude:: ../../examples/curses_elm_template.py
