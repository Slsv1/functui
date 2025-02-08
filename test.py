
def node(a, child):
    def set_size(dim: int):
        print(dim)
        child_render = child()
        def render():
            print("a")
            child_render()

