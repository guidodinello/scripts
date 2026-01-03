.PHONY: all help install install-dev lint format test precommit clean rust-build setup

all: help

help:
	@echo "Available commands:"
	@echo "  make install        - Install the package with Rust extension"
	@echo "  make install-dev    - Install the package with dev dependencies"
	@echo "  make rust-build     - Rebuild Rust extension (for development)"
	@echo "  make lint           - Run all linters (ruff, mypy, pylint)"
	@echo "  make format         - Format code with black"
	@echo "  make test           - Run tests with pytest"
	@echo "  make precommit      - Run pre-commit on all files"
	@echo "  make clean          - Clean up build artifacts"

install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev]"
	pre-commit install

setup:
	@chmod +x ./setup.sh
	@./setup.sh

lint:
	python -m ruff check .
	python -m mypy .
	python -m pylint cheatsheet open organize utils --max-line-length=120 \
		--disable=missing-function-docstring,missing-module-docstring,missing-class-docstring,too-few-public-methods,c-extension-no-member

format:
	python -m black .
	python -m ruff check --fix .

test:
	python -m pytest

precommit:
	pre-commit run --all-files

# Clean up build artifacts
clean:
	rm -rf dist
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build the Rust Python extension
# Note: Regular 'make install' already builds the Rust extension automatically
# This target is useful for quick rebuilds during Rust development
rust-build:
	maturin develop --release
	@echo "Rust extension rebuilt and installed in the current Python environment"
