import os

POSSIBLE_VERSION_CHARS = "=<>!~[@"  

REQUIRED_INDEX_KEYS = ["url", "index_path"] # The keys in the config file for each index.

CLI_NAME = "ross" # The name of this package

SUPPORTED_LANGUAGES = ['python', 'r', 'matlab']

BLOB_BRANCH_REGEX = r'/?blob/[^/]+' # Matches "/blob/branch_name" or "blob/branch_name" (if no leading "/") in a URL
SEMANTIC_VERSIONING_REGEX = r".*?v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"

RELEASE_TYPES = ["patch", "minor", "major"]

DEFAULT_PACKAGE_NAME = "template"

ROSSPROJECT_REQUIRED_FIELDS = [
    "name",    
    "version",
    "repository_url",
    "language",
    "authors",
    "dependencies",
    "readme"
]

# rossproject.toml default content
DEFAULT_ROSSPROJECT_TOML_STR = """
# ROSS project configuration file
name = "{DEFAULT_PACKAGE_NAME}"
version = "0.1.0"
language = "python"
authors = [

]
dependencies = [

]
readme = "README.md"
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
DEFAULT_PIP_SRC_FOLDER_PATH = os.path.join("src", "site-packages")
DEFAULT_PYPROJECT_TOML_PATH = os.path.join(PROJECT_FOLDER, "pyproject.toml")
DEFAULT_ROSSPROJECT_TOML_PATH = os.path.join(PROJECT_FOLDER, "rossproject.toml")

# Paths to initialize the ROSS project
# Don't include the pyproject.toml or rossproject.toml files here
INIT_PATHS = {
    "README.md": "README.md",
    "src/": "src",
    "src/installed/": "src/site-packages",
    "tests/": "tests",
    "docs/": "docs",
    ".gitignore": ".gitignore"    
}
