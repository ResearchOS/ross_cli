import os

import tomli
import subprocess

from .github import get_remote_urls_from_git_repo

def get_package_remote_url_from_index_file(name: str, index_file_path: str):
    """Get the remote URL from the index file."""
    if not os.path.isfile(index_file_path):
        raise FileNotFoundError(f"{index_file_path} is not a file or does not exist.")
    
    # Get any updates from GitHub for the index file
    parent_folder = os.path.dirname(index_file_path)
    index_repo_remote_url = get_remote_urls_from_git_repo(parent_folder)
    try:
        subprocess.run(["git", "pull", index_repo_remote_url])
    except subprocess.CalledProcessError as e:
        raise Exception(f"Git command failed: {e.stderr.strip()}")
    
    with open(index_file_path, "rb") as f:
        toml_content = tomli.load(f)

    if name not in toml_content:
        raise ValueError(f"{name} not found in {index_file_path}")
    
    return toml_content[name]["url"]  # Return the URL associated with the package name