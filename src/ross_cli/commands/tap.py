import os
import shutil
import uuid

import tomli
import tomli_w
import typer

from ..constants import *
from ..utils.config import load_config, validate_index_entries
from .release import is_valid_url

def tap_github_repo_for_ross_index(remote_url: str, index_relative_path = "index.toml"):
    f"""Add a GitHub repository as a ROSS index.
    Puts the repository following information into {DEFAULT_ROSS_CONFIG_FILE_PATH}
    1. "url": Repository URL (ending with .git)
    2. "uuid": Tapped index UUID
    3. "index_path": Relative path to the index.toml file within the repository (default: index.toml)
    """
    ross_config = load_config()

    # Initialize the index key
    if "index" not in ross_config:
        ross_config["index"] = []

    validate_index_entries(ross_config["index"])
            
    # Make sure the remote URL ends in .git
    if not remote_url.endswith('.git'):
        remote_url = remote_url + ".git"

    # Check that this URL exists.
    if not is_valid_url(remote_url):
        typer.echo(f"URL does not exist or could not be reached: {remote_url}")
        raise typer.Exit()
    
    # Check if the index file path already exists in the config file        
    for index in ross_config["index"]:
        if remote_url == index["url"]:
            typer.echo(f"Aborting. Index file already exists in ROSS config at:")
            typer.echo(f"{index['path']}")
            raise typer.Exit()
        
    # Create the dict for this index
    index_dict = {
        "url": remote_url,
        "uuid": uuid.uuid4(),
        "index_path": index_relative_path
    }
    ross_config["index"].append(index_dict)

    # Write the ross config file    
    with open(DEFAULT_ROSS_CONFIG_FILE_PATH, "wb") as f:
        tomli_w.dump(ross_config, f)
    
    typer.echo(f"Successfully tapped GitHub repository: {remote_url}")

def untap_ross_index(remote_url: str):
    """Remove the GitHub repository from the ROSS index. Also remove the index folder from the .ross/indexes folder"""
    ross_config_toml = load_config()

    # Ensure "index" field is initialized
    if "index" not in ross_config_toml:
        ross_config_toml["index"] = []

    # Check that there are indexes to untap
    if len(ross_config_toml["index"]) == 0:
        typer.echo("No indexes present in the config file. Aborting untap...")
        raise typer.Exit()
    
    if not remote_url.endswith(".git"):
        remote_url = remote_url + ".git"

    validate_index_entries(ross_config_toml["index"])

    # Remove this index from the list
    for index in ross_config_toml["index"]:
        if index["url"] == remote_url:            
            ross_config_toml["index"].remove(index)            
            break

    # Save the modified config file
    with open(DEFAULT_ROSS_CONFIG_FILE_PATH, 'wb') as f:
        tomli_w.dump(ross_config_toml, f)

    typer.echo(f"Successfully untapped: {remote_url}")    