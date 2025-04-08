import os

RELEASE_TYPES = ["patch", "minor", "major"]

DEFAULT_PACKAGE_NAME = "template"

# rossproject.toml default content
DEFAULT_ROSSPROJECT_TOML_STR = """
# ROSS project configuration file
name = "{DEFAULT_PACKAGE_NAME}"
description = "A template for ROSS packages"
version = "0.1.0"
repository_url = "{repository_url}"
language = "python"
authors = [

]
dependencies = [

]
"""

# ~/.ross/ross_config.toml default configuration content 
DEFAULT_ROSS_CONFIG_CONTENT = {
    "about": "ROSS (https://github.com/ResearchOS/ross_cli) configuration file",
    "general": {
        "log": "info"
    }
}

# Constants for file paths
PROJECT_FOLDER = os.getcwd()
DEFAULT_ROSS_ROOT_FOLDER = os.path.join(os.path.expanduser("~"), ".ross")
DEFAULT_ROSS_INDICES_FOLDER = os.path.join(DEFAULT_ROSS_ROOT_FOLDER, "indexes")
DEFAULT_ROSS_CONFIG_FILE_PATH = os.path.join(DEFAULT_ROSS_ROOT_FOLDER, "ross_config.toml")
DEFAULT_PIP_SRC_FOLDER_PATH = os.path.join(PROJECT_FOLDER, "src")
DEFAULT_PYPROJECT_TOML_PATH = os.path.join(PROJECT_FOLDER, "pyproject.toml")
DEFAULT_ROSSPROJECT_TOML_PATH = os.path.join(PROJECT_FOLDER, "rossproject.toml")

# Paths to initialize the ROSS project
# Don't include the pyproject.toml or rossproject.toml files here
INIT_PATHS = {
    "README.md": os.path.join(PROJECT_FOLDER, "README.md"),
    "src/": os.path.join(PROJECT_FOLDER, "src"),
    "tests/": os.path.join(PROJECT_FOLDER, "tests"),
    "docs/": os.path.join(PROJECT_FOLDER, "docs"),
    ".gitignore": os.path.join(PROJECT_FOLDER, ".gitignore")
}
