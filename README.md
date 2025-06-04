# Overview
`ross` (Research Open Source Software) is a command-line interface (CLI) for installing and sharing data science projects written in Python, MATLAB, and R. `ross` is built on top of `pip`, `git`, and `github` (via `gh` cli), and is designed with researchers in mind to be easy to use and flexible.

Each project/package's metadata is stored in a `rossproject.toml` text file, which is a stripped-down version of the `pyproject.toml` file used by `pip`. This file contains information about the project, such as its name, version, author, and dependencies.

# Dependencies
- Python
- Git CLI
- GitHub account
- `gh` CLI

# Cross-Platform Installation Using `pip`
`ross` is recommended to be installed in a project-specific virtual environment.

1. Navigate to the project directory. Make sure you have an active virtual environment.
```bash
# Navigate to the project directory or other preferred installation location
cd /path/to/your/project/folder

# Create a virtual environment if one does not already exist.
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate # MacOS/POSIX (bash/zsh)
.venv\Scripts\activate.bat # Windows command prompt
.venv\Scripts\Activate.ps1 # Windows PowerShell
```

2. Install and initialize the `ross-cli` package.
```bash
pip install ross-cli
ross cli-init
```

# Create a new project
```bash
cd /path/to/your/project/folder
ross init
```
Creates the `rossproject.toml` file in the current directory, and creates a minimal project folder structure.

# Tap an index
Before installing any packages, you need to `tap` (add) an existing index to tell `ross` where it should be looking for packages. Indexes are GitHub repositories owned by you or someone else that contain an `index.toml` file. This file contains a list of package names & URL's.

This adds the index repository's URL to your configuration file.
```bash
ross tap https://github.com/github_user/github_repo
```

## Create an index
An index is just a GitHub repository (hosted by GitHub in the cloud). You can create one following your preferred method, or by [going to GitHub's website and creating a new repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository#creating-a-new-repository-from-the-web-ui). 

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

## Installing MATLAB and R packages
`pip install` is a native Python command. For MATLAB and R, the appropriate installation commands are executed - `git clone`, and `install.packages()` (if on CRAN), respectively.

# Release a package (for code authors)
`ross` relies on GitHub releases tagged with [semantic versioning](https://semver.org) to ensure reproducibility.
```bash
ross release patch # Increment v0.0.1
ross release minor # Increment v0.1.0
ross release major # Increment v1.0.0
```
This will create a new release of the package using the `gh` CLI. The version number should be in the format `v#.#.#`, e.g. `v0.1.0` or `v3.12.14`. This will use the information from the `rossproject.toml` file to update the `pyproject.toml` file, and create a new release on GitHub.

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

## Possible `rossproject.toml` Dependency Input & Install Options
Dependencies in the `pyproject.toml` `project.dependencies` field are of the format "package-name @ git+URL@tag". Dependencies in the `project.tool.ross.dependencies` field are of the format "https://github.com/{owner}/{repo}/blob/{tag}".
![ROSSProject Specs](docs/images/rossproject%20specs.png)

# Add your package to an index
After your package's repository has at least one release, you can add it to an index of your choice. This will allow other users to `ross install` your package.
```bash
ross add-to-index https://github.com/username/repo/index.toml
```
This command adds the specified package in the current folder to the specified `index.toml` file in the GitHub repository. You must have write access to that index repository to do this.

# ROSS Configuration File Format
This file is stored locally on your machine at `~/.ross/ross_config.toml` (Mac) or `C:\Program Files\ROSS\ross_config.toml` (Windows). Currently, this file simply contains the list of indexes that are known (tapped) to `ross`.
```toml
[[index]]
url = "https://github.com/username/repo.git" # URL of the GitHub repository.
index_path = "index.toml" # The location of the index.toml file in the repository.
```