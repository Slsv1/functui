import curses
from functui.io.curses import get_input_event


def main(stdscr:curses.window):
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION) # enable reporting of all mouse events
    curses.mouseinterval(0)
    print('\033[?1003h') # xterm enable reporting of all mouse events
    while True:
        key, mouse_button, pos = get_input_event(stdscr)  # Get a single key press
        print(key, mouse_button)

        if key == 'q':
            break
        if key == curses.KEY_MOUSE:
            try:
                _, x, y, _, state = curses.getmouse()
                print(x, y)
                # stdscr.addstr(2, 0, f"Mouse at x={x}, y={y}      ")
                # stdscr.refresh()
            except curses.error:
                pass
        print()

curses.wrapper(main)

