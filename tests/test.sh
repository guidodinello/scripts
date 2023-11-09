#!/bin/bash

PY_VERSION="312"
LINE_LENGTH="80"

echo "Black formatting..."
black -t "py${PY_VERSION}" -l "${LINE_LENGTH}" --exclude venv/ */*.py
echo "Running mypy..."
mypy */*.py --exclude venv/ --disable-error-code no-redef
echo "Running pylint..."
pylint */*.py \
    --exit-zero \
    --max-line-length=${LINE_LENGTH} \
    --disable=missing-function-docstring \
    --disable=missing-module-docstring \
    --ignore-patterns venv/
