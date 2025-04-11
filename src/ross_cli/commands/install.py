import os
from typing import List

import subprocess
import typer

from ..constants import *
from ..git.index import get_package_remote_url

def install(package_name: str, install_folder_path: str = DEFAULT_PIP_SRC_FOLDER_PATH, args: List[str] = []):
    f"""Install a package.
    1. Get the URL from the .toml file (default: {DEFAULT_ROSS_INDICES_FOLDER})
    2. Install the package using pip""" 

    # Check that this folder contains a rossproject.toml file
    # if not os.path.exists(DEFAULT_ROSSPROJECT_TOML_PATH):
    #     typer.echo(f"Current directory is not a ROSS project, missing rossproject.toml file.")
    #     typer.echo("Run `ross init` to create a rossproject.toml in this folder.")
    #     return
    
    # Check that the install folder exists
    if not os.path.exists(install_folder_path):
        os.makedirs(install_folder_path, exist_ok=True)    

    remote_url = get_package_remote_url(package_name)    
    github_full_url = f"git+{remote_url}" # Add git+ to the front of the URL

    # Set the PIP_SRC environment variable to the install folder path
    os.environ["PIP_SRC"] = install_folder_path
    typer.echo(f"Installing {package_name}...")
    subprocess.run(["pip", "install", "-e", github_full_url] + args, check=True)