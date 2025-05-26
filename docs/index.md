# ROSS: Research Open Source Software CLI
`ross` (Research Open Source Software) is a command-line interface (CLI) for installing and sharing data science projects written in Python, MATLAB, and R. `ross` is built on top of `pip`, `git`, and `github` (via `gh` cli), and is designed with researchers in mind to be easy to use and flexible.

Each project/package's metadata is stored in a `rossproject.toml` text file, which is a stripped-down version of the `pyproject.toml` file used by `pip`. This file contains information about the project, such as its name, version, author, and dependencies.

# Dependencies
- Python
- Git CLI
- GitHub account
- `gh` CLI

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

### Manually from GitHub
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
This clones adds the index's URL to your configuration file.

## Create an index
An index is just a GitHub repository (hosted by GitHub in the cloud). You can create one following your preferred method, or by [going to GitHub's website and creating a new repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/quickstart-for-repositories). 

It is OK if the index repository is empty - `ross` will create the `index.toml` file for you.

## index.toml format
This is the format of the `index.toml` file that exists in each ROSS indexed GitHub repository.
```toml
[[package]]
name = "package1_name"
url = "https://github.com/example_user1/example_package1.git"

[[package]]
name = "package2_name"
url = "https://github.com/example_user1/example_package2.git"
```

# Install a package
```bash
ross install package_name
```
This will search through all of the tapped indexes for the package name, and `pip install --editable git+<url>#egg=package_name` the package. By default, each package is installed into `project_folder/src/site-packages/package_name`. Installing a package in editable mode allows you to have just as much control over the packages you install as if you had written it yourself.

### Installing MATLAB and R packages
`pip install` is a native Python command. For MATLAB and R, the appropriate installation commands are executed - `git clone`, and `install.packages()`, respectively.

# Release a package (optional)
```bash
ross release patch # Increment v0.0.1
ross release minor # Increment v0.1.0
ross release major # Increment v1.0.0
```
This will create a new release of the package using the `gh` CLI. The version number should be in the format `v#.#.#`, e.g. `v0.1.0`. This will use the information from the `rossproject.toml` file to update the `pyproject.toml` file, and create a new release on GitHub.

## rossproject.toml format for releases
To release a package, you need to have a `rossproject.toml` file in the root of your package's repository (created during `ross init`). This file must contain the following information:
```toml
name = "example_package"
version = "0.1.0"
language = "python"
authors = [
    "Author 1 Name",
    "Author 2 Name"
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
ross add-to-index https://github.com/username/repo/index.toml
```
This command adds the specified package in the current folder to the specified `index.toml` file in the GitHub repository. You must have write access to that index repository to do this.

# ROSS Configuration File Format
`~/.ross/ross_config.toml`
```toml
[[index]]
url = "https://github.com/username/repo.git" # URL of the GitHub repository.
index_path = "index.toml" # The location of the index.toml file in the repository.
```

## possible rossproject.toml input & install options
![ROSSProject Specs](docs/images/rossproject%20specs.png)