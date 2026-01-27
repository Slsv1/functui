IO
==

Functui has multiple ways of doing input and output.

.. list-table::
  :width: 100 %
  :widths: 1 2 2 3 3
  :header-rows: 1
  :stub-columns: 1

  * - IO type

    - Input

    - Output

    - Pros
    
    - Cons (and quirks)

  * - ANSI

    - No, but possible to handle it yourself.

    - Yes, through :obj:`~functui.io.ansi.result_to_str`

    - Uses ANSI escape codes to render, which virtually all terminals support. True color is supported.

    - Is not very performant right now

  * - Curses

    - Yes, through :obj:`~functui.io.curses.get_input_event`

    - Yes, through :obj:`~functui.io.curses.draw_result`

    - A standard for tuis. Depends on python stdlib curses module (no extra dependencies).

    - No Truecolor support (only 8 bit color). Strikethrough style attribute not supported. Python does not have curses in its stdlib on windows.

  * - HTML

    - No

    - Yes, through :obj:`~functui.io.html.result_to_html_str`

    - Usefull to create html for tui like visuals on the web

    - Dim style attribute is rendered





