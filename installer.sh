#!/bin/bash

USE_RUST=1
SCRIPTS_DIR="${HOME}/scripts/Python/automater"
VENV_NAME="venv"
ACTIVATE_VENV="source ${SCRIPTS_DIR}/${VENV_NAME}/bin/activate"

supported_scripts=("open" "cheatsheet")

function setup_python_venv() {
    python3 -m venv "${SCRIPTS_DIR}/${VENV_NAME}"
    ${ACTIVATE_VENV}
    python3 -m pip install --upgrade pip
    pip3 install -r "${SCRIPTS_DIR}/requirements.txt"
    pip3 install utils/
}

function add_alias() {
    local script="$1"
    echo "alias ${script}='${ACTIVATE_VENV} | python3 ${SCRIPTS_DIR}/${script}/${script}.py'" >> ~/.bash_aliases
}

function install_scripts() {
    for script in "$@"; do
        # if script not in supported scripts list, skip it
        if [[ ! " ${supported_scripts[@]} " =~ " ${script} " ]]; then
            echo "Script ${script} not supported"
            continue
        else
            add_alias "${script}"
        fi
    done
}


if [ ! -d "${SCRIPTS_DIR}/${VENV_NAME}" ]; then
    setup_python_venv
    if [ "${USE_RUST}" -eq 1 ]; then
            cd "${SCRIPTS_DIR}/rust_utils/fuzzy_string_matcher"
            maturin develop --release --strip
    fi
fi
# if not arguments provided install all supported scripts
# else install only the provided scripts
if [ $# -eq 0 ]; then
    install_scripts "${supported_scripts[@]}"
else
    install_scripts "$@"
fi

