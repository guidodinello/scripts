#!/bin/bash

USE_RUST=0
SCRIPTS_DIR="${HOME}/scripts"
VENV_NAME=".venv"
ACTIVATE_VENV="source ${SCRIPTS_DIR}/${VENV_NAME}/bin/activate"

supported_scripts=("open" "cheatsheet")

function setup_python_venv() {
    python -m venv "${SCRIPTS_DIR}/${VENV_NAME}" ||
        (echo "Error: Could not create virtual environment" && exit 1)
    ${ACTIVATE_VENV}
    python -m pip install --upgrade pip
    pip3 install -r "${SCRIPTS_DIR}/requirements.txt"
    pip3 install -e ./utils
}

function add_alias() {
    local script="$1"
    echo "Adding alias for ${script}"
    echo "alias ${script}='${ACTIVATE_VENV} && python ${SCRIPTS_DIR}/${script}/${script}.py'" >>~/.bash_aliases
}

function install_scripts() {
    for script in "$@"; do
        # if script not in supported scripts list, skip it
        if [[ ! "${supported_scripts[*]}" =~ ${script} ]]; then
            echo "Script ${script} not supported"
            continue
        fi
        # if alias already exists in .bash_asliases, skip it.
        if grep -q "alias ${script}" ~/.bash_aliases; then
            echo "Alias for ${script} already exists"
            continue
        fi
        add_alias "${script}"
    done
}

if [ ! -d "${SCRIPTS_DIR}/${VENV_NAME}" ]; then
    if [ "${USE_RUST}" -eq 1 ]; then
        cd "${SCRIPTS_DIR}/rust_utils/fuzzy_string_matcher" ||
            (echo "Error: Could not find rust_utils/fuzzy_string_matcher" && exit 1)
        maturin develop --release --strip
    fi
    setup_python_venv

    git_hooks_setup_script="./tests/setup_hooks.sh"
    chmod +x "${git_hooks_setup_script}"
    "${git_hooks_setup_script}"
fi
# if not arguments provided install all supported scripts
# else install only the provided scripts
if [ $# -eq 0 ]; then
    install_scripts "${supported_scripts[@]}"
else
    install_scripts "$@"
fi
