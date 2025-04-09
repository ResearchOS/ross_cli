# Overview
`ross` (Research Open Source Software) is a command-line interface (CLI) for installing and sharing data science projects written in any programming language. `ross` is built on top of `pip`, `git`, and `github`, and is designed to be easy to use and flexible.

Each project/package's metadata is stored in a `rossproject.toml` text file, which is a stripped-down version of the `pyproject.toml` file used by `pip`. This file contains information about the project, such as its name, version, author, and dependencies.

# Dependencies
- Python
- Git CLI
- GitHub account
- `gh` CLI (optional, for releasing packages)

# Installation
## Cross-platform
Using `pip`, either in the global Python environment or in a project-specific virtual environment:
```bash
# Optional
cd /path/to/preferred/installation/folder
```

```bash
pip install git+https://github.com/ResearchOS/ross_cli.git
ross cli-init
```

## Linux/MacOS
### Using Homebrew (recommended)
```bash
brew tap ResearchOS/ross_cli https://github.com/ResearchOS/ross_cli
brew install ross_cli
ross cli-init
```

### Manually
```bash
# Navigate to where on your computer you want to install the package
# e.g. ~/ross_cli
cd /path/to/preferred/installation/folder

# Clone this repository to that folder
git clone https://github.com/ResearchOS/ross_cli.git

# Add the `ross` CLI to your shell's rc file (e.g. ~/.bashrc, ~/.zshrc, ~/.bash_profile, etc.)
echo 'export PATH="$PATH:/path/to/ross_cli"' >> ~/.bashrc
source ~/.bashrc

# Initialize the CLI
ross cli-init
```

# Create a new project
```bash
cd /path/to/your/project/folder
ross init
```
Creates the `rossproject.toml` file in the current directory, and creates a minimal project folder structure.

# Tap an index
Before installing any packages, you need to `tap` (add) an index to tell `ross` where it should be looking for packages. Indexes are GitHub repositories owned by you or someone else that contain an `index.toml` file. This file contains a list of package names & URL's.
```bash
ross tap https://github.com/github_user/github_repo
```
This clones the repo to your computer at `~/.ross/indexes/github_user/github_repo` and creates an `index.toml` file in that directory, if it doesn't already exist.

## Create an index
An index is just a GitHub repository. You can create one by [going to GitHub's website and creating a new repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/quickstart-for-repositories). 

It is OK if the repository is empty - `ross` will create the `index.toml` file for you.

## Example index.toml
```toml
[[package]]
url = "https://github.com/example_user/example_package"
```

# Install a package
```bash
ross install example_package
```
This will search through all of the tapped indexes for the package name, and `pip install --editable git+<url>` the package. Installing a package in editable mode allows you to have just as much control over the packages you install as if you had written it yourself.

# Release a package (optional, requires `gh` CLI)
```bash
ross release v#.#.#
```
This will create a new release of the package using the `gh` CLI. The version number should be in the format `v#.#.#`, e.g. `v0.1.0`. This will use the information from the `rossproject.toml` file to update the `pyproject.toml` file, and create a new release on GitHub.

## rossproject.toml format for releases
To release a package, you need to have a `rossproject.toml` file in the root of your package's repository. This file should contain the following information:
```toml
name = "example_package"
version = "0.1.0"
description = "A short description of the package"
language = "python"
authors = [
    "Author1",
    "Author2"
]
dependencies = [
    "numpy",
    "pandas",
    "my_other_package"
]
```
This gets converted to [a standard `pyproject.toml` file](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#a-full-example) when you `ross release` the package.

# Add your package to an index
After your package's repository has at least one release, you can add it to an index of your choice. This will allow other users to `ross install` your package.
```bash
ross add-to-index github_user/github_repo
```
This command adds the package in the current folder to the `index.toml` file in `github_user/github_repo`. It will then `git push` the changes to the remote repository.

# ROSS Configuration File Format
```toml
[general]
log = "info"

[[index]]
path = "/Users/username/.ross/indexes/ResearchOS/ross_cli/index.toml"
```