# Introduction
This page will teach you important concepts and terminology by going through some simple examples 

## Basic Usage 
A program rendering a styled string

```py
from functui import Rect, layout_to_str
from functui.nodes.common import *

layout = text("Welcome to the functui introduction!") | border | center
layout_to_str(layout, Rect(10, 10))
```



{func}`text` {func}`border` and {func}`center` are Nodes. Nodes are just python functions.
Nodes are often called with the pipe `|` syntax. The example layout is identical to the following:

```py
layout = center(border(text("Welcome to the functui introduction")))
```

{func}`border` and {func}`center` are wrapper nodes. A node returns a {class}`layout` which can be expanded on by wrapper nodes. 
In the above example the text node returned a layout that got 'piped' into the border node.
The border node expanded the layout (by adding a border) and then returned a new layout.

```{important}
By default layouts take up as much space as they can.
Wrapper nodes limits their children's sizes and decide their position.
```

A good example of that is the {func}`center` node. First the it limits its child to its minimum size, and then centers it in the remaining space.
If the example code did not have the center node, then nothing would be limiting the border and text from taking up all the space.

```py
from functui import Rect, layout_to_str
from functui.nodes.common import *

# no center node this time
layout = text("Welcome to the functui introduction!") | border
layout_to_str(layout, Rect(10, 10))
```

other output

## Rendering
To render a layout functui provide multiple functions, one of the simplest is layout_to_str which turns the layout in to a string and makes it fit in the provided size (defined by a Rect)

```{tip}

If you want the layout to take up the whole terminal you can get the terminals dimentions by using `os.get_terminal_size()`
```
