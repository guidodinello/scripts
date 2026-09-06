from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ProjectEntry:
    """A registered project: its path and an optional command to run
    alongside opening it (e.g. spinning up a docker container)."""

    path: Path
    command: str | None = None


def read_mapping_file(abs_path: str) -> dict[str, ProjectEntry]:
    """Reads a mapping file in the format of key=path[=command] and returns
    a dict. lines starting with # or empty lines are ignored
    Args:
        abs_path (str): absolute path to the file
    Returns:
        dict[str, ProjectEntry]: a dict with key as the key and the parsed
            path/command as the value
    """
    mapping = {}
    with open(abs_path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            path, _, command = value.partition("=")
            mapping[key] = ProjectEntry(Path(path), command or None)
    return mapping


def add_to_mapping_file(new_entries: dict[str, ProjectEntry], abs_path: str) -> None:
    """Adds new entries to the mapping file.
    This means appending to the mapping file. Registering a key that
    already exists appends a new line for it; since the mapping is read
    top-to-bottom, the last line for a key wins.
    Args:
        new_entries (dict[str, ProjectEntry]): new key/entry pairs to add to
            the mapping file
        abs_path (str): absolute path to the mapping file
    """
    with open(abs_path, "a", encoding="utf-8") as file:
        for key, entry in new_entries.items():
            line = f"{key}={entry.path}"
            if entry.command:
                line += f"={entry.command}"
            file.write(line + "\n")


def remove_form_mapping_file(
    to_remove_entries: Iterable[str],
    abs_path: str,
) -> None:
    """Removes entries from the mapping file. This implies reading the file,
    removing the entries and writing the file again.
    Args:
        to_remove_entries (Iterable[str]): _description_
        abs_path (str): _description_
    """
    with open(abs_path, encoding="utf-8") as file:
        lines = file.readlines()
    with open(abs_path, "w", encoding="utf-8") as file:
        for line in lines:
            line = line.strip()
            if line.startswith("#") or line == "":
                file.write(line)
            else:
                key = line.split("=")[0]
                if key not in to_remove_entries:
                    file.write(line)
