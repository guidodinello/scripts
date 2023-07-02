import os
import signal
import subprocess
import sys
from argparse import ArgumentParser

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import configreader  # pylint: disable=C0413

PATHS_DIR = os.path.join(os.path.dirname(__file__), "paths.txt")

if __name__ == "__main__":
    parser = ArgumentParser()
    mutex_group = parser.add_mutually_exclusive_group(required=True)

    mutex_group.add_argument("project_name", nargs="?")
    mutex_group.add_argument("--relative_path", "--rp")
    mutex_group.add_argument(
        "--add_entry", "--ae", nargs=2, metavar=("key", "abs_path")
    )

    args = parser.parse_args()

    PATHS = configreader.read_mapping_file(PATHS_DIR)

    project = args.project_name
    if project is None:
        key, abs_path = args.add_entry
        PATHS[key] = abs_path
        configreader.add_to_mapping_file({key: abs_path}, PATHS_DIR)
    else:
        project = project.lower()

        if project not in PATHS:
            msg = f"Theres no project registered for the name: {project} \n"
            msg += "Supported projects are: \n"
            for k in PATHS:
                msg += f"\t* {k}\n"
            print(msg)
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
