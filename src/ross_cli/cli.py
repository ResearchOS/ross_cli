import os
import subprocess
from typing import List
from pprint import pprint

import typer
import tomli
import tomli_w

from .git.github import get_remote_url_from_git_repo, git_push_to_remote, parse_github_url
from .git.index import get_package_remote_url_from_index_file
from .commands import add_to_index, install, uninstall, release

app = typer.Typer()

index_app = typer.Typer() # Create a new app for the index command
app.add_typer(index_app, name="index") # Add the index app to the main app

from .constants import *

@app.command(name="install")
def install_command(name: str, index_file_path: str = None, install_folder_path: str = DEFAULT_INSTALL_FOLDER_PATH, args: List[str] = []):
    """Install a package.
    1. Get the URL from the .toml file (default: ~/.rto/indices/index1.toml)
    2. Install the package using pip"""
    typer.echo(f"Installing {name}...")

    remote_url = get_package_remote_url_from_index_file(name, index_file_path)    
    github_full_url = f"git+{remote_url}" # Add git+ to the front of the URL

    # Set the PIP_SRC environment variable to the install folder path
    os.environ["PIP_SRC"] = install_folder_path
    subprocess.run(["pip", "install", "-e", github_full_url] + args)

@app.command(name="uninstall")
def uninstall_command(name: str, install_folder_path: str = DEFAULT_INSTALL_FOLDER_PATH, args: List[str] = []):
    """Uninstall a package."""
    typer.echo(f"Uninstalling {name}...")
    subprocess.run(["pip", "uninstall", name] + args)
    os.rmdir(os.path.join(install_folder_path, name))

@app.command(name="add")
def add_to_index_command(name: str, package_folder_path: str = os.getcwd(), index_file_path: str = None):
    """Create a new package.
    1. Register the package with the .toml file living in the user's home directory. Throw error if file does not exist.
        - Locate the .toml file (default: ~/.rto/indices/index1.toml)
        - Get the remote URLs from the git repository (fail if folder is not a git repo, and error if 0 or 2+ remotes exist)
        - Add the package to the .toml file (error if it already exists)
        [package_name]
        url = "https://github.com/username/repo.git"
    2. Create the package directory and files in the `package_folder_path` (default: current working directory). Don't create each file/folder if it already exists.
        - README.md
        - src/
        - tests/
        - docs/
        .gitignore
    """
    typer.echo(f"Creating new package {name}...")

    toml_file_path = index_file_path
    remote_url = get_remote_url_from_git_repo()
    add_to_index.update_toml_index_file(toml_file_path, name, remote_url)
    git_push_to_remote(os.path.dirname(index_file_path))
    result = add_to_index.create_package_structure(name, package_folder_path)
    if result == 0:
        typer.echo(f"Package {name} created successfully.")

@app.command(name="release")
def release_command(pyproject_toml_path: str = DEFAULT_PYPROJECT_TOML_PATH, args: List[str] = ['--fail-on-no-commits', ]):
    """Release a new version of a package."""
    if not os.path.exists(pyproject_toml_path):
        raise typer.BadParameter(f"File {pyproject_toml_path} does not exist.")
    
    pyproject_folder_path = os.path.dirname(pyproject_toml_path)
    os.chdir(pyproject_folder_path)
    pyproject_toml = tomli.load(pyproject_toml_path)
    name = pyproject_toml["project"]["name"]
    version = pyproject_toml["project"]["version"]    

    typer.echo(f"Releasing package {name} version {version}...")
    
    release.release_package(pyproject_toml, args)

    typer.echo(f"Package {name} version {version} released successfully.")

@app.command(name="tap")
def tap_command(remote_url: str):
    """Add the index GitHub repository to the list of indices in the config file at DEFAULT_ROSS_CONFIG_FILE_PATH.
    1. Parse for GitHub username and repository name from the URL
    2. Fail if the folder ~/.ross/indices/<username/repo> exists on disk, or ~/.ross/indices/<username/repo>/.toml exists in ~/.ross/ross_config.toml.
    3. Clone the GitHub repository to ~/.ross/indices/<username/repo>. 
    4. If ~/.ross/indices/<username/repo>/index.toml does not exist, create it.
    5. Add the index.toml file path to ~/.ross/ross_config.toml.
    6. Push the changes to the remote repository."""
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
                raise ValueError(f"Aborting. Index file {index['path']} already exists in {DEFAULT_ROSS_CONFIG_FILE_PATH}.")
            
    # Clone the GitHub repository to ~/.ross/indices/<username/repo>
    if os.path.exists(repo_git_file_path):
        typer.echo(f"Repository already exists at {repo_git_file_path}.")
        typer.echo("Running `git pull` on the repository.")
        subprocess.run(["git", "pull"], cwd=repo_folder_path, check=True)
    else:
        if os.path.exists(repo_folder_path):
            raise ValueError(f"Cannot clone index from remote because local folder already exists at {repo_folder_path}.")
        subprocess.run(["git", "clone", remote_url, repo_folder_path], check=True)

    # Create the index file if it doesn't exist
    index_file_path = os.path.join(repo_folder_path, "index.toml")
    if not os.path.exists(index_file_path):
        with open(index_file_path, "wb") as f:
            tomli_w.dump({}, f)
        # git push to remote
        subprocess.run(["git", "add", index_file_path], cwd=repo_folder_path, check=True)
        subprocess.run(["git", "commit", "-m", "Add index.toml file"], cwd=repo_folder_path, check=True)
        git_push_to_remote(repo_folder_path)

    # Add the index.toml file path to DEFAULT_DEFAULT_ROSS_CONFIG_FILE_PATH
    ross_config["index"].append({"name": repo_name, "path": index_file_path})
    with open(DEFAULT_ROSS_CONFIG_FILE_PATH, "wb") as f:
        tomli_w.dump(ross_config, f)

@app.command(name="config")
def config_command():
    """Print information about the ROSS CLI and its configuration."""
    typer.echo("ROSS command line interface (CLI) information:")
    typer.echo(f"ROSS root folder location: {DEFAULT_ROSS_ROOT_FOLDER}.")
    typer.echo(f"ROSS configuration file location: {DEFAULT_ROSS_CONFIG_FILE_PATH}.")
    typer.echo(f"ROSS indices folder location: {DEFAULT_ROSS_INDICES_FOLDER}.")
    
    # Show config content
    try:
        with open(DEFAULT_ROSS_CONFIG_FILE_PATH, 'rb') as f:
            config = tomli.load(f)
            typer.echo("\nCurrent configuration:")
            pprint(config)
    except FileNotFoundError:
        typer.echo("No configuration file found. Run 'ross init' to create one.")

@app.command(name="init")
def init_command():
    """Initialize the ROSS CLI."""
    typer.echo("Initializing ROSS command line interface (CLI)...")
    if not os.path.exists(DEFAULT_ROSS_CONFIG_FILE_PATH):
        os.makedirs(os.path.dirname(DEFAULT_ROSS_CONFIG_FILE_PATH), exist_ok=True)
        with open(DEFAULT_ROSS_CONFIG_FILE_PATH, "wb") as f:
            tomli_w.dump(DEFAULT_ROSS_CONFIG_CONTENT, f)
        typer.echo(f"ROSS config file created at {DEFAULT_ROSS_CONFIG_FILE_PATH}.")
    else:
        typer.echo(f"Initialization stopped. ROSS config file already exists at {DEFAULT_ROSS_CONFIG_FILE_PATH}.")