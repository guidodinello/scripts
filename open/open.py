import os
import signal
import subprocess
import sys
from argparse import ArgumentParser

from ..configreader import read_mapping_file

PATHS_DIR=os.path.join(os.path.dirname(__file__), "paths.txt")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("project_name")
    parser.add_argument("--relative_path", "--rp", required=False)

    args = parser.parse_args()
    project = args.project_name.lower()
    
    PATHS = read_mapping_file(PATHS_DIR)

    if project not in PATHS:
        msg = f"Theres no project registered for the name: {project} \n"
        msg += "Supported projects are: \n"
        for k in PATHS:
            msg += f"\t* {k}\n"
        sys.exit(1)

    path_project = PATHS[project]
    if args.relative_path:
        path_project = os.path.join(path_project, args.relative_path)

    # open the file system manager
    subprocess.run(["xdg-open", path_project], check=True)
    # open vscode
    subprocess.run(["code", path_project], check=True)

    # close calling terminal
    os.kill(os.getppid(), signal.SIGHUP)
