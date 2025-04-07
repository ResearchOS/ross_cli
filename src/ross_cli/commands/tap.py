import os
import subprocess

import tomli
import tomli_w
import typer

from ..constants import *
from ..git.github import parse_github_url

def tap_github_repo_for_ross_index(remote_url: str):
    # Check for the existence of the config file    
    if not os.path.exists(DEFAULT_ROSS_CONFIG_FILE_PATH):
        raise FileNotFoundError(f"ROSS config file {DEFAULT_ROSS_CONFIG_FILE_PATH} does not exist.")
    
    # Parse for GitHub username and repository name from the URL
    username, repo_name = parse_github_url(remote_url)
    repo_git_file_path = os.path.join(DEFAULT_ROSS_INDICES_FOLDER, username, repo_name, '.git') 
    repo_folder_path = os.path.join(DEFAULT_ROSS_INDICES_FOLDER, username, repo_name)    
    
    # Check if the index file path already exists in the config file
    with open(DEFAULT_ROSS_CONFIG_FILE_PATH, 'rb') as f:
        ross_config = tomli.load(f)
        if "index" not in ross_config:
            ross_config["index"] = []
        for index in ross_config["index"]:
            if index["path"] == repo_folder_path:
                typer.echo(f"Aborting. Index file already exists in ROSS config at: {DEFAULT_ROSS_CONFIG_FILE_PATH}.")
                typer.echo(f"Path: {index['path']}")
                typer.echo(f"Remote URL: {index['url']}")
                return
            
    # Clone the GitHub repository to ~/.ross/indices/<username/repo>
    if os.path.exists(repo_git_file_path):
        typer.echo(f"Repository already exists at {repo_git_file_path}.")
        typer.echo("Running `git pull` on the repository.")
        subprocess.run(["git", "pull"], cwd=repo_folder_path, check=True)
    else:
        if os.path.exists(repo_folder_path):
            typer.echo(f"Cannot clone index repository from remote because a folder already exists at {repo_folder_path}.")
            typer.echo("Please delete the folder and try again.")
            return
        subprocess.run(["git", "clone", remote_url, repo_folder_path], check=True)

    # After the GitHub repository is cloned, create the index file if it doesn't already exist
    index_file_path = os.path.join(repo_folder_path, "index.toml")
    if not os.path.exists(index_file_path):
        with open(index_file_path, "wb") as f:
            tomli_w.dump({}, f)
        # git push to remote
        subprocess.run(["git", "add", index_file_path], cwd=repo_folder_path, check=True)
        subprocess.run(["git", "commit", "-m", "Add index.toml file"], cwd=repo_folder_path, check=True)
        subprocess.run(["git", "push"], cwd=repo_folder_path, check=True)

    # Add the index.toml file path to DEFAULT_DEFAULT_ROSS_CONFIG_FILE_PATH
    index_username_reponame = username + "/" + repo_name
    ross_config["index"].append({"name": index_username_reponame, "path": index_file_path})
    with open(DEFAULT_ROSS_CONFIG_FILE_PATH, "wb") as f:
        tomli_w.dump(ross_config, f)