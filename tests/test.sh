FILE_PATTERN="*/*.py"
PY_VERSION="311"
LINE_LENGTH="80"

black -t py${PY_VERSION} -l ${LINE_LENGTH} ${FILE_PATTERN}
mypy ${FILE_PATTERN}
pylint ${FILE_PATTERN} \
    --exit-zero \
    --max-line-length=${LINE_LENGTH} \
    --disable=missing-docstring