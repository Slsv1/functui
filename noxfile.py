import nox

TEST_VERSION_MATRIX = ["3.12", "3.13", "3.14"]

@nox.session(python=TEST_VERSION_MATRIX)
def tests(session: nox.Session):
    session.install(".")
    session.install('pytest')
    session.run('pytest')

@nox.session(python=TEST_VERSION_MATRIX)
def doctest(session: nox.Session):
    session.install(".")
    session.install("sphinx")
    session.run("sphinx-build", "-M", "doctest", "docs/", "docs/_build")

# @nox.session
# def mypy(session: nox.Session) -> None:
#     session.install(".")
#     session.install("mypy")
#
#     # sometimes mypy may fail because of sqlite development tools not being available on your machine
#     # to fix this you can install them and then reinstall your python interpreter.
#
#     # on fedora: sudo dnf install sqlite-devel
#     session.run(
#         "mypy", 
#         "--show-traceback",
#         "--no-incremental",
#         "src")


@nox.session(python=TEST_VERSION_MATRIX)
def pyright(session: nox.Session) -> None:
    session.install(".")
    session.install("pyright")

    session.run(
        "pyright",
        "src",
    )
