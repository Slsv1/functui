from .classes import *
from dataclasses import dataclass
from typing import Callable
from itertools import chain

BIG_INT = 2 ** 16
@dataclass
class GridItem:
    box: Box
    borders: tuple
    node: Layout


GetSize = Callable[[MeasureTextFunc, Rect, tuple[GridItem, ...]], tuple[int, ...]]

def min_size_x(
    measure_text: MeasureTextFunc,
    available: Rect,
    children: tuple[GridItem, ...]
):
    return tuple(
        child.node.min_size(measure_text, Rect(BIG_INT, BIG_INT)).width for child in children
    )

def constant(
    *values: int
):
    return lambda m, a, c: values

def compose(
    *functions: GetSize
):
    return lambda m, a, c: tuple(chain.from_iterable(f(m, a, c) for f in functions))


# def grid(
#     collumns: GetSize,
#     rows: GetSize,
#     items: tuple[GridItem, ...],
# ) -> Node:
#     return Node(
#         func=grid,
#         min_size=lambda available, measure_text: Rect(
#             sum(collumns(available, measure_text, items)),
#             sum(rows(available, measure_text, items)),
#         ),
#         render=partial(_grid_render)
#     )
# def _min_size(available: Rect):
#     ...
#
#
# def _grid_render(collumns: tuple[int, ...], rows: tuple, frame: Frame, box: Box):
#     ...
#
# grid(
#     collumns=compose(min_size_x, )
# )
