import os
import subprocess
import shutil

import tomli
import tomli_w
import typer

from ..constants import *
from ..git.github import parse_github_url

def tap_github_repo_for_ross_index(remote_url: str):
    # Check for the existence of the config file    
    if not os.path.exists(DEFAULT_ROSS_CONFIG_FILE_PATH):
        typer.echo(f"ROSS config file {DEFAULT_ROSS_CONFIG_FILE_PATH} does not exist.")
        raise typer.Exit()
    
    # Parse for GitHub username and repository name from the URL
    username, repo_name = parse_github_url(remote_url)
    repo_git_file_path = os.path.join(DEFAULT_ROSS_INDICES_FOLDER, username, repo_name, '.git') 
    repo_folder_path = os.path.join(DEFAULT_ROSS_INDICES_FOLDER, username, repo_name)
    index_toml_file_path = os.path.join(repo_folder_path, 'index.toml')    
    
    # Check if the index file path already exists in the config file
    with open(DEFAULT_ROSS_CONFIG_FILE_PATH, 'rb') as f:
        ross_config = tomli.load(f)
    if "index" not in ross_config:
        ross_config["index"] = []
    for index in ross_config["index"]:
        if "path" in index and index["path"] == index_toml_file_path:
            typer.echo(f"Aborting. Index file already exists in ROSS config at:")
            typer.echo(f"{index['path']}")
            raise typer.Exit()
            
    # Clone the GitHub repository to ~/.ross/indexes/<username/repo>
    if os.path.exists(repo_git_file_path):
        typer.echo(f"Repository already exists at {repo_git_file_path}.")
        typer.echo("Running `git pull` on the repository.")
        subprocess.run(["git", "pull"], cwd=repo_folder_path, check=True)
    else:
        if os.path.exists(repo_folder_path):
            typer.echo(f"Cannot clone index repository from remote because a folder already exists at {repo_folder_path}.")
            typer.echo("Please delete the folder and try again.")
            raise typer.Exit()
        subprocess.run(["git", "clone", remote_url, repo_folder_path], check=True)

    # After the GitHub repository is cloned, create the index file if it doesn't already exist    
    if not os.path.exists(index_toml_file_path):
        with open(index_toml_file_path, "wb") as f:
            tomli_w.dump({}, f)
        # git push to remote
        subprocess.run(["git", "add", index_toml_file_path], cwd=repo_folder_path, check=True)
        subprocess.run(["git", "commit", "-m", "Add index.toml file"], cwd=repo_folder_path, check=True)
        subprocess.run(["git", "push"], cwd=repo_folder_path, check=True)

    # Add the index.toml file path to DEFAULT_DEFAULT_ROSS_CONFIG_FILE_PATH
    ross_config["index"].append({"path": index_toml_file_path})
    with open(DEFAULT_ROSS_CONFIG_FILE_PATH, "wb") as f:
        tomli_w.dump(ross_config, f)

    github_user_folder = os.path.dirname(repo_folder_path)
    typer.echo(f"Added folder during tap: {github_user_folder}")
    typer.echo(f"Successfully tapped:     {remote_url}")

def untap_ross_index(remote_url: str):
    """Remove the GitHub repository from the ROSS index. Also remove the index folder from the .ross/indexes folder"""
    # Check for the existence of the config file
    if not os.path.exists(DEFAULT_ROSS_CONFIG_FILE_PATH):
        typer.echo("ROSS config file missing")
        raise typer.Exit()

    # Parse for GitHub username and repository name from the URL
    username, repo_name = parse_github_url(remote_url)
    repo_git_file_path = os.path.join(DEFAULT_ROSS_INDICES_FOLDER, username, repo_name, '.git') 
    repo_folder_path = os.path.join(DEFAULT_ROSS_INDICES_FOLDER, username, repo_name)
    index_toml_file_path = os.path.join(repo_folder_path, 'index.toml')

    with open(DEFAULT_ROSS_CONFIG_FILE_PATH, 'rb') as f:
        ross_config_toml = tomli.load(f)

    if "index" not in ross_config_toml:
        ross_config_toml["index"] = []

    if len(ross_config_toml["index"]) == 0:
        typer.echo("No indexes present in the config file. Aborting...")
        raise typer.Exit()

    # Check that the .git file exists
    if not os.path.exists(repo_git_file_path):
        typer.echo(f"Repository not found at: {repo_git_file_path}")
        raise typer.Exit()

    # Remove it from the index
    indexes = ross_config_toml["index"]
    index = {"path": ""}
    for index in indexes:
        if "path" in index and index["path"] == index_toml_file_path:            
            ross_config_toml["index"].remove(index)            
            break

    # Save the modified config file
    with open(DEFAULT_ROSS_CONFIG_FILE_PATH, 'wb') as f:
        tomli_w.dump(ross_config_toml, f)

    # Remove it from disk
    if "path" in index and os.path.exists(index["path"]):
        github_user_folder_path = os.path.dirname(repo_folder_path)
        shutil.rmtree(github_user_folder_path)
        typer.echo(f"Removed folder during untap: {github_user_folder_path}")

    typer.echo(f"Successfully untapped: {remote_url}")    