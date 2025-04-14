#!/bin/bash
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
supported_scripts=("open" "cheatsheet" "organize")
# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

function shell_config_file() {
    USER_SHELL=$(basename "$SHELL")
    local config_file
    case "$USER_SHELL" in
    zsh)
        config_file="${HOME}/.zshrc"
        echo -e "${GREEN}Detected zsh shell${NC}" >&2
        ;;
    bash)
        config_file="${HOME}/.bashrc"
        echo -e "${GREEN}Detected bash shell${NC}" >&2
        ;;
    *)
        config_file="${HOME}/.bashrc"
        echo -e "${YELLOW}Unrecognized shell ${USER_SHELL}, defaulting to bash configuration${NC}" >&2
        ;;
    esac
    echo "$config_file"
}

function add_alias() {
    local script="$1"
    local shell_config="$2"
    # Check if alias already exists
    if grep -q "alias ${script}=" "${shell_config}"; then
        echo -e "${YELLOW}Alias for ${script} already exists in ${shell_config}${NC}"
        return
    fi
    echo -e "${GREEN}Adding alias for ${script} to ${shell_config}${NC}"
    echo "alias ${script}='cd ${SCRIPTS_DIR} && poetry run python ${script}/${script}.py'" >>"${shell_config}"
}

function setup_aliases() {
    local shell_config="$1"
    shift
    for script in "$@"; do
        add_alias "$script" "$shell_config"
    done
}

# Get shell config file
SHELL_CONFIG=$(shell_config_file)
echo -e "${BLUE}Setting up aliases in ${SHELL_CONFIG}${NC}"

setup_aliases "$SHELL_CONFIG" "${supported_scripts[@]}"
echo -e "${GREEN}Alias setup complete. Please run 'source ${SHELL_CONFIG}' to apply changes.${NC}"
