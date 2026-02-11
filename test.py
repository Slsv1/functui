from functui.io.raw import create_terminal_io, UnixTerminalIO, TerminalFeatures



io = create_terminal_io()

features = TerminalFeatures(
    bracketed_paste=False,
    mouse=False,
    alternate_screen=False,
)

io.run(callback=lambda x: print(x), features=features)
