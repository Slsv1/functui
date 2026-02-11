from functui.io.raw import create_terminal_io, UnixTerminalIO, TerminalFeatures



io = create_terminal_io()

features = TerminalFeatures(
    bracketed_paste=True,
    mouse=True,
    alternate_screen=True,
)

io.run(callback=lambda x: print(f"{x.type.name}{repr(x.data)}"), features=features)
