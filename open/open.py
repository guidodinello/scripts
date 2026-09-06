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

from logger import get_logger, init_logging

from utils import LOG_FILE, configreader
from utils.configreader import ProjectEntry
from utils.sfm import sfm

logger = get_logger(__name__)

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
    def __init__(self, paths: dict[str, ProjectEntry]):
        self.paths = paths

    def execute(self):
        max_length = max(len(key) for key in self.paths)
        for key, entry in self.paths.items():
            suffix = f"  [command: {entry.command}]" if entry.command else ""
            print(f"* {key:{max_length}}: \t{entry.path}{suffix}")
        return 0


class AddProjectCommand:
    def __init__(
        self,
        key: str,
        entry: ProjectEntry,
        paths: dict[str, ProjectEntry],
        paths_dir: str,
    ):
        self.key = key
        self.entry = entry
        self.paths = paths
        self.paths_dir = paths_dir

    def execute(self):
        configreader.add_to_mapping_file({self.key: self.entry}, self.paths_dir)
        logger.info("Added new project: %s ->  %s", self.key, self.entry)
        return 0


class SetProjectCommandCommand:
    def __init__(
        self,
        key: str,
        command: str,
        paths: dict[str, ProjectEntry],
        paths_dir: str,
    ):
        self.key = key
        self.command = command
        self.paths = paths
        self.paths_dir = paths_dir

    def execute(self):
        if self.key not in self.paths:
            print(f"There's no project registered for the name: {self.key}")
            return 1

        entry = ProjectEntry(self.paths[self.key].path, self.command)
        configreader.add_to_mapping_file({self.key: entry}, self.paths_dir)
        logger.info("Set command for project %s: %s", self.key, self.command)
        return 0


class OpenProjectCommand:
    def __init__(
        self,
        project_name: str,
        paths: dict[str, ProjectEntry],
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

        entry = self.paths[self.project_name]
        path_project = entry.path
        if self.relative_path:
            path_project = Path(path_project, self.relative_path)

        if entry.command:
            self._run_custom_command(entry.command, path_project)

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

    def _run_custom_command(self, command: str, cwd: Path) -> None:
        """Launch the project's registered custom command in parallel,
        without blocking on it (e.g. spinning up a docker container)."""
        try:
            subprocess.Popen(  # pylint: disable=consider-using-with
                command,
                shell=True,
                cwd=cwd,
                env=cleaned_env(),
            )
            logger.info("Launched custom command for %s: %s", cwd, command)
        except OSError as e:
            logger.error("Failed to launch custom command:  %s", e)

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
        except Exception as e:  # noqa: BLE001 — best-effort, must not crash
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
        paths: dict[str, ProjectEntry],
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
            entry = ProjectEntry(Path(abs_path), args.command)
            return AddProjectCommand(key, entry, paths, paths_dir)

        if args.set_command:
            key, command = args.set_command
            return SetProjectCommandCommand(key, command, paths, paths_dir)

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
        "--command",
        "-c",
        help=(
            "Custom command to run in parallel when opening the project "
            "(used together with --add_entry)"
        ),
    )
    parser.add_argument(
        "--set_command",
        "-sc",
        nargs=2,
        metavar=("key", "command"),
        help="Set the custom command to run for an already registered project",
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
        init_logging(log_file=LOG_FILE)
        paths = configreader.read_mapping_file(PATHS_DIR)
        parser = configure_cli_args()

        command = CommandFactory.create_command(parser, paths, PATHS_DIR)
        exit_code = command.execute()

        return exit_code

    # pylint: disable-next=broad-exception-caught
    except Exception as e:
        logger.exception("Unhandled exception")
        print(f"An error occurred: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
