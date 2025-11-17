Glossary
========


.. glossary::

    ``|``
        A pipe.
        An operator that passes the left operant into the function on the right.

    node
        A function that returns a :obj:`functui.classes.Layout`.

    wrapper node
        A type of node that both returns and takes in a layout as an argument.
        Example wrapper nodes are :obj:`functui.common.border` and :obj:`functui.common.shrink`.

    container node
        A type of node that takes in multiple nodes. Names for container nodes often contain a 'box' suffix.
        Example container nodes are :obj:`functui.common.vbox` and :obj:`functui.common.static_box`.

    data node
        A type of node that does not take in any child layouts.
        Example data nodes are :obj:`functui.common.text` and :obj:`functui.common.vbar`.

    child
        In a layout, a child layout is a layout returned by a note to the right of the pipe (``|``).
        In the layout ``text("foo") | border`` text is a child of border.

    parent
        In a layout, a parent layout is a layout returned by a note to the left of the pipe (``|``).
        In the layout ``text("foo") | border`` border is a parent of text.

    descendants
        In a layout, descendants are layouts returned by nodes to the right of the pipe (``|``).
        In the layout ``text("foo") | border | center`` text and border are descendants of center.

