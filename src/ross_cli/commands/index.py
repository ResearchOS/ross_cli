import os
from pprint import pprint
import subprocess

import tomli
import tomli_w

from ..constants import *
from ..git.github import get_remote_url_from_git_repo

def print(index_file_path: str) -> None:
    """Print the index file."""
    if not os.path.exists(index_file_path):
        raise ValueError(f"File {index_file_path} does not exist.")
    
    with open(index_file_path, "rb") as f:
        pprint(tomli.load(f))  # Use pprint to print the loaded TOML file
    
def add_to_index(index_name: str, package_folder_path: str) -> None:
    """Add the specified package to the specified index."""
    # Get the index path from the config file
    with open(DEFAULT_ROSS_CONFIG_FILE_PATH, "rb") as f:
        config = tomli.load(f)

    if "index" not in config or index_name not in config["index"]:
        raise ValueError(f"Index {index_name} not found in the config file.")
    
    # Run git pull to get the latest version of the index file
    subprocess.run(["git", "pull"], check=True)
    
    # Load the index file
    index_path = config["index"][index_name]["path"]
    with open(index_path, "rb") as f:
        index_content = tomli.load(f)

    if "package" not in index_content:
        index_content["package"] = []

    # Get the package name from the rossproject.toml file
    rossproject_toml_path = os.path.join(package_folder_path, "rossproject.toml")
    if not os.path.exists(rossproject_toml_path):
        raise ValueError(f"File {rossproject_toml_path} does not exist.")
    
    with open(rossproject_toml_path, "rb") as f:
        rossproject_content = tomli.load(f)
    package_name = rossproject_content.get("name", None)
    if not package_name:
        raise ValueError(f"Package name not found in {rossproject_toml_path}.")

    # Check if the package is already in the index
    if package_name in index_content["package"]:
        raise ValueError(f"Package {package_name} already exists in the index.")
    
    # Check if the package folder is a git repository
    if not os.path.isdir(os.path.join(package_folder_path, ".git")):
        raise ValueError(f"Folder {package_folder_path} is not a git repository.")
    
    # Get the remote URL from the git repository
    remote_url = get_remote_url_from_git_repo(package_folder_path)
    if remote_url.endswith(".git"):
        remote_url = remote_url[:-4]
    
    # Add the package to the index
    index_content["package"].append({"url": remote_url})
    
    # Save the updated index to the file
    with open(index_content, "wb") as f:
        tomli_w.dump(index_name, f)  # Use tomli to dump the updated index to the file

    # Push the changes to the remote repository
    subprocess.run(["git", "add", index_path], check=True)
    subprocess.run(["git", "commit", "-m", f"Add {package_name} to index"], check=True)
    subprocess.run(["git", "push"], check=True)  # Push the changes to the remote repository