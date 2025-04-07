import os

import tomli

# Create the default configuration content
default_ross_config_content_str = f"""
# Ross default configuration
[general]
log = "info"

[[index]]
"""
DEFAULT_ROSS_CONFIG_CONTENT = tomli.loads(default_ross_config_content_str)  # Parse the TOML content
del default_ross_config_content_str # Delete the default_ross_config_content_str variable to keep the namespace clean

# Constants for file paths
DEFAULT_ROSS_ROOT_FOLDER = os.path.join(os.path.expanduser("~"), ".ross")
DEFAULT_ROSS_INDICES_FOLDER = os.path.join(DEFAULT_ROSS_ROOT_FOLDER, "indices")
DEFAULT_ROSS_CONFIG_FILE_PATH = os.path.join(os.path.expanduser("~"), ".ross", "ross_config.toml")
DEFAULT_INSTALL_FOLDER_PATH = os.path.join(os.getcwd(), "src")
DEFAULT_PYPROJECT_TOML_PATH = os.path.join(os.getcwd(), "pyproject.toml")

