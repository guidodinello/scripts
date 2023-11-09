"""
Cheatsheet Manager

This script provides a command-line interface to manage and access cheatsheets 
in Markdown format. Users can open specific cheatsheets using their names, 
list all available cheatsheets, or receive suggestions for similar cheatsheet 
names using fuzzy string matching.

Usage:
    python cheatsheet.py <cheatsheet_name>
    python cheatsheet.py -h | --help
    python cheatsheet.py -l | --list | --show_all

Options:
    <cheatsheet_name>      The name of the cheatsheet to be opened.
    -h, --help             Show usage documentation.
    -l, --list, --show_all List all available cheatsheet names.

Global Constants:
    - CHEATSHEETS_FOLDER: 
        The folder path where cheatsheets in Markdown format are stored.
    - SIMILARITY_THRESHOLD: A threshold for fuzzy string matching similarity.
    
Author:
    guidodinello

"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Callable, Iterable, Optional, TypeVar

try:
    import fuzzy_string_matcher as sfm  # type: ignore[import]
except ImportError:
    import utils.string_fuzzy_matcher as sfm


from utils import configreader

PATH_DIR = os.path.join(os.path.dirname(__file__), "path.txt")

# Configurable Script Constants
CHEATSHEETS_FOLDER = configreader.read_mapping_file(PATH_DIR)["folder"]
SIMILARITY_THRESHOLD = 4

USAGE_DOCS = f"""
Usage: cheatsheet <cheatsheet_name>

This command opens the <cheatsheet_name>.md 
located under FOLDER using in VSCode.
If no file matches <cheatsheet_name>.md, it will show an error 
and print a list of similar files.

FOLDER={CHEATSHEETS_FOLDER}
"""


T = TypeVar("T")


def lazy_find(predicate: Callable[[T], bool], iterable: Iterable[T]) -> Optional[T]:
    return next((x for x in iterable if predicate(x)), None)


def cheatsheets():
    return Path(CHEATSHEETS_FOLDER).glob("*.md")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(USAGE_DOCS)
        sys.exit(1)

    match (sys.argv[1]):
        case "-h", "--help":
            print(USAGE_DOCS)
            sys.exit(1)
        case "-l", "--list", "--show_all":
            print("Available cheatsheets:")
            for cheatsheet in cheatsheets():
                print(f"\t* {cheatsheet.stem}")
            sys.exit(1)
        case cheatsheet_name:
            cheatsheet_name = cheatsheet_name.lower()  # pylint: disable=C0103

            cheatsheet_file = lazy_find(
                lambda x: x.stem.lower() == cheatsheet_name, cheatsheets()
            )

            if cheatsheet_file is not None:
                subprocess.run(
                    [
                        "code",
                        os.path.join(CHEATSHEETS_FOLDER, cheatsheet_file),
                    ],
                    check=True,
                )
                sys.exit(0)
            else:
                print("Cheatsheet not found. Maybe you meant:")
                similar = sfm.find_most_similar_words(  # type: ignore[attr-defined]
                    cheatsheet_name, [x.stem.lower() for x in cheatsheets()], 3
                )
                recommendations = list(
                    filter(lambda x: x.distance < SIMILARITY_THRESHOLD, similar)
                )
                if len(recommendations) == 0:
                    print(f"\t* {similar[0].word}")
                else:
                    for word, _ in recommendations:
                        print(f"\t* {word}")

                sys.exit(1)
