from pathlib import Path
from collections.abc import Iterable


def read_mapping_file(abs_path: str) -> dict[str, Path]:
    """Reads a mapping file in the format of key=value and returns a dict.
    lines starting with # or empty lines are ignored
    Args:
        abs_path (str): absolute path to the file
    Returns:
        dict[str, Path]: a dict with key as the key and value as the value
    """
    mapping = {}
    with open(abs_path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            key, value = line.split("=")
            mapping[key] = Path(value)
    return mapping


def add_to_mapping_file(new_entries: dict[str, str], abs_path: str) -> None:
    """Adds new entries to the mapping file.
    This means appending to the mapping file.
    Args:
        new_entries (Dict[str, str]): new key value pairs to add to the mapping
            file
        abs_path (str): absolute path to the mapping file
    """
    with open(abs_path, "a", encoding="utf-8") as file:
        for key, value in new_entries.items():
            file.write(f"{key}={value}\n")


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
