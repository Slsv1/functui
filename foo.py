# from functui.io import raw
# from prompt_toolkit.input.defaults import create_input
# from prompt_toolkit.output.defaults import create_output
# from time import sleep
# import sys
#
# i = create_input(sys.stdin)
# o = create_output(sys.stdout)
#
#
# o.enter_alternate_screen()
# o.enable_mouse_support()
# o.flush()
#
# with i.raw_mode():
#     for _ in range(10):
#         print(i.read_keys())
#         sleep(0.25)
#
# o.disable_mouse_support()
# o.quit_alternate_screen()
# o.flush()
# i.close()
#
# # io = raw.create_terminal_io()
# # io.run(callback=lambda x: print(x))
#
# # import sys, termios, tty
# #
# # fd = sys.stdin.fileno()
# # old = termios.tcgetattr(fd)
# #
# # def enable():
# #     sys.stdout.write("\x1b[?2004h\x1b[?1000h\x1b[?1006h")
# #     sys.stdout.flush()
# #
# # def disable():
# #     sys.stdout.write("\x1b[?2004l\x1b[?1000l\x1b[?1006l")
# #     sys.stdout.flush()
# #
# # try:
# #     tty.setraw(fd)
# #     enable()
# #
# #     while True:
# #         ch = sys.stdin.read(1)
# #         if ch == "\x03":  # Ctrl+C
# #             break
# #
# #         if ch != "\x1b":
# #             print("KEY:", repr(ch))
# #             continue
# #
# #         seq = ch
# #         while True:
# #             c = sys.stdin.read(1)
# #             seq += c
# #             if c.isalpha() or c in "~mM":
# #                 break
# #
# #         print("ESC:", repr(seq))
# #
# # finally:
# #     disable()
# #     termios.tcsetattr(fd, termios.TCSADRAIN, old)
#
# # tips:
#
