from functui.nav import NavState, NavAction, vnav, hnav

def test_nav_up_and_down():
    nav = NavState()
    tree=vnav("a", "b", "c")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_DOWN)
    assert nav.is_active("a")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_DOWN)
    assert nav.is_active("b")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_DOWN)
    assert nav.is_active("c")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_UP)
    assert nav.is_active("b")

    # those should not do anything.
    nav = nav.update(nav_tree=tree, action=NavAction.NAV_LEFT)
    assert nav.is_active("b")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_RIGHT)
    assert nav.is_active("b")

def test_nav_right_and_left():
    nav = NavState()
    tree=hnav("a", "b", "c")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_RIGHT)
    assert nav.is_active("a")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_RIGHT)
    assert nav.is_active("b")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_RIGHT)
    assert nav.is_active("c")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_LEFT)
    assert nav.is_active("b")

    # those should not do anything.
    nav = nav.update(nav_tree=tree, action=NavAction.NAV_UP)
    assert nav.is_active("b")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_DOWN)
    assert nav.is_active("b")

def test_nav_nested_same_direction():
    nav = NavState()
    tree=vnav("outer 1", vnav("nested 1", "nested 2"), "outer 2")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_DOWN)
    assert nav.is_active("outer 1")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_DOWN)
    assert nav.is_active("nested 1")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_DOWN)
    assert nav.is_active("nested 2")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_DOWN)
    assert nav.is_active("outer 2")


    # now go back up
    # (skip over nested 2 since we start at child number 1 by default)

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_UP)
    assert nav.is_active("nested 1")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_UP)
    assert nav.is_active("outer 1")


def test_nav_inner_different_direction_skip():
    nav = NavState()
    tree=vnav("outer 1", hnav("inner 1", "inner 2"), "outer 2")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_DOWN)
    assert nav.is_active("outer 1")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_DOWN)
    assert nav.is_active("inner 1")

    # skip inner 2
    nav = nav.update(nav_tree=tree, action=NavAction.NAV_DOWN)
    assert nav.is_active("outer 2")

    # now go back up

    # skip inner 2 here aswell
    nav = nav.update(nav_tree=tree, action=NavAction.NAV_UP)
    assert nav.is_active("inner 1")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_UP)
    assert nav.is_active("outer 1")

def test_nav_nested_different_direction_skip():
    nav = NavState()
    tree=vnav(
        "outer 1",
        hnav(
            "middle 1",

            # when navigating down, we should skip over this even though it is
            # a vertical container.
            vnav("inner 1", "inner 2"),
        ),
        "outer 2"
    )

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_DOWN)
    assert nav.is_active("outer 1")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_DOWN)
    assert nav.is_active("middle 1")

    # skip over inner stuff
    nav = nav.update(nav_tree=tree, action=NavAction.NAV_DOWN)
    assert nav.is_active("outer 2")

    # go back up

    # skip here aswell
    nav = nav.update(nav_tree=tree, action=NavAction.NAV_UP)
    assert nav.is_active("middle 1")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_UP)
    assert nav.is_active("outer 1")


def test_nav_remember():
    nav = NavState()
    tree=vnav("outer 1", hnav("nested 1", "nested 2", remember=True))

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_DOWN)
    assert nav.is_active("outer 1")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_DOWN)
    assert nav.is_active("nested 1")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_RIGHT)
    assert nav.is_active("nested 2")

    nav = nav.update(nav_tree=tree, action=NavAction.NAV_UP)
    assert nav.is_active("outer 1")

    # here we remember that nested 2 was selected before
    nav = nav.update(nav_tree=tree, action=NavAction.NAV_DOWN)
    assert nav.is_active("nested 2")


