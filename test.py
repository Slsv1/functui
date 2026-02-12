from functui.io.raw import create_terminal_io, UnixTerminalIO, TerminalFeatures



io = create_terminal_io()

features = TerminalFeatures(
    bracketed_paste=True,
    mouse=True,
    alternate_screen=True,
    line_wrap=True,
)

io.run(callback=lambda x: print(f"{x.key_event} {repr(x.mouse_position_event)}"), features=features)
