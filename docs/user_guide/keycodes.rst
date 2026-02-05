String Key Codes Specification
==============================

Function io modules convert key input into a string format for convinient use that is often contained within :obj:`functui.classes.InputEvent` objects.
This format however is quite limited due to terminals and their `historical reasons <https://catern.com/posts/terminal_quirks.html>`__.

Recognised non Printable Keys
-----------------------------

- ``escape``
- ``tab``
- ``backspace``
- ``enter``
- ``up``
- ``down``
- ``left``
- ``right``
- ``home``
- ``end``
- ``page up``
- ``page down``
- ``delete``
- ``insert``
- ``f1``
- ``f2``
- ``f3``
- ``f4``
- ``f5``
- ``f6``
- ``f7``
- ``f8``
- ``f9``
- ``f10``
- ``f11``
- ``f12``
- ``f13``
- ``f14``
- ``f15``
- ``f16``
- ``f17``
- ``f18``
- ``f19``
- ``f20``

Mouse
-----

- ``left mouse``
- ``left mouse released``
- ``right mouse``
- ``right mouse released``
- ``midle mouse``
- ``midle mouse released``
- ``mouse wheel up``
- ``mouse wheel down``

Available ``ctrl+`` combinations
--------------------------------

- ``ctrl+a``
- ``ctrl+b``
- ``ctrl+c``
- ``ctrl+d``
- ``ctrl+e``
- ``ctrl+f``
- ``ctrl+g``
- ``ctrl+h``
- ``ctrl+k``
- ``ctrl+l``
- ``ctrl+n``
- ``ctrl+o``
- ``ctrl+p``
- ``ctrl+q``
- ``ctrl+r``
- ``ctrl+s``
- ``ctrl+t``
- ``ctrl+u``
- ``ctrl+v``
- ``ctrl+w``
- ``ctrl+x``
- ``ctrl+y``
- ``ctrl+z``
- ``escape``
- ``ctrl+\\``
- ``ctrl+]``
- ``ctrl+^``
- ``ctrl+_``

Missing ``ctrl+`` combinations
------------------------------

- ``ctrl + i`` missing due to being same as ``tab``
- ``ctrl + j`` missing due to being same as ``enter``
- ``ctrl + m`` missing due to being same as ``enter``

Unknown
-------
Unknown keycodes will be represented as ``unknown``.

Alt
---
``alt+`` combinations are not supported.
