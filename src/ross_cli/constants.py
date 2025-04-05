import os

import tomli

# Create the default configuration content
# Use os.path.join for cross-platform compatibility
default_ross_config_content_str = f"""
[[index]]
name = "default"
path = "{os.path.join(os.path.expanduser('~'), '.ross', 'indices', 'default_index.toml')}"
"""
DEFAULT_ROSS_CONFIG_CONTENT = tomli.loads(default_ross_config_content_str)  # Parse the TOML content
del default_ross_config_content_str # Delete the default_ross_config_content_str variable to keep the namespace clean

# Constants for file paths
DEFAULT_INDEX_FILE_PATH = DEFAULT_ROSS_CONFIG_CONTENT["index"][0]["path"]
DEFAULT_ROSS_CONFIG_FILE_PATH = os.path.join(os.path.expanduser("~"), ".ross", "ross_config.toml")
DEFAULT_INSTALL_FOLDER_PATH = os.path.join(os.getcwd(), "src")
DEFAULT_PYPROJECT_TOML_PATH = os.path.join(os.getcwd(), "pyproject.toml")

