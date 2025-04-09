import os
from typing import List
from pprint import pprint
from importlib.metadata import version, metadata

import typer
import tomli
import tomli_w

from .commands import index, init, tap, install, release

app = typer.Typer()

index_app = typer.Typer() # Create a new app for the index command
app.add_typer(index_app, name="index") # Add the index app to the main app

from .constants import *

@app.command(name="init")
def init_command():
    """Initialize a new ROSS project in the current directory.
    1. Create a new rossproject.toml file in the current directory.
    2. Create the package files and folders if they don't exist (default: current working directory). Don't create each file/folder if it already exists.
        - README.md
        - src/
        - tests/
        - docs/
        .gitignore"""
    init.init_ross_project()


@app.command(name="tap")
def tap_command(remote_url: str):
    """Add the index GitHub repository to the list of indices in the config file at DEFAULT_ROSS_CONFIG_FILE_PATH.
    1. Parse for GitHub username and repository name from the URL
    2. Fail if the folder ~/.ross/indices/<username/repo> exists on disk, or ~/.ross/indices/<username/repo>/.toml exists in ~/.ross/ross_config.toml.
    3. Clone the GitHub repository to ~/.ross/indices/<username/repo>. 
    4. If ~/.ross/indices/<username/repo>/index.toml does not exist, create it.
    5. Add the index.toml file path to ~/.ross/ross_config.toml.
    6. Push the changes to the remote repository."""
    tap.tap_github_repo_for_ross_index(remote_url)


@app.command(name="add-to-index")
def add_to_index_command(index_name: str, package_folder_path: str = os.getcwd()):
    """Add a package to the index.
    1. Register the package with the .toml file living in the user's home directory. Throw error if file does not exist.
        - Locate the .toml file (default: ~/.ross/indices/index1.toml)
        - Get the remote URLs from the git repository (fail if folder is not a git repo, and error if 0 or 2+ remotes exist)
        - Add the package to the .toml file (error if it already exists)
        [package_name]
        url = "https://github.com/username/repo"
    """
    index.add_to_index(index_name, package_folder_path)
    

@app.command(name="install")
def install_command(package_name: str, install_folder_path: str = DEFAULT_PIP_SRC_FOLDER_PATH, args: List[str] = []):
    """Install a package.
    1. Get the URL from the .toml file
    2. Install the package using pip""" 
    install.install(package_name, install_folder_path, args)


# Maybe I don't need to support an uninstall command right now, and the user could just use pip?
# @app.command(name="uninstall")
# def uninstall_command(package_name: str, args: List[str] = []):
#     """Uninstall a package."""
#     typer.echo(f"Uninstalling {package_name}...")
#     subprocess.run(["pip", "uninstall", package_name] + args)


@app.command(name="release")
def release_command(release_type: str = None):
    """Release a new version of this package on GitHub.
    Versions follow semantic versioning guidelines.
    "patch" = +0.0.1, "minor" = +0.1.0, "major" = +1.0.0
    Run without an argument to not increment the version number."""    
    if release_type is not None and release_type not in RELEASE_TYPES:        
        typer.echo(f"Release type must be one of: {', '.join(RELEASE_TYPES)}, or omitted")
        return
    release.release(release_type)


@app.command(name="config")
def config_command():
    """Print information about the ROSS CLI and its configuration."""
    typer.echo("ROSS command line interface (CLI) information:\n")
    typer.echo(f"ROSS root folder location: {DEFAULT_ROSS_ROOT_FOLDER}")
    typer.echo(f"ROSS configuration file location: {DEFAULT_ROSS_CONFIG_FILE_PATH}")
    typer.echo(f"ROSS indices folder location: {DEFAULT_ROSS_INDICES_FOLDER}")
    
    # Show config content
    try:
        with open(DEFAULT_ROSS_CONFIG_FILE_PATH, 'rb') as f:
            config = tomli.load(f)
        typer.echo("\nCurrent configuration:")
        pprint(config)
    except:
        typer.echo(f"No configuration file found at {DEFAULT_ROSSPROJECT_TOML_PATH}")
        typer.echo("Run 'ross cli-init' to create it.")


@app.command(name="cli-init")
def cli_init_command():
    """Initialize the ROSS CLI."""
    typer.echo("Initializing ROSS command line interface (CLI)...")
    if not os.path.exists(DEFAULT_ROSS_CONFIG_FILE_PATH):
        os.makedirs(os.path.dirname(DEFAULT_ROSS_CONFIG_FILE_PATH), exist_ok=True)
        with open(DEFAULT_ROSS_CONFIG_FILE_PATH, "wb") as f:
            tomli_w.dump(DEFAULT_ROSS_CONFIG_CONTENT, f)
        typer.echo(f"ROSS config file created at {DEFAULT_ROSS_CONFIG_FILE_PATH}.")
    else:
        typer.echo(f"Aborted initialization. ROSS config file already exists at {DEFAULT_ROSS_CONFIG_FILE_PATH}.")


def version_callback(value: bool):
    """Print the version of the ROSS CLI."""  
    if not value:
        return
        
    __version__ = version("ross_cli")
    meta = metadata("ross_cli")
    __date__ = meta.get("Date")  # Add this to your pyproject.toml
    __url__ = f"https://github.com/ResearchOS/ross_cli/releases/tag/v{__version__}"

    typer.echo(f"ross cli version {__version__}")
    typer.echo(__url__)
    raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True),
):
    """ROSS command line interface (CLI)"""
    return