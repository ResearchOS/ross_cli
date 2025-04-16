import os
from typing import List
from urllib.request import urlopen

import subprocess
import typer
import tomli

from ..constants import *
from ..git.index import search_indexes_for_package_info
from ..git.github import get_default_branch_name, read_github_file

def install(package_name: str, install_folder_path: str = DEFAULT_PIP_SRC_FOLDER_PATH, args: List[str] = []):
    f"""Install a package.
    1. Get the URL from the .toml file (default: {DEFAULT_ROSS_INDICES_FOLDER})
    2. Install the package using pip""" 

    # Check that this folder contains a rossproject.toml file
    if not os.path.exists(DEFAULT_ROSSPROJECT_TOML_PATH):
        typer.echo(f"Current directory is not a ROSS project, missing rossproject.toml file.")
        typer.echo("Run `ross init` to create a rossproject.toml in this folder.")
        return
    
    # Check that the install folder exists
    if not os.path.exists(install_folder_path):
        os.makedirs(install_folder_path, exist_ok=True)    

    pkg_info = search_indexes_for_package_info(package_name)
    remote_url = pkg_info['url']
    url_parts = remote_url.split("/")
    github_user = url_parts[-2]
    github_repo = url_parts[-1].replace(".git", "")
    pyproject_toml_url = f"https://github.com/{github_user}/{github_repo}/pyproject.toml"
    github_full_url = f"git+{remote_url}" # Add git+ to the front of the URL
    
    pip_install = True
    pyproject_content = tomli.loads(read_github_file(pyproject_toml_url))

    if "project" in pyproject_content and "name" in pyproject_content["project"]:
        official_package_name = pyproject_content["project"]["name"]
    else:
        typer.echo("pyproject.toml missing [project][name] field")
        raise typer.Exit()    

    # Set the PIP_SRC environment variable to the install folder path
    os.environ["PIP_SRC"] = install_folder_path
    if pip_install:
        github_full_url_with_egg = github_full_url + "#egg=" + official_package_name
        typer.echo(f"pip installing package {package_name}...")
        subprocess.run(["pip", "install", "-e", github_full_url_with_egg] + args, check=True)
    else:
        typer.echo(f"pip installing from `gh clone` package {package_name}...")
        # Rename the folder
        cloned_folder = os.path.dirname(pyproject_toml_path)
        official_name_folder = os.path.join(os.path.dirname(cloned_folder), official_package_name)
        os.rename(cloned_folder, official_name_folder)
        # pip install -e from that folder
        os.chdir(root_dir)
        subprocess.run(["pip", "install", "-e", official_name_folder] + args, check=True)

    typer.echo(f"Successfully installed package {package_name}")