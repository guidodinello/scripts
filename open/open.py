"""
Open Project Manager

This script provides a command-line interface to manage project paths and their
associated names. It allows users to register, view, and access project paths.
The script supports adding new project entries, displaying registered projects,
and opening project paths in the default file manager and Visual Studio Code.
If a project name is misspelled or not found, the script provides suggestions
for similar project names using fuzzy string matching.

Usage:
    python project_path_manager.py [--list] [--add_entry <key> <abs_path>]
        [project_name [--relative_path <path>] [--keep]]

Author:
    guidodinello
"""

import os
import signal
import subprocess
import sys
from argparse import ArgumentParser
from logging import DEBUG
from pathlib import Path
from typing import Protocol

from utils import configreader
from utils.logger import get_logger
from utils.sfm import sfm

logger = get_logger()

SIMILARITY_THRESHOLD = 4
PATHS_DIR = os.path.join(os.path.dirname(__file__), ".env")

OPEN_FILE_MANAGER = False


def cleaned_env():
    env = os.environ.copy()

    env.pop("VIRTUAL_ENV", None)

    if "PATH" in env:
        paths = env["PATH"].split(":")
        cleaned_paths = [
            p
            for p in paths
            if not p.endswith("/.venv/bin") and not p.endswith("/venv/bin")
        ]
        env["PATH"] = ":".join(cleaned_paths)

    return env


class Command(Protocol):
    def execute(self) -> int: ...


class HelpCommand:
    def __init__(self, parser: ArgumentParser):
        self.parser = parser

    def execute(self):
        self.parser.print_help()
        return 0


class ListProjectsCommand:
    def __init__(self, paths: dict[str, Path]):
        self.paths = paths

    def execute(self):
        max_length = max(len(key) for key in self.paths.keys())
        for key, path in self.paths.items():
            print(f"* {key:{max_length}}: \t{path}")
        return 0


class AddProjectCommand:
    def __init__(self, key: str, abs_path: str, paths: dict[str, Path], paths_dir: str):
        self.key = key
        self.abs_path = abs_path
        self.paths = paths
        self.paths_dir = paths_dir

    def execute(self):
        configreader.add_to_mapping_file({self.key: self.abs_path}, self.paths_dir)
        logger.info("Added new project: %s ->  %s", self.key, self.abs_path)
        return 0


class OpenProjectCommand:
    def __init__(
        self,
        project_name: str,
        paths: dict[str, Path],
        relative_path: str | None = None,
        keep_terminal: bool = False,
    ):
        self.project_name = project_name.lower()
        self.paths = paths
        self.relative_path = relative_path
        self.keep_terminal = keep_terminal

    def execute(self):
        if self.project_name not in self.paths:
            return self._handle_not_found()

        path_project = self.paths[self.project_name]
        if self.relative_path:
            path_project = Path(path_project, self.relative_path)

        # Open VS Code
        try:
            subprocess.run(["code", path_project], env=cleaned_env(), check=True)
            logger.info("Opened VS Code for:  %s", path_project)
        except subprocess.SubprocessError as e:
            logger.error("Failed to open VS Code:  %s", e)
            return 1

        if OPEN_FILE_MANAGER:
            # Open file manager
            try:
                subprocess.run(["xdg-open", path_project], check=True)
                logger.info("Opened file manager for:  %s", path_project)
            except subprocess.SubprocessError as e:
                logger.error("Failed to open file manager:  %s", e)
                return 1

        # Close calling terminal if requested
        if not self.keep_terminal:
            try:
                os.kill(os.getppid(), signal.SIGHUP)
                logger.info("Closed parent terminal")
            except OSError as e:
                logger.error("Failed to close parent terminal:  %s", e)

        return 0

    def _handle_not_found(self) -> int:
        """Handle case when project name is not found"""
        msg = f"There's no project registered for the name: {self.project_name}\n"
        msg += "Maybe you meant:"
        print(msg)

        # Show fuzzy matched projects
        similar = []
        try:
            similar = sfm.find_most_similar_words(  # type: ignore[attr-defined]
                self.project_name,
                list(self.paths.keys()),
                3,
            )
        # pylint: disable-next=broad-exception-caught
        except Exception as e:
            logger.error("Error during fuzzy matching:  %s", e)
            print("Error finding similar project names")

        recommendations = [
            match for match in similar if match.distance < SIMILARITY_THRESHOLD
        ]

        # If there's no name good enough (above the threshold)
        if not recommendations:
            # Just show the most similar
            print(f"\t* {similar[0].word}")
        else:
            for match in recommendations:
                print(f"\t* {match.word}")

        logger.debug("Project not found: %s, suggestions provided", self.project_name)

        return 1


class CommandFactory:
    @staticmethod
    def create_command(
        parser: ArgumentParser,
        paths: dict[str, Path],
        paths_dir: str,
    ) -> Command:
        args = parser.parse_args()

        if args.debug:
            logger.setLevel(DEBUG)

        if args.project_name:
            return OpenProjectCommand(
                args.project_name,
                paths,
                args.relative_path,
                args.keep,
            )

        if args.list:
            return ListProjectsCommand(paths)

        if args.add_entry:
            key, abs_path = args.add_entry
            return AddProjectCommand(key, abs_path, paths, paths_dir)

        return HelpCommand(parser)


def configure_cli_args():
    parser = ArgumentParser(description="Open Project Manager")
    parser.add_argument("project_name", nargs="?", help="Name of the project to open")
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Print logged actions",
    )
    parser.add_argument(
        "--relative_path",
        "-rp",
        help="Relative path from execute path to project",
    )
    parser.add_argument(
        "--add_entry",
        "-ae",
        nargs=2,
        metavar=("key", "abs_path"),
        help="Add a new project entry",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List all registered projects",
    )
    parser.add_argument(
        "--keep",
        "-k",
        action="store_true",
        help="Keep the terminal open after executing",
    )
    return parser


def main():
    try:
        paths = configreader.read_mapping_file(PATHS_DIR)
        parser = configure_cli_args()

        command = CommandFactory.create_command(parser, paths, PATHS_DIR)
        exit_code = command.execute()

        return exit_code

    # pylint: disable-next=broad-exception-caught
    except Exception as e:
        logger.error("Unhandled exception: %s", e, exc_info=True)
        print(f"An error occurred: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
