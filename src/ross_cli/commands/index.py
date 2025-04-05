import os
import tomli
from pprint import pprint

from ..constants import *

def print(index_file_path: str) -> None:
    """Print the index file."""
    if not os.path.exists(index_file_path):
        raise ValueError(f"File {index_file_path} does not exist.")
    
    with open(index_file_path, "rb") as f:
        pprint(tomli.load(f))  # Use pprint to print the loaded TOML file

def locate(ross_config_file_path: str = DEFAULT_ROSS_CONFIG_FILE_PATH) -> str:
    """Read the config file path to located the index file."""
    if not os.path.exists(ross_config_file_path):
        raise ValueError(f"File {ross_config_file_path} does not exist.")
    
    with open(ross_config_file_path, "rb") as f:
        toml_file = tomli.load(f)
        index_file_path = toml_file["index"]["file"]
        return index_file_path