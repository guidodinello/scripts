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
from itertools import chain
from pathlib import Path

from utils import configreader
from utils.functional_utils import lazy_find
from utils.logger import get_logger
from utils.sfm import sfm

logger = get_logger()


PATH_DIR = os.path.join(os.path.dirname(__file__), ".env")

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


def cheatsheets():
    extensions = ["*.md", "*.txt", "*.pdf"]
    return chain(*(Path(CHEATSHEETS_FOLDER).glob(ext) for ext in extensions))


def open_cheatsheet(cheatsheet_path: Path):
    path = os.path.join(CHEATSHEETS_FOLDER, cheatsheet_path)
    # subprocess.run(["code", path], check=True)
    subprocess.run(["xdg-open", path], check=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(USAGE_DOCS)
        sys.exit(1)

    match sys.argv[1]:
        case "-h" | "--help":
            print(USAGE_DOCS)
            sys.exit(1)
        case "-l" | "--list" | "--show_all":
            print("Available cheatsheets:")
            for cheatsheet in cheatsheets():
                print(f"\t* {cheatsheet.stem}")
            sys.exit(1)
        case cheatsheet_name:
            cheatsheet_name = cheatsheet_name.lower()  # pylint: disable=C0103

            cheatsheet_file = lazy_find(
                lambda x: x.stem.lower() == cheatsheet_name,
                cheatsheets(),
            )

            if cheatsheet_file is not None:
                open_cheatsheet(cheatsheet_file)
                sys.exit(0)

            print("Cheatsheet not found. Maybe you meant:")
            similar = sfm.find_most_similar_words(  # type: ignore[attr-defined]
                cheatsheet_name,
                [x.stem.lower() for x in cheatsheets()],
                3,
            )
            recommendations = list(
                filter(lambda x: x.distance < SIMILARITY_THRESHOLD, similar),
            )
            if len(recommendations) == 0:
                # if no good enough recommendations, show first similar
                print(f"\t1- {similar[0].word}")
                recommendations = [similar[0]]
            else:
                for index, (word, _) in enumerate(recommendations):
                    print(f"\t{index}- {word}")

            read = input("Open a similar cheatsheet? [number/n] ")
            if read == "n":
                sys.exit(1)

            try:
                index = int(read)
                cheatsheet_file = lazy_find(
                    lambda x: x.stem.lower() == recommendations[index - 1].word,
                    cheatsheets(),
                )
                open_cheatsheet(cheatsheet_file)  # type: ignore[arg-type]
                sys.exit(0)
            except (ValueError, IndexError):
                print("Invalid input!")
                sys.exit(1)
