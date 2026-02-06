from functui.nav import InteractibleID, NavState, NavAction, ROOT_VERTICAL, Direction

root = ROOT_VERTICAL

# directiot=Direction.HORIZONTAL means navigating by
# NavAction.NAV_LEFT and NavAction.NAV_RIGHT
inner_container = root.child(0, direction=Direction.HORIZONTAL)
inner_child_1 = inner_container.child(0)
inner_child_2 = inner_container.child(1)
outer_child_1 = root.child(1)

# the above create a tree that looks something like this
# x-------------------------------x
# |x-----------------------------x|
# || inner_child_1 inner_child_2 ||
# |x-----------------------------x|
# | outer_child_1                 |
# x-------------------------------x


nav_tree = [inner_child_1, inner_child_2, outer_child_1]

nav = NavState()

# just activate keyboard navigation.
nav = nav.update(nav_tree=nav_tree, action=NavAction.NAV_DOWN)
assert nav.is_active(inner_child_1)

nav = nav.update(nav_tree=nav_tree, action=NavAction.NAV_RIGHT)
assert nav.is_active(inner_child_2)

nav = nav.update(nav_tree=nav_tree, action=NavAction.NAV_DOWN)
assert nav.is_active(outer_child_1)

