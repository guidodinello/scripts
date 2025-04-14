[![Pipeline](https://github.com/guidodinello/scripts/actions/workflows/pipeline.yaml/badge.svg)](https://github.com/guidodinello/scripts/actions/workflows/pipeline.yaml)

### Description

Collection of useful scripts that I made to automate various tasks.

### Installation

You can install the scripts using the Makefile:

```bash
# Basic installation
make install

# Installation with development tools
make install-dev

# Installation with Rust extensions (better performance)
make install-rust

# Full installation with development tools and Rust extensions
make install-dev-rust
```

After installation, you can set up shell aliases and completions:

```bash
make setup
```

This will add aliases to your shell configuration file (`.bashrc` or `.zshrc`) and create shell completions for better command-line experience. You'll need to run `source ~/.bashrc` (or `source ~/.zshrc`) after setup to apply the changes.

The setup creates aliases for each script, allowing you to call them from anywhere in the terminal:

```bash
open <project_key>
cheatsheet <cheatsheet_name>
organize
```

### Available Scripts

- **open**: Quickly navigate to your projects with file manager and VS Code
- **cheatsheet**: Access your markdown cheatsheets with fuzzy matching
- **organize**: Command-line utilities for organizing files

### Development

If you want to contribute to this project, you can do so by forking the repository and creating a pull request.

You can set up the development environment with:

```bash
make install-dev
```

This will install all development dependencies and set up pre-commit hooks.

To run the tests:

```bash
make test
```

For code quality checks:

```bash
make lint
make format
```

### Performance with Rust

For better performance, you can use the Rust implementation of the fuzzy string matcher:

```bash
make install-rust
```

To verify that the Rust module is properly installed:

```bash
make check-rust
```

### Future Improvements

- [ ] Allow the user to add some custom command to the open script (and persist it). For instance, if some project needs to spin up a database docker container, that would be useful.
- [ ] Add more comprehensive logging
- [ ] Implement unit testing
- [ ] Add more scripts
