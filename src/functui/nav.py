"""Tools to make layouts responsive to keyboard and mouse input"""
from enum import Enum, auto
from typing import Hashable, Self, Literal, Iterable, Any, NamedTuple, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from functools import partial, reduce
from .classes import *
from .common import fg, vbox, offset, vbar, static_box, text, border, bg_char, shrink
from time import sleep

__all__ = [
    "NavAction",
    "KeyboardNavAction",
    "ScrollAction",

    "Direction",

    "NavState",

    "vnav",
    "hnav",
    "DEFAULT_NAV_BINDINGS",

    # nodes
    "hoverable",
    "v_scroll",
    "v_resizable_split"
]

class NavAction(Enum):
    """An action that is meant to be sent to :obj:`NavData.update`.

    Attributes:
        SELECT_VIA_KEYBOARD:
        SELECT_VIA_MOUSE_START:
            For example, if user presses down left click.
        SELECT_VIA_MOUSE_END:
            For example, if user releases left click.
        PAGE_DOWN:
        PAGE_UP:
        SCROLL_UP:
        SCROLL_DOWN:
        NAV_UP:
        NAV_RIGHT:
        NAV_DOWN:
        NAV_LEFT:

    """
    SELECT_VIA_KEYBOARD = auto()
    SELECT_VIA_MOUSE_START = auto()
    SELECT_VIA_MOUSE_END = auto()
    PAGE_DOWN = auto()
    PAGE_UP = auto()
    SCROLL_UP = auto()
    SCROLL_DOWN = auto()
    NAV_UP = auto()
    NAV_RIGHT = auto()
    NAV_DOWN = auto()
    NAV_LEFT = auto()

class Direction(Enum):
    VERTICAL = auto()
    HORIZONTAL = auto()

type KeyboardNavAction = Literal[NavAction.NAV_DOWN, NavAction.NAV_UP, NavAction.NAV_LEFT, NavAction.NAV_RIGHT]
KEYBOARD_NAV_ACTION = [NavAction.NAV_DOWN, NavAction.NAV_UP, NavAction.NAV_LEFT, NavAction.NAV_RIGHT]

type ScrollAction = Literal[NavAction.PAGE_DOWN, NavAction.PAGE_UP, NavAction.SCROLL_DOWN, NavAction.SCROLL_UP]
SCROLL_ACTION = [NavAction.PAGE_DOWN, NavAction.PAGE_UP, NavAction.SCROLL_DOWN, NavAction.SCROLL_UP]



@dataclass
class NavContainer:
    direction: Direction 
    children: tuple[NodeId | NavContainer, ...]
    remember: bool
    container_id: NodeId | None


def vnav(*ids: NodeId | NavContainer, remember:bool=False, container_id:NodeId|None=None):
    return NavContainer(Direction.VERTICAL, tuple(ids), remember, container_id)

def hnav(*ids: NodeId | NavContainer, remember:bool=False, container_id:NodeId|None=None):
    return NavContainer(Direction.HORIZONTAL, tuple(ids), remember, container_id)



def hoverable(node_id: NodeId):
    """A wrapper node that marks its child layout as interactive."""
    def _out(child: Layout):
        return Layout(
            func=hoverable,
            min_size=child.min_size,
            render=partial(_render_interaction_area, node_id, child)
        )
    return _out


def _render_interaction_area(
    node_id: NodeId,
    child: Layout,
    frame: Frame,
    box: Box
) -> Result:
    res = Result()
    res.set_box_data(node_id, box, frame.view_box)
    res.add_children_after([child.render(frame, box)])
    return res

def v_resizable_split(
    node_id: NodeId,
    nav: NavState,
    left: Layout,
    right: Layout,
    sep: Layout = vbar,
    sep_id: NodeId | None = None
):
    sep_id = sep_id if sep_id is not None else (node_id, "separator")

    sep_at = 10

    if nav.result_data is not None and sep_id in nav.result_data.box_data:
        sep_box = nav.result_data.box_data[sep_id].box 
        box = nav.result_data.box_data[node_id].box

        sep_at = nav._split_data.get(node_id, -1)

        # if no no previous sep set, then place it in the middle
        if sep_at == -1:
            sep_at = box.width//2 - sep_box.width//2

        if nav.is_held_down(sep_id):
            sep_at += nav.get_mouse_drag_difference().x

        sep_at = clamp(sep_at, 0, box.width-sep_box.width)
        nav._split_data[node_id] = sep_at


    return Layout(
        v_resizable_split,
        min_size_horizontal([left.min_size, right.min_size, sep.min_size]),
        partial(
            _v_resizable_split_render,
            left,
            right,
            sep | hoverable(sep_id),
            sep_at,
        )
    ) | hoverable(node_id)

def _v_resizable_split_render(
        left: Layout,
        right: Layout,
        sep: Layout,
        sep_at: int | None,
        frame: Frame,
        box: Box
) -> Result:
    sep_rect = sep.min_size(frame.measure_text, box.rect)

    sep_at = clamp(sep_at, 0, box.width-sep_rect.width)

    left_box = Box(
        sep_at,
        box.height,
        box.position,
    )
    right_box = Box(
        box.width-sep_at-sep_rect.width,
        box.height,
        box.position + Coordinate(sep_at + sep_rect.width, 0)
    )
    split_box = Box(
        sep_rect.width,
        box.height,
        box.position + Coordinate(sep_at, 0)
    )

    res = Result()

    res.add_children_after([
        left.render(frame.shrink_to(left_box), left_box),
        sep.render(frame.shrink_to(split_box), split_box),
        right.render(frame.shrink_to(right_box), right_box),
    ])
    return res


def v_scroll(
    container_id: NodeId,
    nav: NavState,
    children: Sequence[NodeId],
    scroll_ovveride: Iterable[NodeId] = (),
    scrolling_speed:int=1,
):
    """Allow vertical scrolling if child does not fit into available space."""

    def _v_scroll(child: Layout):
        at_y = nav._scrolling_data.get(container_id, None)

        if at_y is None:
            at_y = 0

        a = []
        if nav.result_data is not None and container_id in nav.result_data.box_data:
            last_box_data = nav.result_data.box_data[container_id]

            if nav._keyboard_nav.active is not None\
                and (active_box := nav.result_data.box_data.get(nav._keyboard_nav.active.id, None)) is not None\
                and nav.action in KEYBOARD_NAV_ACTION\
                and nav._keyboard_nav.active.id in children: 

                selected_at_y = active_box.box.position.y - last_box_data.box.position.y # to local space
                start = 0 # including
                end = last_box_data.box.height # excluding
                if nav.action == NavAction.NAV_UP:
                    # aproach form below

                    if not (start <= selected_at_y < end):
                        at_y += (selected_at_y)
                else:

                    # aproach from above
                    if not (start <= (selected_at_y + active_box.box.height) < end):
                        at_y += (selected_at_y - last_box_data.box.height + active_box.box.height)
            else:
                # make sure scrolling does nothing when child gets scrolled
                child_interaction = False
                for c in scroll_ovveride:
                    if (child_box_data := nav.result_data.box_data.get(c, None)) is not None:
                        child_interaction = child_box_data.visible_box.is_overlaping(last_box_data.visible_box) and child_box_data.visible_box.is_point_inside(nav.mouse_position)
                        if child_interaction: break
                if last_box_data.view_box.is_point_inside(nav.mouse_position) and not child_interaction:
                    at_y += nav.get_scrolling_difference() * scrolling_speed

            at_y = clamp(at_y,
                0,
                child.min_size(nav.result_data.measure_text, Rect(last_box_data.box.width, 9999)).height - last_box_data.visible_box.height
            )

        nav._scrolling_data[container_id] = at_y

        return Layout(
            func=v_scroll,
            min_size=child.min_size,
            render=partial(
                _v_scroll_render,
                at_y,
                container_id,
                child,
            )
        )
    return _v_scroll

def _v_scroll_render(
    at_y: int,
    container_id: NodeId,
    child: Layout,
    frame: Frame, 
    box: Box
):
    # move to selected if selected out of bounds

    # if active_box is not None:


    res = Result()
    res.set_box_data(container_id, box, frame.view_box)
    # a.append(text("final:" + str(scroll_dy)))

    modified_child = vbox([child], at_y=-at_y)
    res.add_children_after([modified_child.render(frame, box)])
    return res


@dataclass
class KeyboardNav:
    active: _ActiveData | None = None
    _remembered_data: dict[tuple[int, ...], int] = field(default_factory=dict)

    class _ActiveData(NamedTuple):
        id: NodeId
        tree_index: tuple[int, ...]

    @staticmethod
    def _find_default_active(tree: NavContainer, index: tuple[int, ...] = ()) -> _ActiveData | None:
        for i, child in enumerate(tree.children):
            if isinstance(child, NavContainer):
                return KeyboardNav._find_default_active(child, index + (i,))
            return KeyboardNav._ActiveData(child, index + (i,))
        return None

    @staticmethod
    def _find_nearest_active(container: NavContainer, index: tuple[int, ...], depth=0) -> _ActiveData:
        if (index[depth]) > len(container.children):
            temp_index = list(index)
            temp_index[depth] = (len(container.children) -1)
            index = tuple(temp_index)

        child = container.children[index[depth]]
        if not isinstance(child, NavContainer):
            return KeyboardNav._ActiveData(child, index[:(depth+1)])

        if depth == len(index):
            active_for_child = KeyboardNav._find_default_active(child)
            if active_for_child is None:
                raise Exception("what")

            return KeyboardNav._ActiveData(active_for_child.id, index + active_for_child.tree_index)

        return KeyboardNav._find_nearest_active(child, index, depth+1)

    def update(
            self,
            tree: NavContainer,
            action: KeyboardNavAction,
    ) -> Self:

        # if no keyboardnav was happening before, try find default
        if self.active is None:
            self.active = KeyboardNav._find_default_active(tree)
            return self

        # deside direction and backwards
        direction = Direction.HORIZONTAL if action in (NavAction.NAV_RIGHT, NavAction.NAV_LEFT) else Direction.VERTICAL
        backwards = False
        if direction == Direction.HORIZONTAL:
            backwards = True if action == NavAction.NAV_LEFT else False
        elif direction == Direction.VERTICAL:
            backwards = True if action == NavAction.NAV_UP else False


        old_active_data = KeyboardNav._find_nearest_active(
            tree,
            self.active.tree_index,
        )

        # helper
        def _find_container(tree:NavContainer, index: Sequence[int]) -> NavContainer:
            return reduce(lambda acc, index: acc.children[index] if isinstance(acc, NavContainer) else acc, index, tree) # type: ignore

        stack = list(old_active_data.tree_index)
        has_incemented = False

        # breakpoint()

        while True:
            container = _find_container(tree, stack[:-1])
            child_index = stack[-1]
            child = container.children[child_index]

            # go into child container
            # (push container)
            if isinstance(child, NavContainer):
                new_child = self._remembered_data.get(tuple(stack), 0)
                if new_child >= len(child.children):
                    new_child = len(child.children) -1
                    del self._remembered_data[tuple(stack)]
                stack.append(new_child)
                continue

            if has_incemented:
                if container.remember:
                    self._remembered_data[tuple(stack[:-1])] = child_index
                self.active =  KeyboardNav._ActiveData(child, tuple(stack))
                return self


            # if current container is wrong direction OR at end of container
            # (pop containers)
            while (container.direction != direction) or (child_index == 0 if backwards else len(container.children) == (child_index+1)):
                if len(stack) == 1:
                    return self # don't navigate
                stack.pop()

                container = _find_container(tree, stack[:-1])

                child_index = stack[-1]
                child = container.children[child_index]



            # increment
            stack[-1] = stack[-1] + (-1 if backwards else 1)
            has_incemented = True


@dataclass
class NavState:

    # context reset with every update

    """A data structure storing and managing keyboard navigation and mouse data."""
    mouse_position: Coordinate = Coordinate(-1, -1)
    last_mouse_position: Coordinate = Coordinate(-1, -1)

    action: NavAction | None = None
    last_action: NavAction | None = None

    result_data: ResultData | None = None
    _currently_hovered: tuple[NodeId, ...] = ()


    # state keps between updates

    _held_down: tuple[NodeId, ...] = ()
    _scrolling_data: dict[NodeId, int] = field(default_factory=dict)
    _split_data: dict[NodeId, int] = field(default_factory=dict)

    # keyboard nav data
    
    _keyboard_nav: KeyboardNav = field(default_factory=lambda: KeyboardNav())


    def is_active(self, key: NodeId) -> bool:
        if self._keyboard_nav.active is None:
            return False
        return key == self._keyboard_nav.active.id

    def is_hovered(self, key: NodeId) -> bool:
        return key in self._currently_hovered

    def is_selected(self, key: NodeId) -> bool:
        """Whether an interactible was selected by keyboard or mouse.

        This condition if often triggered by pressing enter while an
        interactible is active through keyboard navigation, or by releasing left click on an interactible with a mouse.

        More specifically, this returns whether an interactible is active and
        :obj:`~NavAction.SELECT_VIA_KEYBOARD` was triggered OR an interactible
        is hovered and :obj:`~NavAction.SELECT_VIA_MOUSE_END` was triggered
        """
        return \
            (self.is_hovered(key) and self.action == NavAction.SELECT_VIA_MOUSE_END)\
            or (self.is_active(key) and self.action == NavAction.SELECT_VIA_KEYBOARD)

    def is_held_down(self, key: NodeId) -> bool:
        return key in self._held_down

    def get_scrolling_difference(self):
        if self.action == NavAction.SCROLL_UP:
            return -1
        if self.action == NavAction.SCROLL_DOWN:
            return 1
        return 0

    def get_mouse_drag_difference(self) -> Coordinate:
        return self.mouse_position - self.last_mouse_position


    def update(
            self,
            res: ResultData | None = None,
            action: NavAction | None = None,
            nav_tree: NavContainer | None = None,
            mouse_position: Coordinate | None = Coordinate(-1, -1),
    ):
        if nav_tree is not None and action in KEYBOARD_NAV_ACTION:
            self._keyboard_nav.update(nav_tree, action) # type: ignore
        elif action == NavAction.SELECT_VIA_MOUSE_START:
            self._keyboard_nav.active = None

        # hovered
        if res is not None and mouse_position is not None:
            hovered = []
            for (node_id, box_data) in res.box_data.items():
                if box_data.visible_box.is_point_inside(mouse_position):
                    hovered.append(node_id)

            self._currently_hovered = tuple(hovered)
        else:
            self._currently_hovered = tuple()

        # held down
        if action == NavAction.SELECT_VIA_MOUSE_START:
            self._held_down = self._currently_hovered
        elif action == NavAction.SELECT_VIA_MOUSE_END:
            self._held_down = tuple()

        self.action = action
        self.last_mouse_position = self.mouse_position
        self.mouse_position = mouse_position if mouse_position is not None else self.mouse_position
        self.result_data = res



        return self


DEFAULT_NAV_BINDINGS = {
    "h": NavAction.NAV_LEFT,
    "left": NavAction.NAV_LEFT,
    "j": NavAction.NAV_DOWN,
    "down": NavAction.NAV_DOWN,
    "k": NavAction.NAV_UP,
    "up": NavAction.NAV_UP,
    "l": NavAction.NAV_RIGHT,
    "right": NavAction.NAV_RIGHT,

    "enter": NavAction.SELECT_VIA_KEYBOARD,
    " ": NavAction.SELECT_VIA_KEYBOARD,
    "left mouse": NavAction.SELECT_VIA_MOUSE_START,
    "left mouse released": NavAction.SELECT_VIA_MOUSE_END,

    "page up": NavAction.PAGE_UP,
    "ctrl+u": NavAction.PAGE_UP,
    "page down": NavAction.PAGE_DOWN,
    "ctrl+d": NavAction.PAGE_DOWN,

    "mouse wheel down": NavAction.SCROLL_DOWN,
    "mouse wheel up": NavAction.SCROLL_UP
}
"""A dictinary that maps the string representation of keycodes to a :obj:`NavAction`"""
