import uuid

import tomli_w
import typer

from ..constants import *
from ..utils.config import load_config, validate_index_entries
from .release import is_valid_url
from ..git.github import get_default_branch_name, create_empty_file_in_repo, parse_github_url
from ..utils.urls import check_url_exists

def tap_github_repo_for_ross_index(remote_url: str, index_relative_path = "index.toml",
                                   _config_file_path = DEFAULT_ROSS_CONFIG_FILE_PATH):
    f"""Add a GitHub repository as a ROSS index.
    Puts the repository following information into {DEFAULT_ROSS_CONFIG_FILE_PATH}
    1. "url": Repository URL (ending with .git)
    2. "uuid": Tapped index UUID
    3. "index_path": Relative path to the index.toml file within the repository (default: index.toml)
    """
    ross_config = load_config(_config_file_path)

    # Initialize the index key
    if "index" not in ross_config:
        ross_config["index"] = []

    validate_index_entries(ross_config["index"])

    owner, repo, file_path = parse_github_url(remote_url)
    remote_url = f"https://github.com/{owner}/{repo}.git"

    # Check that this URL exists.
    if not is_valid_url(remote_url):
        typer.echo(f"URL does not exist or could not be reached: {remote_url}")
        raise typer.Exit()
    
    # Check if the index file path already exists in the config file        
    for index in ross_config["index"]:
        if remote_url == index["url"]:
            typer.echo(f"Aborting. Index file already exists in ROSS config file")
            raise typer.Exit()
        
    # Create the dict for this index
    index_dict = {
        "url": remote_url,
        "uuid": str(uuid.uuid4()),
        "index_path": index_relative_path
    }
    ross_config["index"].append(index_dict)

    # Create the index.toml file if it does not exist already.
    # 1. Query GitHub to see if the index.toml file exists.
    # 2. If so, do nothing.
    # 3. If not, create it.
    remote_url_no_git = remote_url.replace(".git", "")
    branch_name = get_default_branch_name(remote_url)    
    index_toml_url = remote_url_no_git + f"/blob/{branch_name}/index.toml"
    if not check_url_exists(index_toml_url):
        typer.echo(f"index file not found, attempting to create index file at: {index_toml_url}")
        try:
            create_empty_file_in_repo(remote_url, index_relative_path)
        except:
            typer.echo(f"Failed to create index.toml file. Please create the file manually at: {remote_url_no_git}")
            raise typer.Exit()

    # Write the ross config file    
    with open(_config_file_path, "wb") as f:
        tomli_w.dump(ross_config, f)
    
    typer.echo(f"Successfully tapped GitHub repository: {remote_url}")

def untap_ross_index(remote_url: str, _config_file_path = DEFAULT_ROSS_CONFIG_FILE_PATH):
    """Remove the GitHub repository from the ROSS index. Also remove the index folder from the .ross/indexes folder"""
    ross_config_toml = load_config(_config_file_path)

    # Ensure "index" field is initialized
    if "index" not in ross_config_toml:
        ross_config_toml["index"] = []

    typer.echo("Index:")
    typer.echo(ross_config_toml["index"])

    # Check that there are indexes to untap
    if len(ross_config_toml["index"]) == 0:
        typer.echo("No indexes present in the config file. Aborting untap...")
        raise typer.Exit()
    
    owner, repo, file_path = parse_github_url(remote_url)
    remote_url = f"https://github.com/{owner}/{repo}.git"

    validate_index_entries(ross_config_toml["index"])

    # Remove this index from the list
    found_in_index = False
    for index in ross_config_toml["index"]:
        if index["url"] == remote_url:            
            ross_config_toml["index"].remove(index)      
            found_in_index = True      
            break

    if not found_in_index:
        typer.echo(f"Aborting. Index file not found in ROSS config file")
        raise typer.Exit()

    # Save the modified config file
    with open(_config_file_path, 'wb') as f:
        tomli_w.dump(ross_config_toml, f)

    typer.echo(f"Successfully untapped: {remote_url}")    