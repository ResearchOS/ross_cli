
import typer
import tomli

from ..constants import *

def load_config(config_path: str = DEFAULT_ROSS_CONFIG_FILE_PATH) -> dict:
    """Check for the existence of the config file, and load it."""
    # Check for the existence of the config file    
    if not os.path.exists(config_path):
        typer.echo(f"ROSS config file {config_path} does not exist.")
        raise typer.Exit()
    
    # Read the config file
    with open(config_path, 'rb') as f:
        ross_config = tomli.load(f)

    return ross_config

def validate_index_entries(indexes: list) -> bool:
    """Validate that each index contains all of the required index keys."""
    # Validate the index entries
    for index in indexes:
        for key in REQUIRED_INDEX_KEYS:
            if key not in index:
                typer.echo(f"Missing field: {key} from index in config file at {DEFAULT_ROSS_CONFIG_FILE_PATH}")
                raise typer.Exit()