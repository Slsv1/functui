import curses
from enum import Enum, auto
from typing import Self, Literal, Iterable, Any, NamedTuple
from dataclasses import dataclass, field
from types import MappingProxyType
from functools import partial
from .classes import Coordinate, Result, ResultData, applicable, Layout, Frame, Box

class NavAction(Enum):
    SELECT = auto()
    NAV_UP = auto()
    NAV_RIGHT = auto()
    NAV_DOWN = auto()
    NAV_LEFT = auto()
type NavDirAction = Literal[NavAction.NAV_DOWN, NavAction.NAV_UP, NavAction.NAV_LEFT, NavAction.NAV_RIGHT]

class Direction(Enum):
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
    data: tuple[InteractibleIDPart, ...]
    """every intercatible id stores its own part at the end of the data tuple, and its ancestors part before it"""
    def child(self, local_id: int, direction: None | Direction = None, persistent: bool = False, first_child_default: bool=False) -> Self:
        if len(self.data):
            return self.__class__((*self.data, InteractibleIDPart(
                direction=self.data[-1].direction if direction is None else direction,
                local_id=local_id,
                persistent=persistent,
                first_child_default=first_child_default
            )))
        return self.__class__((*self.data, InteractibleIDPart(
            direction=direction if direction is not None else Direction.VERTICAL,
            local_id=local_id,
            persistent=persistent,
            first_child_default=first_child_default
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
        return InteractibleID(self.data[:-1])

    def mutual_parent(self, b: Self) -> Self:
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
ROOT_HORIZONTAL = InteractibleID((InteractibleIDPart(direction=Direction.HORIZONTAL, local_id=0, persistent=False, first_child_default=False),))
EMPTY_INTERACTIBLE = InteractibleID(())


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

@dataclass(frozen=True, eq=True)
class NextInteractible(ResultData):
    next_id: InteractibleID
    def merge_children(self, child_data):
        return child_data
    @classmethod
    def create_dummy(cls):
        return cls(EMPTY_INTERACTIBLE)

@dataclass(frozen=True)
class NavState:
    mouse_position: Coordinate = Coordinate(-1, -1)
    action: NavAction | None = None
    _selected_id: InteractibleID = EMPTY_INTERACTIBLE
    _persistent_state: MappingProxyType[tuple[InteractibleID, Any], Any] = MappingProxyType({}) # a MappingProxyType is used here as an immutable dict
    _persistent_selected_id: MappingProxyType[InteractibleID, InteractibleID] = MappingProxyType({})
    """if any interactible id part declares it self as persistent,
    then it's last selected child will be saved here"""


    @property
    def selected_id(self):
        return self._selected_id
    #
    # persistent state
    #
    def try_state[T](self, interactible_id: InteractibleID, data: type[T]) -> T | None:
        return self._persistent_state.get((interactible_id, data))
    #
    # state management
    #
    def is_active(self, key: InteractibleID) -> bool:
        if self._selected_id == EMPTY_INTERACTIBLE:
            return False
        return key.data == self._selected_id.data[: len(key.data)]
    def is_selected(self, key: InteractibleID) -> bool:
        return self.is_active(key) and self.action == NavAction.SELECT
    def was_active(self, key: InteractibleID) -> bool:
        for id in self._persistent_selected_id.values():
            if key.data == id.data[:len(key.data)]:
                return True
        return False

    # while True:
    #    res = render() (print)
    #    input()
    #    step()

    def update(
            self,
            res: Result,
            action: NavAction | None = None,
            nav_data: list[InteractibleID] = field(default_factory=list),
            mouse_position: Coordinate | None = None,
    ):
        # persistent state
        next_state = dict(self._persistent_state)
        if set_state := res.try_data(SetState):
            for key, state in set_state.new_state:
                next_state[(key, state.__class__)] = state

        # reactivity
        next_persistent_selected_id = dict(self._persistent_selected_id)

        next_id = self._selected_id
        if action in (NavAction.NAV_DOWN, NavAction.NAV_LEFT, NavAction.NAV_UP, NavAction.NAV_RIGHT) and len(nav_data):
            # handle keyboard nav and its edge cases
            if self._selected_id in nav_data and self._selected_id != EMPTY_INTERACTIBLE:
                selected_index = nav_data.index(self._selected_id)
                if result := _navigate_by_keyboard(self._persistent_selected_id, selected_index, tuple(nav_data), action):
                    next_id = result.next_id

                    if result.shared_parent.persistent:
                        next_persistent_selected_id[result.shared_parent] = result.next_id
            else:
                next_id = nav_data[0]
        elif next_inderactible := res.try_data(NextInteractible):
            # use mouse navigation instead
            next_id = next_inderactible.next_id

        if self._selected_id not in nav_data and nav_data:
            next_id = nav_data[0]
        return NavState(
            mouse_position=mouse_position if mouse_position is not None else self.mouse_position,
            action=action,
            _selected_id=next_id,
            _persistent_state=MappingProxyType(next_state),
            _persistent_selected_id=MappingProxyType(next_persistent_selected_id),
        )
    def interaction_area(self, interactible_id: InteractibleID):
        @applicable
        def _out(child: Layout):
            return Layout(
                func=self.interaction_area,
                min_size=child.min_size,
                render=partial(_render_read_box, interactible_id, self.mouse_position, child)
            )
        return _out


def _render_read_box(
    interactible_id: InteractibleID,
    mouse_position: Coordinate,
    child: Layout,
    frame: Frame,
    box: Box
) -> Result:
    res = Result()
    availabe_box = frame.view_box.intersect(box)
    if availabe_box.is_point_inside(mouse_position):
        res.set_data(NextInteractible(interactible_id))
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

        if nav_data[next_index].mutual_parent(original_id).direction != direction:
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
        action: NavDirAction 
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
        shared_parent = next_id.mutual_parent(current_id)

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


default_nav_bindings = {
    "h": NavAction.NAV_LEFT,
    "left": NavAction.NAV_LEFT,
    "j": NavAction.NAV_DOWN,
    "down": NavAction.NAV_DOWN,
    "k": NavAction.NAV_UP,
    "up": NavAction.NAV_UP,
    "l": NavAction.NAV_RIGHT,
    "right": NavAction.NAV_RIGHT,
    "enter": NavAction.SELECT,
    "left mouse": NavAction.SELECT,
    " ": NavAction.SELECT,
}
