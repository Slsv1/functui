from dataclasses import dataclass
from functools import lru_cache, partial
from typing import Callable, Iterable
from ._classes import *


@dataclass(frozen=True, eq=True)
class Flex:
    """Extra data to mark layouts as flexible for flex containers

    Note:
        You are highly unlikely to use this class directly. Consider using :obj:`flex` or :obj:`flex_custom`.
    """
    node: Layout
    grow: int
    shrink: bool
    basis: bool

def flex_custom(grow=1, shrink=True, basis=False) -> Callable[[Layout], Flex]:
    """Wrap child layout in a :obj:`Flex` class to mark it as flexible and adjust attributes.

    Note:
        This node is only useful with flex containers (:obj:`vbox_flex` and :obj:`hbox_flex`).

    Args:
        grow: 
            If there is any leftover space, this value is used to determine how
            much of this space does this child get relative to other children.
        shrink:
            Should this child shrink if container does not fit into the
            available space? This property has an effect only when ``basis`` is
            set to ``True``.
        basis:
            If true, container will take this children's minimum size into account.
            If false, container will assume minimum size of 0.
    """

    def out(node: Layout):
        return Flex(node, grow, shrink, basis)
    return out

def flex(node: Layout) -> Flex:
    """Wrap layout in a :obj:`Flex` class to mark it as flexible.

    Equivalent to :obj:`flex_custom` ``(grow=1 shrink=True, basis=False)``.

    Note:
        This node is only useful with flex containers (:obj:`vbox_flex` and :obj:`hbox_flex`).
    """
    return flex_custom(1, True, False)(node)


def _calculate_flex_children_sizes(
    available_space: int,
    children: Iterable[Flex],
    child_basis: Iterable[int],
) -> Iterable[int]:

    leftover_space = available_space - sum(child_basis)
    child_data = list(zip(child_basis, children))

    if leftover_space < 0: # shrink
        # missing_space = -1 * leftover_space
        fixed_space = sum(basis for (basis, child) in child_data if child.shrink == 0)
        flexible_space = available_space - fixed_space

        children_that_will_shrink = [i for i in child_data if i[1].shrink]

        # shrink_factor equation explanation

        # a -> flexible_space
        # k -> shrink factor
        # bₙ -> basis size of shrinkable child n

        # after elements have ben shrunk by factor k,
        # the below eqation should be true.
        # a = b₁k + ... + bₙk 
        # <=> a = k(b₁ + ... + bₙ)
        # <=> k = a/(b₁ + ... + bₙ)

        basis_sum = sum(
            basis for (basis, child) in children_that_will_shrink
        )

        if basis_sum == 0:
            return child_basis

        shrink_factor = flexible_space / basis_sum
        shrunk_children = []
        calculated_flexible_space = 0
        for (basis, child) in children_that_will_shrink:
            child_size = round(basis * shrink_factor)
            calculated_flexible_space += child_size
            shrunk_children.append(child_size)

        # because child sizes are actually floats that have been rounded to ints
        # there may be a rounding error that needs to be handled
        rounding_error = flexible_space - calculated_flexible_space

        if rounding_error:
            rounding_rations = even_divide(rounding_error, len(shrunk_children))
            shrunk_children = [a + b for (a, b) in zip(shrunk_children, rounding_rations)]

        shrunk_children = list(reversed(shrunk_children)) # so that pop is in order
        out = []
        for basis, child in child_data:
            if child.shrink == 0:
                out.append(basis)
            else:
                out.append(shrunk_children.pop())

        return out

    # grow
    total_grow = sum(i.grow for i in children)
    space_rations = even_divide(leftover_space, total_grow)
    out = []
    for (basis, child) in child_data:
        out.append(basis + sum(space_rations.pop() for _ in range(child.grow)))
    return out


def vbox_flex(children: Iterable[Flex | Layout]) -> Layout:
    """A container node that allows children to expand on the y axis.

    Modeled of the CSS flexbox layout model. By default acts as a regular
    :obj:`~functui.common.vbox`. Wrap children in :func:`flex` or
    :func:`flex_custom` wrapper nodes to allow them to use leftover space if
    there is any.

    """
    children = tuple(child if isinstance(child, Flex) else flex_custom(0, False, True)(child) for child in children)

    def _min_size(measure_text: MeasureTextFunc, from_size: Rect):
        child_basis = [(i.node.min_size(measure_text, from_size).height if
                i.basis else 0) for i in children]
        child_heights = _calculate_flex_children_sizes(from_size.height, children, child_basis)

        child_widths = []
        for (height, child) in zip(child_heights, children):
            rect = child.node.min_size(
                measure_text,
                Rect(from_size.width, height)
            )
            child_widths.append(rect.width)
        return Rect(max(child_widths), sum(child_heights))

    return Layout(
        func=vbox_flex,
        min_size=_min_size,
        render=partial(_vbox_flex_render, children)
    )


def _vbox_flex_render(children: tuple[Flex, ...], frame: Frame, box: Box):
    child_basis = [(i.node.min_size(frame.measure_text, box.rect).height if
            i.basis else 0) for i in children]
    child_heights = _calculate_flex_children_sizes(box.height, children, child_basis)

    at_y = 0
    for child, child_height in zip(children, child_heights):
        child_box = Box(box.width, child_height, box.position + Coordinate(0, at_y))
        at_y += child_box.height

        child.node.render(frame.shrink_to(child_box), child_box)


def hbox_flex(children: Iterable[Flex | Layout], /):
    """A container node that allows children to expand on the x axis.

    Modeled of the CSS flexbox layout model. By default acts as a regular
    :obj:`~functui.common.hbox`. Wrap children in :func:`flex` or
    :func:`flex_custom` wrapper nodes to allow them to use leftover space if
    there is any.

    Examples:
        Usage with flex:
            >>> from functui import Rect, layout_to_str
            >>> from functui.common import border, text
            >>> from functui.flex import flex, hbox_flex, flex_custom
            >>> layout = hbox_flex([
            ...     text("Flex.") | border | flex,
            ...     text("No flex.") | border,
            ... ]) | border
            >>> print(layout_to_str(layout, Rect(40, 5)))
            ┌──────────────────────────────────────┐
            │┌──────────────────────────┐┌────────┐│
            ││Flex.                     ││No flex.││
            │└──────────────────────────┘└────────┘│
            └──────────────────────────────────────┘

        Usage with flex_custom grow argument:
            >>> layout = hbox_flex([
            ...     text("grow 1") | border | flex_custom(grow=1),
            ...     text("grow 2") | border | flex_custom(grow=2),
            ...     text("grow 1") | border | flex, # flex same as flex_custom(1)
            ... ]) | border
            >>> print(layout_to_str(layout, Rect(40, 5)))
            ┌──────────────────────────────────────┐
            │┌───────┐┌─────────────────┐┌────────┐│
            ││grow 1 ││grow 2           ││grow 1  ││
            │└───────┘└─────────────────┘└────────┘│
            └──────────────────────────────────────┘

        Usage with flex_custom grow and basis arguments:
            >>> layout = hbox_flex([
            ...     text("basis and grow") | border | flex_custom(grow=1, basis=True),
            ...     text("grow") | border | flex, # flex is same as flex_custom(grow=1)
            ... ]) | border
            >>> print(layout_to_str(layout, Rect(40, 5)))
            ┌──────────────────────────────────────┐
            │┌─────────────────────────┐┌─────────┐│
            ││basis and grow           ││grow     ││
            │└─────────────────────────┘└─────────┘│
            └──────────────────────────────────────┘

    """
    children = tuple(child if isinstance(child, Flex) else flex_custom(0, False, True)(child) for child in children)

    def _min_size(measure_text: MeasureTextFunc, from_size: Rect):
        child_basis = [(i.node.min_size(measure_text, from_size).width if
                i.basis else 0) for i in children]
        child_widths = _calculate_flex_children_sizes(from_size.width, children, child_basis)

        child_heights = []
        for (width, child) in zip(child_widths, children):
            rect = child.node.min_size(
                measure_text,
                Rect(width, from_size.height)
            )
            child_heights.append(rect.height)
        return Rect(sum(child_widths), max(child_heights))


    return Layout(
        func=hbox_flex,
        min_size=_min_size,
        render=partial(_hbox_flex_render, children)
    )

def _hbox_flex_render(children: Iterable[Flex], frame: Frame, box: Box):
    child_basis = [(i.node.min_size(frame.measure_text, box.rect).width if
            i.basis else 0) for i in children]
    child_widths = _calculate_flex_children_sizes(box.width, children, child_basis)

    at_x = 0
    for child, child_width in zip(children, child_widths):
        child_box = Box(child_width, box.height, box.position + Coordinate(at_x, 0))
        at_x += child_box.width

        child.node.render(frame.shrink_to(child_box), child_box)



@dataclass
class _FlexData:
    bounding_rect: Rect
    flex_children: list[Flex]

def _split_flex_by_lines_h(available_space: int, children: Iterable[Flex], measure_text: MeasureTextFunc):

    flex_by_lines = [_FlexData(Rect(0, 0), [])]


    for flex in children:
        current_flex_data = flex_by_lines[-1]

        if not flex.basis:
            current_flex_data.flex_children.append(flex)
            continue

        child_min_width, child_min_height = flex.node.min_size(
            measure_text, Rect(available_space, 999999))

        if current_flex_data.bounding_rect.width + child_min_width > available_space:
            flex_by_lines.append(_FlexData(
                Rect(child_min_width, child_min_height),
                [flex])
            )
        else:
            current_flex_data.bounding_rect = Rect(
                current_flex_data.bounding_rect.width + child_min_width,
                max(current_flex_data.bounding_rect.height, child_min_height)
            )
            current_flex_data.flex_children.append(flex)
    return flex_by_lines

def hbox_wrap(children: Iterable[Flex | Layout]) -> Layout:
    """A container node that allows children to wrap vertically.

    Modeled of the CSS flexbox layout model. If all children can't fit into the
    available horizontal space, wrap them. Wrap children in :func:`flex` or
    :func:`flex_custom` wrapper nodes to allow them to use leftover space if
    there is any.

    """
    children = tuple(child if isinstance(child, Flex) else flex_custom(0, False, True)(child) for child in children)
    def min_size(measure_text: MeasureTextFunc, from_rect: Rect):
        lines = _split_flex_by_lines_h(from_rect.width, children, measure_text)

        return Rect(
            width=max(i.bounding_rect.width for i in lines),
            height=sum(i.bounding_rect.height for i in lines),
        )
    return Layout(
        func=hbox_wrap,
        min_size=min_size,
        render=partial(_hbox_wrap_render, children)
    )


def _hbox_wrap_render(children: Iterable[Flex], frame: Frame, box: Box):
    #
    # split by 'lines'
    #
    children_by_lines = _split_flex_by_lines_h(box.width, children, frame.measure_text)

    at_y = 0

    for data in children_by_lines:
        row_rect = Rect(box.width, data.bounding_rect.height)
        row_box = Box.from_rect(row_rect, box.position + Coordinate(0, at_y))
        _hbox_flex_render(
            tuple(data.flex_children),
            frame.shrink_to(row_box),
            row_box
        )
        at_y += data.bounding_rect.height
