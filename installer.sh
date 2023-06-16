#!/bin/bash

SCRIPTS_DIR="/home/"
VENV_NAME="venv"
ACTIVATE_VENV="source ${SCRIPTS_DIR}/${VENV_NAME}/bin/activate"

function setup_python_venv() {
    python3 -m venv "${SCRIPTS_DIR}/${VENV_NAME}"
    ${ACTIVATE_VENV}
    pip3 install -r "${SCRIPTS_DIR}/requirements.txt"
}

function add_alias() {
    local main="$1"
    echo "alias ${main}='${ACTIVATE_VENV} | python3 ${SCRIPTS_DIR}/${main}/${main}.py'" >> ~/.bash_aliases
}

setup_python_venv
add_alias "open"
add_alias "cheatsheet"

