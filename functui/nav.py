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

type NodeId = tuple[str, int] | str


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

    # keyboard nav data

    _active_data: _ActiveData | None = None
    """Interactible that is active through keyboard navigation."""

    _hovered_data: _HoveredData | None = None
    """Interactible that the mouse is hovering over."""

    _remembered_data: MappingProxyType[tuple[int, ...], int] = MappingProxyType({})


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
        if self._active_data is None:
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

    @staticmethod
    def _find_closest(tree: NavContainer, index: tuple[int, ...] = ()) -> _ActiveData | None:
        for i, child in enumerate(tree.children):
            if isinstance(child, NavContainer):
                return NavState._find_closest(child, index + (i,))
            return NavState._ActiveData(child, index + (i,))
        return None

    @staticmethod
    def _navigate_by_keyboard(
            tree: NavContainer,
            current_index: tuple[int, ...],
            action: KeyboardNavAction,
            remembered_data: MappingProxyType[tuple[int, ...], int]
    ) -> _ActiveData | bool:

        direction = Direction.HORIZONTAL if action in (NavAction.NAV_RIGHT, NavAction.NAV_LEFT) else Direction.VERTICAL
        backwards = False
        if direction == Direction.HORIZONTAL:
            backwards = True if action == NavAction.NAV_LEFT else False
        elif direction == Direction.VERTICAL:
            backwards = True if action == NavAction.NAV_UP else False


        found_current = False

        def _iter(tree: NavContainer, parent_index: tuple[int, ...] = ()) -> NavState._ActiveData | None:
            nonlocal found_current

            child_iterator = iter(enumerate(reversed(tree.children) if backwards else tree.children))

            if found_current and (parent_index in remembered_data):
                remembered_id = remembered_data[parent_index]
                for i in child_iterator:
                    if i == remembered_id:
                        break


            for i, child in child_iterator:
                i = len(tree.children) - i - 1 if backwards else i

                if isinstance(child, NavContainer):
                    if (res := _iter(child, parent_index + (i,) )) is not None:
                        # if we found new active, then return it
                        return res
                    continue

                if current_index == parent_index + (i,):
                    found_current = True
                    continue

                if found_current: #then search for next
                    if tree.direction == direction:
                        return NavState._ActiveData(child, parent_index + (i,))

        if (res := _iter(tree)) is not None:
            return res
        return found_current

    def update(
            self,
            res: Result | None = None,
            action: NavAction | None = None,
            nav_tree: NavContainer | None = None,
            mouse_position: Coordinate = Coordinate(-1, -1),
    ):
        next_active_data = self._active_data
        if nav_tree is not None and action in KEYBOARD_NAV_ACTION:
            if self._active_data is None:
                next_active_data = self._find_closest(nav_tree)
            else:
                nav_result = self._navigate_by_keyboard(nav_tree, self._active_data.tree_index, action) # type: ignore
                if isinstance(nav_result, self._ActiveData):
                    next_active_data = nav_result

                    # TODO: update remembered data
                elif not nav_result: # id was not found
                    next_active_data = self._find_closest(nav_tree)



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
