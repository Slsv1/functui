"""Tools to make layouts responsive to keyboard and mouse input"""

from enum import Enum, auto
from typing import Hashable, Self, Literal, Iterable, Any, NamedTuple, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from functools import partial, reduce
from ._classes import *
from ._common import vbox, nothing, hoverable
from ._border import vbar
from time import sleep
import math


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
    children: tuple[NodeID | Self, ...]
    remember: bool
    container_id: NodeID | None


def vnav(*ids: NodeID | NavContainer, remember:bool=False, container_id:NodeID|None=None):
    return NavContainer(Direction.VERTICAL, tuple(ids), remember, container_id)

def hnav(*ids: NodeID | NavContainer, remember:bool=False, container_id:NodeID|None=None):
    return NavContainer(Direction.HORIZONTAL, tuple(ids), remember, container_id)



def _vsplit_render(
        left: Layout,
        right: Layout,
        sep: Layout,
        sep_at: int | None,
        frame: Frame,
        box: Box
):
    sep_rect = sep.min_size(frame.measure_text, box.rect)

    if sep_at is None:
        sep_at = box.width//2 - sep_rect.width//2
    else:
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

    left.render(frame.shrink_to(left_box), left_box)
    sep.render(frame.shrink_to(split_box), split_box)
    right.render(frame.shrink_to(right_box), right_box)


@dataclass
class KeyboardNav:
    active: "_ActiveData | None" = None
    _remembered_data: dict[tuple[int, ...], int] = field(default_factory=dict)

    class _ActiveData(NamedTuple):
        id: NodeID
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

class _ScrollingData(NamedTuple):
    at_y: int
    max_at_y: int
    content_height: int

    @property
    def visible_height(self):
        return self.content_height - self.max_at_y


@dataclass
class NavState:

    # context reset with every update

    """A data structure storing and managing keyboard navigation and mouse data."""
    mouse_position: Coordinate = Coordinate(-1, -1)
    last_mouse_position: Coordinate = Coordinate(-1, -1)

    action: NavAction | None = None
    last_action: NavAction | None = None

    result_data: ResultData | None = None
    _currently_hovered: tuple[NodeID, ...] = ()


    # state keps between updates

    _held_down: tuple[NodeID, ...] = ()
    _scrolling_data: dict[NodeID, _ScrollingData] = field(default_factory=dict)
    _split_data: dict[NodeID, int] = field(default_factory=dict)

    # keyboard nav data
    
    _keyboard_nav: KeyboardNav = field(default_factory=lambda: KeyboardNav())


    def is_active(self, key: NodeID) -> bool:
        if self._keyboard_nav.active is None:
            return False
        return key == self._keyboard_nav.active.id

    def is_hovered(self, key: NodeID) -> bool:
        return key in self._currently_hovered

    def is_selected(self, key: NodeID) -> bool:
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

    def is_held_down(self, key: NodeID) -> bool:
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


    def vscrollable(
        self,
        container_id: NodeID,
        children: Sequence[NodeID] = (),
        scroll_ovveride: Iterable[NodeID] = (),
        scrolling_speed: int=1,
        scrollbar_id: NodeID | None = None,
    ):
        """Allow vertical scrolling if child does not fit into available space."""

        def _v_scroll(child: Layout):

            # if container's size is unknown then we cant do much
            if self.result_data is None or container_id not in self.result_data.box_data:
                data = self._scrolling_data.get(container_id, None)
                if data is None:
                    data = _ScrollingData(
                        at_y=0,
                        max_at_y=1,
                        content_height=1,
                    ) if data is None else data
                    self._scrolling_data[container_id] =  data

                return vbox([child], at_y=-data.at_y) | hoverable(container_id)

            data = self._scrolling_data[container_id] # here we can assume that container_id is in data thanks to to previous if check
            at_y = data.at_y
            s_id = (container_id, "scrollbar") if scrollbar_id is None else scrollbar_id

            container_box_data = self.result_data.box_data[container_id]

            content_height = child.min_size(self.result_data.measure_text, Rect(container_box_data.box.width, 9999)).height
            max_at_y = content_height - container_box_data.visible_box.height


            # change at_y based on keyboard navigation
            if self._keyboard_nav.active is not None\
                and self.action in KEYBOARD_NAV_ACTION\
                and self._keyboard_nav.active.id in children: 

                active_box = self.result_data.box_data.get(self._keyboard_nav.active.id, None)

                if active_box is None:
                    # move by fixed amount
                    move_by = container_box_data.box.height//2 + 1
                    at_y += (-move_by) if self.action == NavAction.NAV_UP else (move_by)
                else:
                    # move exactly to beggining of next

                    # offset from where scroll box starts
                    selected_at_y_offset = active_box.box.position.y - container_box_data.box.position.y 
                    start = 0 # including
                    end = container_box_data.box.height # excluding


                    if self.action == NavAction.NAV_UP:
                        # aproach form below
                        if not (start <= selected_at_y_offset < end):
                            at_y += (selected_at_y_offset)
                    else:

                        # aproach from above
                        if not (start <= (selected_at_y_offset + active_box.box.height) < end):
                            at_y += (selected_at_y_offset - container_box_data.box.height + active_box.box.height)

            # change at_y based on mouse navigation
            elif container_box_data.view_box.is_point_inside(self.mouse_position) and (scrolling_difference := self.get_scrolling_difference()) != 0:
                # make sure scrolling does nothing when child gets scrolled
                child_interaction = False
                for c in scroll_ovveride:
                    if (child_box_data := self.result_data.box_data.get(c, None)) is not None:
                        child_interaction = child_box_data.visible_box.is_overlaping(container_box_data.visible_box) and child_box_data.visible_box.is_point_inside(self.mouse_position)
                        if child_interaction: break
                if  not child_interaction:
                    at_y += scrolling_difference * scrolling_speed

            # change at_y by scrolling a scrollbar
            elif self.is_held_down(s_id):
                scrollbar_max_height = self.result_data.box_data[s_id].box.height
                dy_scroll_bar_space = self.get_mouse_drag_difference().y
                dy = dy_scroll_bar_space * (content_height / scrollbar_max_height)
                at_y += int(dy)


            # finalizing

            at_y = clamp(at_y, 0, max_at_y)
            self._scrolling_data[container_id] = _ScrollingData(at_y, max_at_y, content_height)

            return vbox([child], -at_y) | hoverable(container_id)
        return _v_scroll

    def vsplit(
        self,
        node_id: NodeID,
        left: Layout,
        right: Layout,
        sep: Layout = vbar,
        sep_id: NodeID | None = None
    ):
        sep_id = sep_id if sep_id is not None else (node_id, "separator")

        sep_at = None # if nonw, then assumed middle of box in the render function

        if self.result_data is not None and sep_id in self.result_data.box_data:
            sep_box = self.result_data.box_data[sep_id].box 
            box = self.result_data.box_data[node_id].box

            sep_at = self._split_data.get(node_id, None)

            # if no no previous sep set, then place it in the middle
            if sep_at == None:
                sep_at = box.width//2 - sep_box.width//2

            if self.is_held_down(sep_id):
                sep_at += self.get_mouse_drag_difference().x

            sep_at = clamp(sep_at, 0, box.width-sep_box.width)
            self._split_data[node_id] = sep_at


        return Layout(
            self.vsplit,
            min_size_horizontal([left.min_size, right.min_size, sep.min_size]),
            partial(
                _vsplit_render,
                left,
                right,
                sep | hoverable(sep_id),
                sep_at,
            )
        ) | hoverable(node_id)

    def vscroll_bar(
        self,
        container_id: NodeID,
        scrollbar_id: NodeID | None = None,
        hide_if_unnecessary: bool = False,
    ):
        scrollbar_id = (container_id, "scrollbar") if scrollbar_id is None else scrollbar_id

        if self.result_data is None:
            return nothing()
        if container_id not in self._scrolling_data:
            return nothing()

        # calculate data needed for visual

        scrolling_data = self._scrolling_data[container_id]

        if scrolling_data.content_height == 0:
            start_percent = 0
            visible_percent = 1.0
        else:
            start_percent = scrolling_data.at_y / scrolling_data.content_height
            visible_percent = scrolling_data.visible_height / scrolling_data.content_height


        if hide_if_unnecessary and visible_percent >= 1.0:
            return nothing()

        return Layout(
            func=self.vscroll_bar,
            min_size=min_size_constant(Rect(1, 1)),
            render=partial(_vscroll_bar_render, start_percent, visible_percent)

        ) | hoverable(scrollbar_id)


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

def parse_key_press(key_press: str):
    return DEFAULT_NAV_BINDINGS.get(key_press, None)


def _vscroll_bar_render(start: float, showing: float, frame: Frame, box: Box):
    start_at_pixel = box.height * start
    start_at_pixel_int = math.floor(start_at_pixel)
    start_at_progress = abs(start_at_pixel - start_at_pixel_int -1)

    end_at_pixel = box.height * start + box.height * showing # should be clampt
    end_at_pixel_int = math.floor(end_at_pixel)
    end_at_progress = end_at_pixel - end_at_pixel_int


    match [start_at_progress > 0.33, start_at_progress > 0.66]:
        case [True, True]:
            start_char = None
        case [True, False]:
            start_char = "╷"
        case _:
            start_char = "│"

    match [end_at_progress > 0.33, end_at_progress > 0.66]:
        case [True, True]:
            end_char = "│"
        case [True, False]:
            end_char = "╵"
        case _:
            end_char = None


    frame.draw_line_v("│", box.position.down(start_at_pixel_int), (end_at_pixel_int - start_at_pixel_int))
    if start_char:
        frame.draw_pixel(start_char, box.position.down(start_at_pixel_int))
    if end_char:
        frame.draw_pixel(end_char, box.position.down(end_at_pixel_int))

"""



constraint(max_width=2, max_height=2, hmax=2, hmin=3)
"""

