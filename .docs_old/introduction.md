# Introduction
!!! abstract
    This introduction will introduce you to core concepts and terminology of functui.

## Basic Usage 
A program rendering a styled string
```py
from functui import Rect, layout_to_str
from functui.nodes.common import *

layout = text("Welcome to the functui introduction!") | border | center
layout_to_str(layout, Rect(10, 10))
```
```
example lol
```

## Nodes
text border and center are Nodes. Nodes are just python functions.


## Pipe syntax
Nodes are often called with the pipe `|` syntax. The example layout is identical to the following:
```py
    layout = center(border(text("Welcome to the functui introduction")))
```
## Wrapper nodes
border and center are wrapper nodes.
### Wrapper nodes expand layouts.
!!! info
    A node returns a layout which can be expanded on by wrapper nodes. 

In the above example the text nodes returned a layout that got piped into the border node which expanded on it by adding the border and then returned a new layout.

### Wrapper nodes control their children

!!! info
    By default layouts take up as much space as they can.
    Wrapper nodes limits their children's sizes and decide their position.

A good example of that is the center node. First the center node limits its child to its minimum size, and then centers it in the available space.

If the example code did not have the center node, then nothing would be limiting the border and text layout from taking up all the space.

```py
from functui import Rect, layout_to_str
from functui.nodes.common import *

layout = text("Welcome to the functui introduction!") | border # no center node this time
layout_to_str(layout, Rect(10, 10))
```
```
other output
```

## Rendering
To render a layout functui provide multiple functions, one of the simplest is layout_to_str which turns the layout in to a string and makes it fit in the provided size (defined by a Rect)

!!! tip
    If you want the layout to take up the whole terminal you can get the terminals dimentions by using `os.get_terminal_size()`

