### Description

Collection of useful scripts that I made to automate various tasks.

### Installation

Call the installation script and you're good to go:
```bash
    chmod +x install.sh
    ./install.sh
```
You can optionally pass the name of the scripts and it will only install those:
```bash
    ./install.sh script1 script2 script3
```
It simply creates a virtual environment inside the automater folder (if it doesn't exist) and pip installs the requirements.
Furthermore, if the rust flag is set to true, it will also compile the rust_utils module and use that instead of the python one.

Finally, the installer adds a bash alias for each script in the .bashrc file. This allows you to call the scripts from anywhere in the terminal.
```bash
open <project_key>
```

#### Future improvements
* 
  
[![Pipeline](https://github.com/guidodinello/scripts/actions/workflows/pipeline.yaml/badge.svg)](https://github.com/guidodinello/scripts/actions/workflows/pipeline.yaml)