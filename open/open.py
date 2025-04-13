"""
Open Project Manager

This script provides a command-line interface to manage project paths and their
associated names. It allows users to register, view, and access project paths.
The script supports adding new project entries, displaying registered projects,
and opening project paths in the default file manager and Visual Studio Code.
If a project name is misspelled or not found, the script provides suggestions
for similar project names using fuzzy string matching.

Usage:
    python project_path_manager.py [--list] [--add_entry <key> <abs_path>] [project_name [--relative_path <path>] [--keep]]

Author:
    guidodinello
"""

import os
import signal
import subprocess
import sys
from argparse import ArgumentParser
from logging import DEBUG, Logger

from utils import configreader  # type: ignore
from utils.logger import get_logger  # type: ignore

logger: Logger = get_logger(__name__)

try:
    # using the rust module
    import fuzzy_string_matcher as sfm  # type: ignore[import]

    logger.debug("Using Rust utils module")
except ImportError:
    # fallback to the python module
    import utils.string_fuzzy_matcher as sfm  # type: ignore

    logger.debug("Using Python utils module")


SIMILARITY_THRESHOLD = 4
PATHS_DIR = os.path.join(os.path.dirname(__file__), ".env")


class Command:
    """Base command interface"""

    def execute(self) -> int:
        """Execute the command and return exit code"""
        raise NotImplementedError


class HelpCommand(Command):
    def __init__(self, parser: ArgumentParser):
        self.parser = parser

    def execute(self) -> int:
        self.parser.print_help()
        return 0


class ListProjectsCommand(Command):
    def __init__(self, paths: dict[str, str]):
        self.paths = paths

    def execute(self) -> int:
        max_length = max(len(key) for key in self.paths.keys())
        for key, path in self.paths.items():
            print(f"* {key:{max_length}}: \t{path}")
        return 0


class AddProjectCommand(Command):
    def __init__(self, key: str, abs_path: str, paths: dict[str, str], paths_dir: str):
        self.key = key
        self.abs_path = abs_path
        self.paths = paths
        self.paths_dir = paths_dir

    def execute(self) -> int:
        self.paths[self.key] = self.abs_path
        configreader.add_to_mapping_file({self.key: self.abs_path}, self.paths_dir)
        logger.info(f"Added new project: {self.key} -> {self.abs_path}")
        return 0


class OpenProjectCommand(Command):
    def __init__(
        self,
        project_name: str,
        paths: dict[str, str],
        relative_path: str | None = None,
        keep_terminal: bool = False,
    ):
        self.project_name = project_name.lower()
        self.paths = paths
        self.relative_path = relative_path
        self.keep_terminal = keep_terminal

    def execute(self) -> int:
        if self.project_name not in self.paths:
            return self._handle_not_found()

        path_project = self.paths[self.project_name]
        if self.relative_path:
            path_project = os.path.join(path_project, self.relative_path)

        # Open file manager
        try:
            subprocess.run(["xdg-open", path_project], check=True)
            logger.info(f"Opened file manager for: {path_project}")
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to open file manager: {e}")
            return 1

        # Open VS Code
        try:
            subprocess.run(["code", path_project], check=True)
            logger.info(f"Opened VS Code for: {path_project}")
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to open VS Code: {e}")
            return 1

        # Close calling terminal if requested
        if not self.keep_terminal:
            try:
                os.kill(os.getppid(), signal.SIGHUP)
                logger.info("Closed parent terminal")
            except OSError as e:
                logger.error(f"Failed to close parent terminal: {e}")

        return 0

    def _handle_not_found(self) -> int:
        """Handle case when project name is not found"""
        msg = f"There's no project registered for the name: {self.project_name}\n"
        msg += "Maybe you meant:"
        print(msg)

        # Show fuzzy matched projects
        try:
            similar = sfm.find_most_similar_words(  # type: ignore[attr-defined]
                self.project_name,
                list(self.paths.keys()),
                3,
            )

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

            logger.warning(
                f"Project not found: {self.project_name}, suggestions provided",
            )

        except Exception as e:
            logger.error(f"Error during fuzzy matching: {e}")
            print("Error finding similar project names")

        return 1


class CommandFactory:
    @staticmethod
    def create_command(
        parser: ArgumentParser,
        paths: dict[str, str],
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
        elif args.list:
            return ListProjectsCommand(paths)
        elif args.add_entry:
            key, abs_path = args.add_entry
            return AddProjectCommand(key, abs_path, paths, paths_dir)
        else:
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

    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        print(f"An error occurred: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
