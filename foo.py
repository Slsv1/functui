from functui.classes import *
from functui.common import *
from functui.common import custom_border, _border_render
from functools import lru_cache, partial
def b():
    def inner():
        return 1
    return inner

c = partial(b())

@lru_cache
def a(num, f):
    return f() + num
g = partial(a, 1)

g(c)
g(c)
print(a.cache_info())

# layout: Layout = text("hej") | border
# layout_to_result(Rect(10, 10), layout)
#
# # print(layout.func.__module__)
# # print(layout.func.__name__)
# # print(hash(layout))
#
# layout: Layout = text("hej") | border
# layout_to_result(Rect(10, 10), layout)
# print(_border_render.cache_info())

# print(layout.func.__module__)
# print(layout.func.__name__)
# print(hash(layout))




