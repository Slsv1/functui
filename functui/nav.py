"""Tools to make layouts responsive to keyboard and mouse input"""
from enum import Enum, auto
from typing import Self, Literal, Iterable, Any, NamedTuple
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

type KeyboardNavAction = Literal[NavAction.NAV_DOWN, NavAction.NAV_UP, NavAction.NAV_LEFT, NavAction.NAV_RIGHT]
KEYBOARD_NAV_ACTION = [NavAction.NAV_DOWN, NavAction.NAV_UP, NavAction.NAV_LEFT, NavAction.NAV_RIGHT]

type ScrollAction = Literal[NavAction.PAGE_DOWN, NavAction.PAGE_UP, NavAction.SCROLL_DOWN, NavAction.SCROLL_UP]
SCROLL_ACTION = [NavAction.PAGE_DOWN, NavAction.PAGE_UP, NavAction.SCROLL_DOWN, NavAction.SCROLL_UP]

class Direction(Enum):
    """Used to specify navigation direction for a container defined by a :obj:`InteractibleID`.

    Attributes:
        VERTICAL:
        HORIZONTAL:"""
    VERTICAL = auto()
    HORIZONTAL = auto()

@dataclass(frozen=True, eq=True)
class InteractibleIDPart:
    direction: Direction
    local_id: int
    persistent: bool
    first_child_default: bool

@dataclass(frozen=True, eq=True)
class InteractibleID:
    """Used to create keyboard navigable tree. May be used either as a container or an item.

    If an id is created with the :obj:`InteractibleID.child` method (which is
    the preffered way of creating new InteractibleID's), the parent
    will be saved in the child as an :obj:`InteractibleIDPart` part."""
    data: tuple[InteractibleIDPart, ...]
    """Every intercatible id stores its own part at the end of the data tuple, and its ancestors parts before it."""
    def child(self, local_id: int, direction: None | Direction = None, persistent: bool = False) -> Self:
        """Create a new InteractibleID with specified attributes.

        The newly created child will remeber this ID as its parent.
        (as well as all of this ID's ancestors if there are any)

        Args:
            local_id:
                Child's local id relative to its parent
                (the InteractibleID on which this method is being called on).
                Used to distinguish this child from other children of same parent.
            direction:
                If child is used as a container, navigate it's children
                by specified direction. If no direction is provided, it will be
                inherited from child's parent.
                (the InteractibleID on which this method is being called on).
            persistent:
                If child is used as a container, remember which child
                was active and make it active insted of just the first elemnt
                if this container becomes active again.

        """

        if len(self.data):
            return self.__class__((*self.data, InteractibleIDPart(
                direction=self.data[-1].direction if direction is None else direction,
                local_id=local_id,
                persistent=persistent,
                first_child_default=False
            )))
        return self.__class__((*self.data, InteractibleIDPart(
            direction=direction if direction is not None else Direction.VERTICAL,
            local_id=local_id,
            persistent=persistent,
            first_child_default=False
        )))

    @property
    def direction(self):
        return self.data[-1].direction
    @property
    def local_id(self):
        return self.data[-1].local_id
    @property
    def persistent(self):
        return self.data[-1].persistent
    @property
    def first_child_default(self):
        return self.data[-1].first_child_default
    @property
    def depth(self):
        return len(self.data)
    @property
    def parent(self):
        """may error"""
        # may error?
        return InteractibleID(self.data[:-1])

    def mutual_ancestor(self, b: Self) -> Self:
        """Get the closest ID to which both self, and a are descendants."""
        # enumerate to retain order and not earase duplicates
        # BUG this will error if a is longer than b AND the last part of the shorter one matches the longer one
        # technicaly this should not happend but it can i guess
        out = []
        for i, part in enumerate(self.data):
            if part == b.data[i]:
                out.append(part)
            else:
                break
        return self.__class__(tuple(out))

    def ancestors(self) -> list[Self]:
        out = []
        for part in self.data:
            if len(out):
                out.append(InteractibleID((*out[-1].data, part,)))
            else:
                out.append(InteractibleID((part,)))
        return out

    def __bool__(self):
        return bool(len(self.data))
    # def with_attributes(self, direction: Direction | None = None, persistent: bool | None = None, first_child_default: bool | None = None):
    #     return self.__class__(
    #         (*self.data[:-1], InteractibleIDPart(
    #             direction=direction if direction is not None else self.data[-1].direction,
    #             local_id=self.data[-1].local_id,
    #             persistent=persistent if persistent is not None else self.data[-1].persistent,
    #             first_child_default=first_child_default if first_child_default is not None else self.data[-1].first_child_default)
    #         )
    #     )

ROOT_VERTICAL = InteractibleID((InteractibleIDPart(direction=Direction.VERTICAL, local_id=0, persistent=False, first_child_default=False),))
"""A Root for a keyboard navigation tree who's children are navigated vertically."""
ROOT_HORIZONTAL = InteractibleID((InteractibleIDPart(direction=Direction.HORIZONTAL, local_id=0, persistent=False, first_child_default=False),))
"""A Root for a keyboard navigation tree who's children are navigated horizontaly."""
EMPTY_INTERACTIBLE = InteractibleID(())
# EMPTY_INTERACTIBLE = InteractibleID((InteractibleIDPart(direction=Direction.VERTICAL, local_id=-1, persistent=False, first_child_default=False),))


@dataclass(frozen=True, eq=True)
class SetState(ResultData):
    new_state: tuple[tuple[InteractibleID, Any], ...]
    def merge_children(self, child_data):
        return SetState((*self.new_state, *child_data.new_state))
    @classmethod
    def create_dummy(cls):
        return cls(tuple())

def set_state(*new_state: tuple[InteractibleID, Any]):
    return SetState(new_state)

# @dataclass(frozen=True, eq=True)
# class NextInteractible(ResultData):
#     next_id: InteractibleID
#     def merge_children(self, child_data):
#         return child_data
#     @classmethod
#     def create_dummy(cls):
#         return cls(EMPTY_INTERACTIBLE)

class BoxData(NamedTuple):
    visible_box: Box
    actual_box: Box
    dragable: bool
class _HoveredData(NamedTuple):
    id: InteractibleID
    is_dragable: bool

@dataclass(frozen=True, eq=True)
class InteractionAreas(ResultData):
    areas: dict[InteractibleID, BoxData]
    def merge_children(self, child_data):
        self.areas.update(child_data.areas)
        return self
    @classmethod
    def create_dummy(cls):
        return cls({})

@dataclass(frozen=True)
class NavState:
    """A data structure storing and managing keyboard navigation and mouse data."""
    mouse_position: Coordinate = Coordinate(-1, -1)
    last_mouse_position: Coordinate = Coordinate(-1, -1)

    action: NavAction | None = None
    last_action: NavAction | None = None

    areas: MappingProxyType[InteractibleID, BoxData] = MappingProxyType({})
    """All areas that were marked by an :obj:`interaction_area` wrapper node."""
    _active_id: InteractibleID = EMPTY_INTERACTIBLE
    """Interactible that is active through keyboard navigation."""
    _hovered_data: _HoveredData = _HoveredData(EMPTY_INTERACTIBLE, False)
    """Interactible that the mouse is hovering over."""
    _held_down: InteractibleID = EMPTY_INTERACTIBLE
    _held_down_is_being_dragged: bool = False
    _just_held_down: InteractibleID = EMPTY_INTERACTIBLE

    _last_active_or_hovered_id: InteractibleID = EMPTY_INTERACTIBLE

    _persistent_state: MappingProxyType[tuple[InteractibleID, Any], Any] = MappingProxyType({}) # a MappingProxyType is used here as an immutable dict

    _persistent_selected_id: MappingProxyType[InteractibleID, InteractibleID] = MappingProxyType({})
    """if any interactible id part declares it self as persistent,
    then it's last selected child will be saved here"""


    @property
    def active_id(self):
        """The interactible that is active through keyboard navigation.

        Returns:
            :obj:`EMPTY_INTERACTIBLE` if no interactible is active"""
        return self._active_id
    #
    # persistent state
    #
    def try_state[T](self, interactible_id: InteractibleID, data: type[T]) -> T | None:
        return self._persistent_state.get((interactible_id, data))
    #
    # state management
    #
    def is_active(self, key: InteractibleID) -> bool:
        """Whether an interactible or one of its descendants is active via keyboard navigation"""
        if self._active_id == EMPTY_INTERACTIBLE:
            return False
        return key.data == self._active_id.data[: len(key.data)]

    def is_hover(self, key: InteractibleID) -> bool:
        """Whether the mouse is hovering above an interactible or one of its descendants.

        Note:
            Only one interactible at a time can be hovered, so if there is an
            overlap between interactible areas, only one of them will return
            true."""
        if self._hovered_data.id == EMPTY_INTERACTIBLE:
            return False
        return key.data == self._hovered_data.id.data[: len(key.data)]

    def is_selected(self, key: InteractibleID) -> bool:
        """Whether an interactible was selected by keyboard or mouse.

        This condition if often triggered by pressing enter while an
        interactible is active through keyboard navigation, or by releasing left click on an interactible with a mouse.

        More specifically, this returns whether an interactible is active and
        :obj:`~NavAction.SELECT_VIA_KEYBOARD` was triggered OR an interactible
        is hovered and :obj:`~NavAction.SELECT_VIA_MOUSE_END` was triggered
        """
        # prioritise keyboard navigation over hover
        if (self.is_active(key) and self.action == NavAction.SELECT_VIA_KEYBOARD):
            return True
        if self._just_held_down == EMPTY_INTERACTIBLE:
            return False
        return (key.data == self._just_held_down.data[: len(key.data)])

    def is_held_down(self, key: InteractibleID) -> bool:
        """Whether :obj:`~NavAction.SELECT_VIA_MOUSE_START` was triggered while hovering over interactive or its descendant, but before :obj:`~NavAction.SELECT_VIA_MOUSE_END` is triggered."""
        if self._held_down == EMPTY_INTERACTIBLE:
            return False
        return (key.data == self._held_down.data[: len(key.data)])


    def was_selected_or_active(self, key: InteractibleID) -> bool:
        for id in self._persistent_selected_id.values():
            if key.data == id.data[:len(key.data)]:
                return True
        return False
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
            nav_tree: list[InteractibleID] | None = None,
            mouse_position: Coordinate | None = None,
    ):
        """Create a new NavState based on data and user input.

        Args:
            res: Result created from a :obj:`~functui.classes.Layout` being renedered.
            action: User input parsed as an action.
            nav_data:
                The keyboard navigation tree that is used to perform keyboard
                navigation based on the action. InteractibleID's must be defined in order.
            mouse_position: Mouse position.
        Returns:
            A new NavState with keyboard navigation and mouse interactivity performed.
        """
        if res is None:
            res = Result()
        if nav_tree is None:
            nav_tree = []
        mouse_position = mouse_position if mouse_position is not None else self.mouse_position
        # persistent state
        next_state = dict(self._persistent_state)
        if set_state := res.try_data(SetState):
            for key, state in set_state.new_state:
                next_state[(key, state.__class__)] = state

        # keyboard navigation and mouse reactivity

        areas_result = res.try_data(InteractionAreas)
        if areas_result is None:
            areas = MappingProxyType({})
        else:
            areas = MappingProxyType(areas_result.areas)

        next_active_id = self._active_id
        next_hovered_data = self._hovered_data
        if action in (NavAction.NAV_DOWN, NavAction.NAV_LEFT, NavAction.NAV_UP, NavAction.NAV_RIGHT) and len(nav_tree):
            # handle keyboard nav and its edge cases

            # there is already an active id
            if self._active_id in nav_tree and self._active_id != EMPTY_INTERACTIBLE:
                selected_index = nav_tree.index(self._active_id)
                if result := _navigate_by_keyboard(self._persistent_selected_id, selected_index, tuple(nav_tree), action):
                    next_active_id = result.next_id
            # otherwise, use start from where we left off
            elif self._last_active_or_hovered_id != EMPTY_INTERACTIBLE and self._last_active_or_hovered_id in nav_tree:
                next_active_id = self._last_active_or_hovered_id
            else:
                next_active_id = nav_tree[0]

        else:
            # use mouse navigation instead
            for id, box_data in areas.items():
                if box_data.visible_box.is_point_inside(mouse_position):
                    next_hovered_data = _HoveredData(id, box_data.dragable)
                    break
            else:
                next_hovered_data = _HoveredData(EMPTY_INTERACTIBLE, False)

            # stop navigation by keyboard if we are using mouse
            if action == NavAction.SELECT_VIA_MOUSE_END:
                next_active_id = EMPTY_INTERACTIBLE



        # update persistent selected ids

        next_persistent_selected_id = dict(self._persistent_selected_id)
        next_last_active_or_hovered_id = self._last_active_or_hovered_id
        if next_active_id != EMPTY_INTERACTIBLE:
            next_last_active_or_hovered_id = next_active_id

            for ancestor in next_active_id.ancestors():
                if ancestor.persistent:
                    next_persistent_selected_id[ancestor] = next_active_id
        elif next_hovered_data != EMPTY_INTERACTIBLE:
            next_last_active_or_hovered_id = next_hovered_data.id

            if action == NavAction.SELECT_VIA_MOUSE_END and next_hovered_data.id == self._held_down:
                for ancestor in next_hovered_data.id.ancestors():
                    if ancestor.persistent:
                        next_persistent_selected_id[ancestor] = next_hovered_data.id
        # held down
        next_just_held_down = EMPTY_INTERACTIBLE
        next_held_down_is_being_dragged = self._held_down_is_being_dragged
        next_held_down = self._held_down
        if action == NavAction.SELECT_VIA_MOUSE_START:
            next_held_down = next_hovered_data.id
            next_held_down_is_being_dragged = next_hovered_data.is_dragable
        elif next_hovered_data.id != self._held_down and not self._held_down_is_being_dragged:
            next_held_down = EMPTY_INTERACTIBLE
        elif action == NavAction.SELECT_VIA_MOUSE_END:
            next_just_held_down = self._held_down
            next_held_down = EMPTY_INTERACTIBLE


        return NavState(
            mouse_position=mouse_position,
            last_mouse_position=self.mouse_position,
            action=action,
            last_action=self.action,
            areas=areas,
            _active_id=next_active_id,
            _hovered_data=next_hovered_data,
            _held_down=next_held_down,
            _held_down_is_being_dragged=next_held_down_is_being_dragged,
            _just_held_down=next_just_held_down,
            _last_active_or_hovered_id=next_last_active_or_hovered_id,
            _persistent_state=MappingProxyType(next_state),
            _persistent_selected_id=MappingProxyType(next_persistent_selected_id),
        )

def interaction_area(interactible_id: InteractibleID, dragable=False):
    """A wrapper node that marks its child layout as interactive.

    Meant to be used along with :obj:`NavState`.

    This wrapper node also retrieves at which size and position child layout was rendered at.
    This allows mouse hover detection, and in a scrollable container, automatically
    scrolling to a child that became active through keyboard navigation.
    """
    def _out(child: Layout):
        return Layout(
            func=interaction_area,
            min_size=child.min_size,
            render=partial(_render_interaction_area, interactible_id, child, dragable)
        )
    return _out


def _render_interaction_area(
    interactible_id: InteractibleID,
    child: Layout,
    dragable: bool,
    frame: Frame,
    box: Box
) -> Result:
    res = Result()
    availabe_box = frame.view_box.intersect(box)
    res.set_data(InteractionAreas({interactible_id: BoxData(availabe_box, box, dragable)}))
    res.add_children_after([child.render(frame, box)])
    return res

def _try_find_nearest(nav_data: tuple[InteractibleID, ...], current_index: int, direction: Direction, backwards: bool) -> int | None:
    next_index = current_index
    advance = lambda n: n + (-1 if backwards else 1)
    next_index = advance(next_index)

    original_depth = len(nav_data[current_index].data)
    original_id = nav_data[current_index]

    while True:
        # if next index is out of bounds
        if next_index >= len(nav_data) or next_index < 0:
            return None

        # if next index parent is a different direction then inputed,
        # in this case just keep advancing index untill either end of nav_data or direction matches and nav_depth is same or less than original

        if nav_data[next_index].mutual_ancestor(original_id).direction != direction:
            next_index = advance(next_index)
            continue
        # if skipped_ids and nav_data[next_index].depth > original_depth: # if depth exceeds original depth then continue
        #     # in a strcuture similar to the following:
        #     #
        #     # vbox
        #     #  - item 1
        #     #  - item 2 [start point]
        #     # hbox
        #     #  - item 1 (with vbox submenu)
        #     #    - item 1
        #     #    - item 2
        #     # vbox2
        #     #  - item 1 [desired end point on navigating down]
        #     #
        #     # in order to get to desired point you have to skip the items in the vbox submenu
        #     # it is this if statement that hinders you from selecting them.
        #     next_index = advance(next_index)
        #     continue

        # at this point we found an appropritae index
        return next_index

class _ApplyRulesResult(NamedTuple):
    next_index: int
    depth: int
    done: bool

def _apply_rules(
        persistent_selected_ids: MappingProxyType[InteractibleID, InteractibleID],
        nav_data: tuple[InteractibleID, ...],
        current_index: int,
        depth: int,
        backwards: bool
) -> _ApplyRulesResult:
    curr_id = nav_data[current_index]
    # find the depth at which the part is either persistent or first_child_default
    while True:
        if depth >= curr_id.depth:
            return _ApplyRulesResult(current_index, depth, True)

        part = curr_id.data[depth-1]
        if part.persistent or part.first_child_default:
            break
        depth += 1

    parent = InteractibleID(curr_id.data[:depth])


    if parent.persistent:
        remembered_id = persistent_selected_ids.get(parent, None)
        if remembered_id is not None and remembered_id in nav_data:
            next_id = remembered_id
            current_index = nav_data.index(next_id)
            return _ApplyRulesResult(current_index, depth, False)

    if backwards:
        # go to first index
        while True:
            if current_index <= 0:
                return _ApplyRulesResult(0, depth, True)

            curr_id = nav_data[current_index]
            if len(curr_id.data) > depth:
                if curr_id.data[depth].local_id == 0:
                    return _ApplyRulesResult(current_index, depth, False)
            else:
                return _ApplyRulesResult(current_index, depth, False)
            current_index -= 1
    return _ApplyRulesResult(current_index, depth, False)

class _NavigationResult(NamedTuple):
    next_id: InteractibleID
    shared_parent: InteractibleID

def _navigate_by_keyboard(
        persistent_selected_ids: MappingProxyType[InteractibleID, InteractibleID],
        current_index: int,
        nav_data: tuple[InteractibleID, ...],
        action: KeyboardNavAction 
) -> _NavigationResult | None:
    direction = Direction.HORIZONTAL if action in (NavAction.NAV_RIGHT, NavAction.NAV_LEFT) else Direction.VERTICAL
    backwards = False
    if direction == Direction.HORIZONTAL:
        backwards = True if action == NavAction.NAV_LEFT else False
    elif direction == Direction.VERTICAL:
        backwards = True if action == NavAction.NAV_UP else False

    next_index = _try_find_nearest(nav_data, current_index, direction, backwards)
    if next_index is not None:
        next_id = nav_data[next_index]
        current_id = nav_data[current_index]
        shared_parent = next_id.mutual_ancestor(current_id)

        next_parent = next_id.parent
        current_parent = current_id.parent

        if next_parent == current_parent: # parent is the same, no need to look up persistent data
            return _NavigationResult(next_id, shared_parent)

        done = False
        depth = shared_parent.depth
        while not done:
            next_index, depth, done = _apply_rules(persistent_selected_ids, nav_data, next_index, depth, backwards)
            depth += 1

        next_id = nav_data[next_index]
        return _NavigationResult(next_id, shared_parent)

def debug_interactible_str(id: InteractibleID):
    return "|".join(f"{"1" if i.first_child_default else " "}{"p" if i.persistent else " "}{i.local_id}{"V" if i.direction == Direction.VERTICAL else "H"}" for i in id.data)

def debug_nav_data_str(state: NavState, nav_data: Iterable[InteractibleID], persistent: bool = True):
    out = ["==| first_child_default | persistent | local_id | direction |=="]
    for id in nav_data:
        interactible_str = debug_interactible_str(id)
        out.append((">" if state.is_active(id) else " ") + interactible_str)
    if persistent and state._persistent_selected_id:
        out.append("== Persistent ==")
        for id in state._persistent_selected_id.values():
            interactible_str = debug_interactible_str(id)
            out.append((">" if state.is_active(id) else " ") + interactible_str)
    return "\n".join(out)


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

def v_scroll(container_id: InteractibleID, nav: NavState):
    """Allow vertical scrolling if child does not fit into available space."""
    def _v_scroll(child: Layout):
        at_y: int | None = nav.try_state(container_id, int)

        if at_y is None:
            at_y = 0

        # find active box
        active_box = None
        if (_active_box := nav.areas.get(nav.active_id, None)) is not None\
            and nav.action in KEYBOARD_NAV_ACTION\
            and nav.active_id.data[:len(container_id.data)] == container_id.data:
            # ^^^^^^^^ if active_id is a child of container_id
            active_box = _NewActiveBox(_active_box.actual_box, nav.action == NavAction.NAV_UP)


        at_y += nav.get_scrolling_difference()

        return Layout(
            func=v_scroll,
            min_size=child.min_size,
            render=partial(
                _v_scroll_render,
                at_y,
                active_box,
                container_id,
                child,
            )
        )
    return _v_scroll

def _v_scroll_render(
    scroll_dy: int,
    active_box: _NewActiveBox | None,
    container_id: InteractibleID,
    child: Layout,
    frame: Frame, 
    box: Box
):
    # move to selected if selected out of bounds
    a = []
    if active_box is not None:
        selected_at_y = active_box.box.position.y - box.position.y # to local space
        start = 0 # including
        end = box.height # excluding
        # a.append(text(str(start)))
        # a.append(text(str(end)))
        # a.append(text("scroll_dy:" + str(scroll_dy)))
        # a.append(text("selected_at_local:" + str(selected_at_y)))
        # a.append(text("selected_at_global:" + str(active_box)))

        if active_box.reverse:
            # aproach form below

            if not (start <= selected_at_y < end):
                scroll_dy += (selected_at_y)
        else:

            # aproach from above
            if not (start <= (selected_at_y + active_box.box.height) < end):
                scroll_dy += (selected_at_y - box.height + active_box.box.height)

    scroll_dy = clamp(scroll_dy,
        0,
        child.min_size(frame.measure_text, Rect(box.width, 9999)).height - box.height
    )

    res = Result()
    res.set_data(set_state((container_id, scroll_dy)))
    # a.append(text("final:" + str(scroll_dy)))
    modified_child = vbox([child,], at_y=-scroll_dy)
    res.add_children_after([modified_child.render(frame, box)])
    return res

@dataclass(frozen=True, eq=True)
class ResizableSplitData:
    at: int

def h_resizable_split(interactible_id: InteractibleID, nav: NavState, left: Layout, right: Layout, sep: Layout = vbar) -> Layout:
    split_data = nav.try_state(interactible_id, ResizableSplitData)
    if split_data is not None:
        split_at = split_data.at
    else:
        split_at = 20
    if nav.is_held_down(interactible_id):
        split_at += nav.get_mouse_drag_difference().x

    return Layout(
        func=h_resizable_split,
        min_size=min_size_horizontal([left.min_size, right.min_size, sep.min_size]),
        render=partial(
            _h_resizable_split_render,
            interactible_id,
            left,
            right,
            sep | interaction_area(interactible_id, dragable=True),
            split_at,
        )
    )

def _h_resizable_split_render(
        interactible_id: InteractibleID,
        left: Layout,
        right: Layout,
        sep: Layout,
        split_at: int,
        frame: Frame,
        box: Box
) -> Result:
    split_rect = sep.min_size(frame.measure_text, box.rect)

    split_at = clamp(split_at, 0, box.width-split_rect.width)

    left_box = Box(
        split_at,
        box.height,
        box.position,
    )
    right_box = Box(
        box.width-split_at-split_rect.width,
        box.height,
        box.position + Coordinate(split_at + split_rect.width, 0)
    )
    split_box = Box(
        split_rect.width,
        box.height,
        box.position + Coordinate(split_at, 0)
    )

    res = Result()
    res.set_data(set_state((interactible_id, ResizableSplitData(split_at))))

    res.add_children_after([
        left.render(frame.shrink_to(left_box), left_box),
        sep.render(frame.shrink_to(split_box), split_box),
        right.render(frame.shrink_to(right_box), right_box),
    ])
    return res

