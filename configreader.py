from pathlib import Path

def read_mapping_file(abs_path: str) -> dict[str, Path]:
    mapping = {}
    with open(abs_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            # if line is empty or starts with #, ignore it
            if line == "" or line.startswith('#'):
                continue
            key, value = line.split('=')
            mapping[key] = Path(value)
    return mapping
