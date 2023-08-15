"""
Open Project Manager

This script provides a command-line interface to manage project paths and their 
associated names. It allows users to register, view, and access project paths. 
The script supports adding new project entries, displaying registered projects, 
and opening project paths in the default file manager and Visual Studio Code.
If a project name is misspelled or not found, the script provides suggestions 
for similar project names using fuzzy string matching.

Usage:
    python project_path_manager.py [--show] [project_name] 
        [--relative_path <path>] [--add_entry <key> <abs_path>]

Options:
    project_name           
        The name of the registered project to be accessed.
    --relative_path <path> 
        Specify a relative path within the registered project.
    --add_entry <key> <abs_path> 
        Add a new project entry with the provided key and absolute path.
    --show                 
        Display a list of registered project names and their associated paths.

Example usage:
    1. View registered projects:
       python open.py --show

    2. Access a registered project:
       python open.py my_project

    3. Access a specific path within a registered project:
       python open.py my_project --relative_path src/

    4. Add a new project entry:
       python open.py --add_entry project_key ~/path/to/new_project

Global Constants:
    - SIMILARITY_THRESHOLD: A threshold for fuzzy string matching similarity.
    - PATHS_DIR: The path to the configuration file storing project paths.

Author:
    guidodinello
"""

import os
import signal
import subprocess
import sys
from argparse import ArgumentParser

# using the rust module
import fuzzy_string_matcher as sfm

from utils import configreader


SIMILARITY_THRESHOLD = 4
PATHS_DIR = os.path.join(os.path.dirname(__file__), "paths.txt")

if __name__ == "__main__":
    PATHS = configreader.read_mapping_file(PATHS_DIR)

    parser = ArgumentParser()
    mutex_group = parser.add_mutually_exclusive_group(required=True)

    mutex_group.add_argument("project_name", nargs="?")
    mutex_group.add_argument("--relative_path", "--rp")
    mutex_group.add_argument(
        "--add_entry", "--ae", nargs=2, metavar=("key", "abs_path")
    )
    mutex_group.add_argument("--show", "--s", action="store_true")
    args = parser.parse_args()

    project = args.project_name
    if project is None:
        if args.show:
            for key, path in PATHS.items():
                print(f"* {key}: \t{path}")
            sys.exit(0)
        else:
            key, abs_path = args.add_entry
            PATHS[key] = abs_path
            configreader.add_to_mapping_file({key: abs_path}, PATHS_DIR)
            sys.exit(0)
    else:
        project = project.lower()

        if project not in PATHS:
            msg = f"Theres no project registered for the name: {project} \n"
            msg += "Maybe you meant:"
            print(msg)

            # show fuzzy matched projects
            similar = sfm.find_most_similar_words(  # type: ignore[attr-defined]
                project, list(PATHS.keys()), 3
            )
            recommendations = list(
                filter(lambda x: x.distance < SIMILARITY_THRESHOLD, similar)
            )
            # if theres no name good enough (above the threshold)
            if len(recommendations) == 0:
                # just show the most similar
                print(f"\t* {similar[0].word}")
            else:
                for word, _ in recommendations:
                    print(f"\t* {word}")

            sys.exit(1)

        path_project = PATHS[project]
        if args.relative_path:
            path_project = path_project.joinpath(args.relative_path)

        # open the file system manager
        subprocess.run(["xdg-open", path_project], check=True)
        # open vscode
        subprocess.run(["code", path_project], check=True)

        # close calling terminal
        os.kill(os.getppid(), signal.SIGHUP)
