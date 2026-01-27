from dataclasses import dataclass
from functools import lru_cache, partial
from typing import runtime_checkable, Callable, Iterable
from .classes import *

@dataclass(frozen=True, eq=True)
class Flex:
    """Extra data to mark layouts as flexible for flex containers

    Note:
        You are highly unlikely to use this class directly. Consider using :obj:`flex` or :obj:`flex_custom`.
    """
    node: Layout
    grow: int
    shrink: int
    basis: bool

def flex_custom(grow=1, shrink=1, basis=False) -> Callable[[Layout], Flex]:
    """Wrap child layout in a :obj:`Flex` class to mark it as flexible and adjust attributes.

    Note:
        This node is only userful with flex containers (:obj:`vbox_flex` and :obj:`hbox_flex`).

    Args:
        grow: 
            How much unused space will be given to this layout relative to other layouts.
        shrink:
            How much to shrink this layout relative to other layouts if it cant fit the container.
            This property has an effect only when ``basis`` is set to ``True``.
        basis:
            If parent container should reserve space for this layout's minum size.
    """

    def out(node: Layout):
        return Flex(node, grow, shrink, basis)
    return out

def flex(node: Layout) -> Flex:
    """Wrap layout in a :obj:`Flex` class to mark it as flexible.

    Note:
        This node is only usefull with flex containers (:obj:`vbox_flex` and :obj:`hbox_flex`).
    """
    return flex_custom(1, 1, False)(node)


def vbox_flex(children: Iterable[Flex | Layout]) -> Layout:
    """A container node that allows children to expand on the y axis.

    Modeled of the CSS flexbox layout model. By default acts as a regular :obj:`~functui.common.vbox`.
    If a child with the :obj:`flex` node as a parent is added, its height will be equal to the unused space on the y axis.
    If multiple childred with the :obj:`flex` node are added, the remaing space will be devided equaly among them.
    To destribute remaing space unevanly, childrens ``grow`` attribute can be changed by using :obj:`flex_custom`.

    """
    children = tuple(child if isinstance(child, Flex) else flex_custom(0, 0, True)(child) for child in children)
    return Layout(
        func=vbox_flex,
        min_size=min_size_vertical([i.node.min_size for i in children]),
        render=partial(_vbox_flex_render, children)
    )


@lru_cache(LRU_MAX_SIZE)
def _vbox_flex_render(children: tuple[Flex, ...], frame: Frame, box: Box):
    reserved_space = sum(i.node.min_size(frame.measure_text, box.rect).height for i in children if i.basis)
    total_grow = sum(i.grow for i in children)
    total_shrink = sum(i.shrink for i in children)

    available_space = box.height - reserved_space
    space_rations = even_divide(available_space, total_grow if available_space >= 0 else total_shrink)
    at_y = 0
    res = Result()
    for flex in children:
        child_min_height = flex.node.min_size(frame.measure_text, box.rect).height if flex.basis else 0
        child_box = Box(
            width=box.width,
            height=child_min_height + sum(space_rations.pop() for _ in range(flex.grow if available_space >= 0 else flex.shrink))
        )
        child_box = child_box.offset_by(box.position + Coordinate(0, at_y))
        res.add_children_after([flex.node.render(frame.shrink_to(child_box), child_box)])
        at_y += child_box.height
    return res


def hbox_flex(processed_children: Iterable[Flex | Layout]):
    """A container node that allows children to expand on the x axis.

    Modeled of the CSS flexbox layout model. By default acts as a regular :obj:`~functui.common.xbox`.
    If a child with the :obj:`flex` node as a parent is added, its width will be equal to the unused space on the x axis.
    If multiple childred with the :obj:`flex` node are added, the remaing space will be devided equaly among them.
    To destribute remaing space unevanly, childrens ``grow`` attribute can be changed by using :obj:`flex_custom`.

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
    processed_children = tuple(child if isinstance(child, Flex) else flex_custom(0, 0, True)(child) for child in processed_children)
    return Layout(
        func=hbox_flex,
        min_size=min_size_horizontal([i.node.min_size for i in processed_children]),
        render=partial(_hbox_flex_render, processed_children)
    )
@lru_cache(LRU_MAX_SIZE)
def _hbox_flex_render(children: Iterable[Flex], frame: Frame, box: Box):
    reserved_space = sum(i.node.min_size(frame.measure_text, box.rect).width for i in children if i.basis)
    total_grow = sum(i.grow for i in children)
    total_shrink = sum(i.shrink for i in children)

    available_space = box.width - reserved_space
    space_rations = even_divide(available_space, total_grow if available_space >= 0 else total_shrink)
    at_x = 0
    res = Result()
    for flex in children:
        child_min_width = flex.node.min_size(frame.measure_text, box.rect).width if flex.basis else 0
        child_box = Box(
            width=child_min_width + sum(space_rations.pop() for _ in range(flex.grow if available_space >= 0 else flex.shrink)),
            height=box.height,
        )
        child_box = child_box.offset_by(box.position + Coordinate(at_x, 0))
        res.add_children_after([flex.node.render(frame.shrink_to(child_box), child_box)])
        at_x += child_box.width
    return res

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

        child_min_width, child_min_height = flex.node.min_size(measure_text, Rect(available_space, 9999))

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

def hbox_flex_wrap(children: Iterable[Flex | Layout]) -> Layout:
    """A container node that allows children to expand on the y axis.

    Modeled of the CSS flexbox layout model. By default acts as a regular :obj:`~functui.common.vbox`.
    If a child with the :obj:`flex` node as a parent is added, its height will be equal to the unused space on the y axis.
    If multiple childred with the :obj:`flex` node are added, the remaing space will be devided equaly among them.
    To destribute remaing space unevanly, childrens ``grow`` attribute can be changed by using :obj:`flex_custom`.

    """
    children = tuple(child if isinstance(child, Flex) else flex_custom(0, 0, True)(child) for child in children)
    def min_size(measure_text: MeasureTextFunc, from_rect: Rect):
        lines = _split_flex_by_lines_h(from_rect.width, children, measure_text)

        return Rect(
            width=max(i.bounding_rect.width for i in lines),
            height=sum(i.bounding_rect.height for i in lines),
        )
    return Layout(
        func=hbox_flex_wrap,
        min_size=min_size,
        render=partial(_hbox_flex_wrap_render, children)
    )

@lru_cache(LRU_MAX_SIZE)
def _hbox_flex_wrap_render(children: Iterable[Flex], frame: Frame, box: Box):
    #
    # split by 'lines'
    #
    children_by_lines = _split_flex_by_lines_h(box.width, children, frame.measure_text)

    at_y = 0
    res = Result()

    for data in children_by_lines:
        children = data.flex_children
        available_width = box.width - data.bounding_rect.width
        row_height = data.bounding_rect.height

        total_grow = sum(i.grow for i in children)
        total_shrink = sum(i.shrink for i in children)

        space_rations = even_divide(available_width, total_grow if available_width >= 0 else total_shrink)
        at_x = 0
        for flex in children:
            child_min_width, child_min_height = flex.node.min_size(frame.measure_text, box.rect) if flex.basis else Rect(0, 0)
            child_box = Box(
                width=child_min_width + sum(space_rations.pop() for _ in range(flex.grow if available_width >= 0 else flex.shrink)),
                height=row_height,
            )
            child_box = child_box.offset_by(box.position + Coordinate(at_x, at_y))
            res.add_children_after([flex.node.render(frame.shrink_to(child_box.intersect(box)), child_box)])
            at_x += child_box.width
        at_y += row_height
    return res
