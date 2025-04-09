import os
from pprint import pprint
import subprocess
import json

import tomli
import tomli_w
import typer

from ..constants import *
from ..git.github import get_remote_url_from_git_repo

def print(index_file_path: str) -> None:
    """Print the index file."""
    if not os.path.exists(index_file_path):
        typer.echo(f"File {index_file_path} does not exist.")
    
    with open(index_file_path, "rb") as f:
        pprint(tomli.load(f))  # Use pprint to print the loaded TOML file
    
def add_to_index(index_name: str, package_folder_path: str) -> None:
    """Add the specified package to the specified index."""
    # Check if the package folder is a git repository
    if not os.path.isdir(os.path.join(package_folder_path, ".git")):
        typer.echo(f"Folder {package_folder_path} is not a git repository.")
        raise typer.Exit()
    
    # Check for the rossproject.toml file
    if not os.path.exists(DEFAULT_ROSSPROJECT_TOML_PATH):
        typer.echo("Missing rossproject.toml file")
        raise typer.Exit()
    
    # Get the index path from the config file
    with open(DEFAULT_ROSS_CONFIG_FILE_PATH, "rb") as f:
        config = tomli.load(f)

    if "index" not in config:
        typer.echo(f"No indexes found in the config file.")
        raise typer.Exit()
    
    # Run git pull to get the latest version of the index file
    try:
        typer.echo("Running `git pull`")
        subprocess.run(["git", "pull"], check=True)
    except subprocess.CalledProcessError:
        parts = package_folder_path.split(os.sep)
        name = parts[-1]
        # try:
        #     gh_api_user = json.load(subprocess.run(["gh", "api", "user"], capture_output=True, text=True, check=True))
        #     user = gh_api_user["login"]
        # except:
        #     user = "github_user"
        typer.echo("`git pull` failed. Make sure this package's git repo has an associated GitHub repository")
        typer.echo(f'To associate this git repo with a new private GitHub repository, do the following:')
        typer.echo("git add .")
        typer.echo('git commit -m "Initial commit"')
        typer.echo(f'gh repo create {name} --source=. --public --push')
        # typer.echo(f'gh repo create {name} --source="." --public')
        # typer.echo(f'git remote add origin https://github.com/{user}/{name}.git')
        # typer.echo('git branch -M main')
        # typer.echo('git push -u origin main')
        raise typer.Exit()        

    # Get the index path
    index_file_path = get_index_path(index_name, config)
    
    # Load the index file    
    with open(index_file_path, "rb") as f:
        index_content = tomli.load(f)

    if "package" not in index_content:
        index_content["package"] = []

    # Get the package name from the rossproject.toml file
    rossproject_toml_path = os.path.join(package_folder_path, "rossproject.toml")
    if not os.path.exists(rossproject_toml_path):
        typer.echo(f"File {rossproject_toml_path} does not exist.")
        raise typer.Exit()
    
    with open(rossproject_toml_path, "rb") as f:
        rossproject_content = tomli.load(f)
    package_name = rossproject_content.get("name", None)
    if not package_name:
        typer.echo(f"Package name not found in {rossproject_toml_path}.")
        raise typer.Exit()

    # Check if the package is already in the index
    if package_name in index_content["package"]:
        typer.echo(f"Package {package_name} already exists in the index.")    
        raise typer.Exit()
    
    # Get the remote URL from the git repository
    remote_url = get_remote_url_from_git_repo(package_folder_path)
    if remote_url.endswith(".git"):
        remote_url = remote_url[:-4]
    
    # Add the package to the index
    index_content["package"].append({"url": remote_url})
    
    # Save the updated index to the file
    with open(index_file_path, "wb") as f:
        tomli_w.dump(index_content, f)  # Use tomli to dump the updated index to the file

    # Push the changes to the remote repository
    index_folder_path = os.path.dirname(index_file_path)
    os.chdir(index_folder_path)
    subprocess.run(["git", "add", index_file_path], check=True)
    subprocess.run(["git", "commit", "-m", f"Add {package_name} to index"], check=True)
    subprocess.run(["git", "push"], check=True)  # Push the changes to the remote repository

def get_index_path(index_name: str, config: dict) -> str:
    """Helper function for add_to_index to get the path to the specified index from the config.
    Currently assumes that the index lives in ~/.ross/indexes/username/repo.
    TODO: What if the repository name changes? Probably shouldn't have the repo name in the path."""
    # Get all of the index usernames & repos
    indexes_username_repo = []
    for index in config["index"]:
        path = index["path"]
        parts = path.split(os.sep)
        if parts[-1].endswith(".toml"):
            parts = parts[0:-1] # Remove the last part if it contains e.g. "index.toml"
        username_repo = os.sep.join(parts[-2:])
        indexes_username_repo.append(username_repo)

    # Determine which repo it's in
    repo_idx = [idx for idx, user_repo in enumerate(indexes_username_repo) if index_name in user_repo]
    if len(repo_idx) == 0:
        typer.echo("No indices found matching that name.")
        raise typer.Exit()
    elif len(repo_idx) > 1:
        typer.echo("Multiple indices found matching that name:")
        typer.echo(', '.join(indexes_username_repo[i] for i in repo_idx))
        raise typer.Exit()

    repo_idx = repo_idx[0]
    index_path = config["index"][repo_idx]["path"]
    
    return index_path