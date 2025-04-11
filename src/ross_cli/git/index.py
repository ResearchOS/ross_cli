import os
import subprocess

import tomli
import typer

from .github import get_remote_url_from_git_repo
from ..constants import DEFAULT_ROSS_CONFIG_FILE_PATH

def get_index_files_from_config(config_file_path: str = DEFAULT_ROSS_CONFIG_FILE_PATH):
    """Get the index files from the config file."""
    if not os.path.isfile(config_file_path):
        typer.echo(f"{config_file_path} is not a file or does not exist.")
        raise typer.Exit()
    
    with open(config_file_path, "rb") as f:
        toml_content = tomli.load(f)
    
    return toml_content["index"]  # Return the index files from the config file

def get_package_remote_url(package_name: str, config_file_path: str = DEFAULT_ROSS_CONFIG_FILE_PATH) -> str:
    """Get the remote URL from the index file."""
    index_files = get_index_files_from_config(config_file_path)
    typer.echo(index_files)
    for index_file in index_files:
        try:
            remote_url = get_package_remote_url_from_index_file(package_name, index_file["path"])
            return remote_url
        except:
            continue
    typer.echo(f"{package_name} not found in any index file.")
    raise typer.Exit()

def get_package_remote_url_from_index_file(package_name: str, index_file_path: str):
    """Get the remote URL from the index file."""
    if not os.path.isfile(index_file_path):
        typer.echo(f"{index_file_path} is not a file or does not exist.")
        raise typer.Exit()
    
    # Get any updates from GitHub for the index file
    parent_folder = os.path.dirname(index_file_path)
    index_repo_remote_url = get_remote_url_from_git_repo(parent_folder)
    try:
        subprocess.run(["git", "pull", index_repo_remote_url])
    except subprocess.CalledProcessError as e:
        typer.echo(f"Git command failed: {e.stderr.strip()}")
        raise typer.Exit()
    
    with open(index_file_path, "rb") as f:
        toml_content = tomli.load(f)

    for package in toml_content:
        if package_name not in package["url"]:
            typer.echo(f"{package_name} not found in {index_file_path}")
            raise typer.Exit()
    
    return toml_content[package_name]["url"]  # Return the URL associated with the package name