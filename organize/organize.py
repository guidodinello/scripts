import os
import functools
from typing import Callable
import code


def str_matcher_iterator(substr: str, case_sensitive: bool):
    transform = (lambda x: x) if case_sensitive else (lambda x: x.lower())
    for name in os.listdir("."):
        if transform(substr) in transform(name):
            yield name


def foreach(
    action: Callable[[str], None],
    substr: str,
    case_sensitive: bool = False,
    debug: bool = True,
):
    for file in str_matcher_iterator(substr, case_sensitive):
        if debug:
            print(f"{action.__name__} performed over {file}")
        action(file)


def move(dst: str, *args, **kwargs):
    """Move files that match the substr to the (absolute) destination
    Example: move("/home/user/Downloads", substr="pdf")
    """

    def move_action(name):
        os.rename(name, dst=f"{dst}/{name}")

    foreach(move_action, *args, **kwargs)


show = functools.partial(foreach, print, debug=False)
show.__doc__ = "Show files that has the substr"
remove = functools.partial(foreach, os.remove)
remove.__doc__ = "Remove files that has the substr"

ls = functools.partial(show, substr="")
cd = os.chdir


# pylint: disable=W0622
def help(specific_command: str = ""):
    if specific_command == "":
        print("Available commands: move, show, remove, ls, cd, help")
    else:
        print(f"Help for {specific_command}")
        print(globals()[specific_command].__doc__)


if __name__ == "__main__":
    code.interact(local=locals())
