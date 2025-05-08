import os
import subprocess
from urllib.parse import urlparse

import tomli
import typer

from .github import get_remote_url_from_git_repo, is_valid_url, read_github_file_from_release, parse_github_url
from ..constants import DEFAULT_ROSS_CONFIG_FILE_PATH
from ..utils.config import load_config

def get_indexes_info_from_config(config_file_path: str = DEFAULT_ROSS_CONFIG_FILE_PATH):
    """Get the index files' info from the config file."""
        
    toml_content = load_config(config_file_path)  
    if "index" not in toml_content:
        return None
    else:
        return toml_content["index"]

def search_indexes_for_package_info(package_identifier: str, config_file_path: str = DEFAULT_ROSS_CONFIG_FILE_PATH) -> str:
    """Get the package's information (dict) given an identifier.
    Identifier can be any of: package name, GitHub `owner/repo` string, or GitHub repository URL.
    If more than one package is identified, returns all of them.
    If none are identified, returns None."""
    
    indexes = get_indexes_info_from_config(config_file_path)

    id_type = "package name"
    if is_valid_url(package_identifier):
        # Convert to owner/repo to make sure the URL is properly specified.
        owner, repo, _ = parse_github_url(package_identifier)
        id_type = "owner/repo"
        package_identifier = f"{owner}/{repo}"
    elif "/" in package_identifier:
        id_type = "owner/repo"    
    
    for index in indexes:
        index_file_url = index["url"][0:-4] + "/" + index["index_path"]
        index_content = tomli.loads(read_github_file_from_release(index_file_url))

        if "package" not in index_content:
            continue
    
        for package in index_content["package"]:
            if id_type == "package name":
                if package["name"] == package_identifier:
                    return package
            else:
                package_url = f"https://github.com/{package_identifier}.git"
                if package["url"] == package_url:
                    return package
    return None
    

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

    packages = toml_content["package"]
    for package in packages:
        if package_name in package["url"]:
            return package["url"]
    
    typer.echo(f"{package_name} not found in {index_file_path}")
    return None