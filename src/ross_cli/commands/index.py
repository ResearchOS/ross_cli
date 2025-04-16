import os
from pprint import pprint
import subprocess
import base64

import tomli
import tomli_w
import typer

from ..constants import *
from ..git.github import get_remote_url_from_git_repo, read_github_file
from ..utils.config import load_config
from ..utils.rossproject import load_rossproject

def print(index_file_path: str) -> None:
    """Print the index file."""
    if not os.path.exists(index_file_path):
        typer.echo(f"File {index_file_path} does not exist.")
    
    with open(index_file_path, "rb") as f:
        pprint(tomli.load(f))  # Use pprint to print the loaded TOML file
    
def add_to_index(index_file_url: str, package_folder_path: str) -> None:
    """Add the specified package to the specified index.
    1. Register the package with the .toml file living in the user's home directory. Throw error if file does not exist.
    - Locate the .toml file (default: ~/.ross/indices/index1.toml)
    - Get the remote URLs from the git repository (fail if folder is not a git repo, and error if 0 or 2+ remotes exist)
    - Add the package to the .toml file (error if it already exists)"""
    # Check if the package folder is a git repository
    if not os.path.exists(os.path.join(package_folder_path, ".git")):
        typer.echo(f"Folder {package_folder_path} is not a git repository.")
        raise typer.Exit()
    
    # Check for the rossproject.toml file
    if not os.path.exists(DEFAULT_ROSSPROJECT_TOML_PATH):
        typer.echo(f"Folder {package_folder_path} is missing a rossproject.toml file")
        raise typer.Exit()
    
    config = load_config()

    if "index" not in config or len(config["index"]) == 0:
        typer.echo(f"No indexes found in the config file.")
        raise typer.Exit()    

    # Get the package name from the rossproject.toml file
    rossproject_toml_path = os.path.join(package_folder_path, "rossproject.toml")
    rossproject_content = load_rossproject(rossproject_toml_path)
    package_name = rossproject_content["name"]
    
    # Get the remote URL from the git repository
    remote_url = get_remote_url_from_git_repo(package_folder_path)

    # Download the content of the index.toml file directly from GitHub.
    index_content = tomli.loads(read_github_file(index_file_url))

    if "package" not in index_content:
        index_content["package"] = []

    # Check if the package is already in the index
    for package in index_content["package"]:
        if remote_url == package["url"]:    
            typer.echo(f"Package {package_name} already exists in the index.")    
            raise typer.Exit(2)    
    
    # Add the package to the index
    index_content["package"].append(
        {
            "name": package_name,
            "url": remote_url
        }
    )

    # Configuration
    index_file_url_no_https = index_file_url.replace("https://", "").replace("/blob/main", "")
    parts = index_file_url_no_https.split("/")
    username = parts[1]
    repo = parts[2]
    file_path = '/'.join(parts[3:])
    new_content = tomli_w.dumps(index_content)
    commit_message = f"Update {file_path}"

    # Step 1: Get the SHA of the current file
    get_sha_cmd = ["gh", "api", f"repos/{username}/{repo}/contents/{file_path}", "-q", ".sha"]
    sha_result = subprocess.run(get_sha_cmd, check=True, capture_output=True, text=True)
    file_sha = sha_result.stdout.strip()

    # Step 2: Encode the new content to base64
    encoded_content = base64.b64encode(new_content.encode()).decode()

    # Step 3: Update the file
    update_cmd = [
        "gh", "api",
        "--method", "PUT",
        f"repos/{username}/{repo}/contents/{file_path}",
        "-f", f"message={commit_message}",
        "-f", f"content={encoded_content}",
        "-f", f"sha={file_sha}"
    ]

    update_result = subprocess.run(update_cmd, check=True, capture_output=True, text=True)

    typer.echo(f"Successfully added package {package_name} to index at {index_file_url}")