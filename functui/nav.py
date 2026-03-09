"""Tools to make layouts responsive to keyboard and mouse input"""
from enum import Enum, auto
from typing import Hashable, Self, Literal, Iterable, Any, NamedTuple
from dataclasses import dataclass, field
from types import MappingProxyType
from functools import partial
from .classes import Coordinate, Result, ResultData, Layout, Frame, Box, Rect, clamp, min_size_horizontal
from .common import vbox, offset, vbar

__all__ = [
    "NavAction",
    "KeyboardNavAction",
    "ScrollAction",

    "Direction",
    "InteractibleID",
    "InteractibleIDPart",
    "ROOT_VERTICAL",
    "ROOT_HORIZONTAL",
    "EMPTY_INTERACTIBLE",

    "NavState",
    "DEFAULT_NAV_BINDINGS",

    "interaction_area",
    "v_scroll",
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

type NodeId = tuple[str, int] | str | None


@dataclass
class NavContainer:
    direction: Direction 
    children: tuple[NodeId | NavContainer, ...]
    remember: bool
    container_id: NodeId


def vnav(*ids: NodeId | NavContainer, remember:bool=False, container_id:NodeId=None):
    return NavContainer(Direction.VERTICAL, tuple(ids), remember, container_id)

def hnav(*ids: NodeId | NavContainer, remember:bool=False, container_id:NodeId=None):
    return NavContainer(Direction.HORIZONTAL, tuple(ids), remember, container_id)

@dataclass(frozen=True, eq=True)
class SetState(ResultData):
    new_state: tuple[tuple[NodeId, Any], ...]
    def merge_children(self, child_data):
        return SetState((*self.new_state, *child_data.new_state))

# @dataclass(frozen=True, eq=True)
# class NextInteractible(ResultData):
#     next_id: InteractibleID
#     def merge_children(self, child_data):
#         return child_data

class BoxData(NamedTuple):
    visible_box: Box
    actual_box: Box
    dragable: bool


@dataclass(frozen=True, eq=True)
class InteractionAreas(ResultData):
    areas: dict[NodeId, BoxData]
    def merge_children(self, child_data):
        self.areas.update(child_data.areas)
        return self

@dataclass(frozen=True)
class NavState:
    class _HoveredData(NamedTuple):
        id: NodeId
        is_dragable: bool
    class _ActiveData(NamedTuple):
        id: NodeId
        tree_index: tuple[int, ...]

    """A data structure storing and managing keyboard navigation and mouse data."""
    mouse_position: Coordinate = Coordinate(-1, -1)
    last_mouse_position: Coordinate = Coordinate(-1, -1)

    action: NavAction | None = None
    last_action: NavAction | None = None

    areas: MappingProxyType[NodeId, BoxData] = MappingProxyType({})
    """All areas that were marked by an :obj:`interaction_area` wrapper node."""

    _active_data: _ActiveData = _ActiveData(None, (0,))
    """Interactible that is active through keyboard navigation."""
    _hovered_data: _HoveredData = _HoveredData(None, False)
    """Interactible that the mouse is hovering over."""


    # _held_down: InteractibleID = EMPTY_INTERACTIBLE
    # _held_down_is_being_dragged: bool = False
    # _just_held_down: InteractibleID = EMPTY_INTERACTIBLE
    #
    # _last_active_or_hovered_id: InteractibleID = EMPTY_INTERACTIBLE
    #
    # _persistent_state: MappingProxyType[tuple[InteractibleID, Any], Any] = MappingProxyType({}) # a MappingProxyType is used here as an immutable dict
    #
    # _persistent_selected_id: MappingProxyType[InteractibleID, InteractibleID] = MappingProxyType({})
    # """if any interactible id part declares it self as persistent,
    # then it's last selected child will be saved here"""


    # @property
    # def active_id(self):
    #     """The interactible that is active through keyboard navigation.
    #
    #     Returns:
    #         :obj:`EMPTY_INTERACTIBLE` if no interactible is active"""
    #     return self._active_data.id
    #
    # persistent state
    #

    # def try_state[T](self, interactible_id: InteractibleID, data: type[T]) -> T | None:
    #     return self._persistent_state.get((interactible_id, data))
    #
    # state management
    #
    def is_active(self, key: NodeId) -> bool:
        if self._active_data.id == None:
            return False
        return key == self._active_data.id

    # def is_hover(self, key: NodeId) -> bool:
    #     """Whether the mouse is hovering above an interactible or one of its descendants.
    #
    #     Note:
    #         Only one interactible at a time can be hovered, so if there is an
    #         overlap between interactible areas, only one of them will return
    #         true."""
    #     if self._hovered_data.id == EMPTY_INTERACTIBLE:
    #         return False
    #     return key.data == self._hovered_data.id.data[: len(key.data)]

    # def is_selected(self, key: InteractibleID) -> bool:
    #     """Whether an interactible was selected by keyboard or mouse.
    #
    #     This condition if often triggered by pressing enter while an
    #     interactible is active through keyboard navigation, or by releasing left click on an interactible with a mouse.
    #
    #     More specifically, this returns whether an interactible is active and
    #     :obj:`~NavAction.SELECT_VIA_KEYBOARD` was triggered OR an interactible
    #     is hovered and :obj:`~NavAction.SELECT_VIA_MOUSE_END` was triggered
    #     """
    #     # prioritise keyboard navigation over hover
    #     if (self.is_active(key) and self.action == NavAction.SELECT_VIA_KEYBOARD):
    #         return True
        # if self._just_held_down == EMPTY_INTERACTIBLE:
        #     return False
        # return (key.data == self._just_held_down.data[: len(key.data)])

    # def is_held_down(self, key: InteractibleID) -> bool:
    #     """Whether :obj:`~NavAction.SELECT_VIA_MOUSE_START` was triggered while hovering over interactive or its descendant, but before :obj:`~NavAction.SELECT_VIA_MOUSE_END` is triggered."""
    #     if self._held_down == EMPTY_INTERACTIBLE:
    #         return False
    #     return (key.data == self._held_down.data[: len(key.data)])
    #
    #
    # def was_selected_or_active(self, key: InteractibleID) -> bool:
    #     for id in self._persistent_selected_id.values():
    #         if key.data == id.data[:len(key.data)]:
    #             return True
    #     return False
    def get_scrolling_difference(self):
        if self.action == NavAction.SCROLL_UP:
            return -3

        if self.action == NavAction.SCROLL_DOWN:
            return 3

        return 0
    def get_mouse_drag_difference(self) -> Coordinate:
        return self.mouse_position - self.last_mouse_position

    def update(
            self,
            res: Result | None = None,
            action: NavAction | None = None,
            nav_tree: NavContainer | None = None,
            mouse_position: Coordinate = Coordinate(-1, -1),
    ):
        next_active_data = self._active_data
        if nav_tree is not None and action in KEYBOARD_NAV_ACTION:
            if self._active_data.id == None:
                ... # TODO: find_closest

            nav_result = _navigate_by_keyboard(nav_tree, list(self._active_data.tree_index), action) # type: ignore
            next_active_data = self._ActiveData(nav_result.next_id, tuple(nav_result.next_index))



        areas = []
        return NavState(
            mouse_position=mouse_position,
            last_mouse_position=self.mouse_position,
            action=action,
            last_action=self.action,
            areas=self.areas,
            _active_data=next_active_data,
            _hovered_data=self._hovered_data,
        )

# def interaction_area(interactible_id: InteractibleID, dragable=False):
#     """A wrapper node that marks its child layout as interactive.
#
#     Meant to be used along with :obj:`NavState`.
#
#     This wrapper node also retrieves at which size and position child layout was rendered at.
#     This allows mouse hover detection, and in a scrollable container, automatically
#     scrolling to a child that became active through keyboard navigation.
#     """
#     def _out(child: Layout):
#         return Layout(
#             func=interaction_area,
#             min_size=child.min_size,
#             render=partial(_render_interaction_area, interactible_id, child, dragable)
#         )
#     return _out
#
#
# def _render_interaction_area(
#     interactible_id: InteractibleID,
#     child: Layout,
#     dragable: bool,
#     frame: Frame,
#     box: Box
# ) -> Result:
#     res = Result()
#     availabe_box = frame.view_box.intersect(box)
#     res.set_data(InteractionAreas({interactible_id: BoxData(availabe_box, box, dragable)}))
#     res.add_children_after([child.render(frame, box)])
#     return res


class _NavigationResult(NamedTuple):
    next_id: NodeId
    next_index: list[int]

def _navigate_by_keyboard(
        tree: NavContainer,
        current_index: list[int],
        action: KeyboardNavAction 
) -> _NavigationResult:

    direction = Direction.HORIZONTAL if action in (NavAction.NAV_RIGHT, NavAction.NAV_LEFT) else Direction.VERTICAL
    backwards = False
    if direction == Direction.HORIZONTAL:
        backwards = True if action == NavAction.NAV_LEFT else False
    elif direction == Direction.VERTICAL:
        backwards = True if action == NavAction.NAV_UP else False


    next_index = []
    found_current = False

    def _iter(tree: NavContainer):
        nonlocal found_current
        next_index.append(0)
        for i, child in enumerate(reversed(tree.children) if backwards else tree.children):
            next_index[-1] = i

            if isinstance(child, NavContainer):
                _iter(child)
                continue

            if current_index == next_index:
                found_current = True
                continue
            
            if found_current: #then search for next

                if len(next_index) < len(current_index) and tree.direction == direction:
                    return child
    next_id = _iter(tree)
    if found_current:
        return _NavigationResult(
            next_id=next_id,
            next_index=next_index
        )
    return _NavigationResult(
        next_id=None,
        next_index=[],
    )



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


class _NewActiveBox(NamedTuple):
    box: Box
    reverse: bool = False

# def v_scroll(container_id: InteractibleID, nav: NavState):
#     """Allow vertical scrolling if child does not fit into available space."""
#     def _v_scroll(child: Layout):
#         at_y: int | None = nav.try_state(container_id, int)
#
#         if at_y is None:
#             at_y = 0
#
#         # find active box
#         active_box = None
#         if (_active_box := nav.areas.get(nav.active_id, None)) is not None\
#             and nav.action in KEYBOARD_NAV_ACTION\
#             and nav.active_id.data[:len(container_id.data)] == container_id.data:
#             # ^^^^^^^^ if active_id is a child of container_id
#             active_box = _NewActiveBox(_active_box.actual_box, nav.action == NavAction.NAV_UP)
#
#
#         at_y += nav.get_scrolling_difference()
#
#         return Layout(
#             func=v_scroll,
#             min_size=child.min_size,
#             render=partial(
#                 _v_scroll_render,
#                 at_y,
#                 active_box,
#                 container_id,
#                 child,
#             )
#         )
#     return _v_scroll
#
# def _v_scroll_render(
#     scroll_dy: int,
#     active_box: _NewActiveBox | None,
#     container_id: InteractibleID,
#     child: Layout,
#     frame: Frame, 
#     box: Box
# ):
#     # move to selected if selected out of bounds
#     a = []
#     if active_box is not None:
#         selected_at_y = active_box.box.position.y - box.position.y # to local space
#         start = 0 # including
#         end = box.height # excluding
#         # a.append(text(str(start)))
#         # a.append(text(str(end)))
#         # a.append(text("scroll_dy:" + str(scroll_dy)))
#         # a.append(text("selected_at_local:" + str(selected_at_y)))
#         # a.append(text("selected_at_global:" + str(active_box)))
#
#         if active_box.reverse:
#             # aproach form below
#
#             if not (start <= selected_at_y < end):
#                 scroll_dy += (selected_at_y)
#         else:
#
#             # aproach from above
#             if not (start <= (selected_at_y + active_box.box.height) < end):
#                 scroll_dy += (selected_at_y - box.height + active_box.box.height)
#
#     scroll_dy = clamp(scroll_dy,
#         0,
#         child.min_size(frame.measure_text, Rect(box.width, 9999)).height - box.height
#     )
#
#     res = Result()
#     res.set_data(set_state((container_id, scroll_dy)))
#     # a.append(text("final:" + str(scroll_dy)))
#     modified_child = vbox([child,], at_y=-scroll_dy)
#     res.add_children_after([modified_child.render(frame, box)])
#     return res

