import curses
from functui.io.curses import get_input_event, wrapper


def main(stdscr:curses.window):
    while True:
        key, mouse_button, pos = get_input_event(stdscr)  # Get a single key press
        print(key, mouse_button)

        if key == 'ctrl+c':
            break

wrapper(main)

