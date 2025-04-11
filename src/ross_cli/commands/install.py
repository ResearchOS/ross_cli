import os
from typing import List
from urllib.request import urlopen

import subprocess
import typer
import tomli

from ..constants import *
from ..git.index import get_package_remote_url
from ..git.github import get_default_branch_name

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

    remote_url = get_package_remote_url(package_name)
    url_parts = remote_url.split("/")
    github_user = url_parts[-2]
    github_repo = url_parts[-1]
    main_branch_name = get_default_branch_name(remote_url)
    pyproject_toml_url = f"https://raw.githubusercontent.com/{github_user}/{github_repo}/{main_branch_name}/pyproject.toml"
    github_full_url = f"git+{remote_url}" # Add git+ to the front of the URL
    try:
        pip_install = True
        with urlopen(pyproject_toml_url) as response:
            pyproject_content = tomli.load(response.read().decode())
    except:
        typer.echo("Failed to directly `pip install` the GitHub repository. The repository is likely private.")
        typer.echo("Switching to `gh clone` method. This requires you to have read access to the private repository.")

        try:
            subprocess.run(["gh", "--version"], capture_output=True)
        except:
            typer.echo("`gh` CLI not found. Check the official repository for more information: https://github.com/cli/cli")
            raise typer.Exit()

        try:
            # Get the current directory
            pip_install = False
            root_dir = os.getcwd()
            os.chdir(install_folder_path)
            subprocess.run(["gh", "repo", "clone", f"{github_user}/{github_repo}"])
            # Read the pyproject.toml file for the official package name
            pyproject_toml_path = os.path.join(install_folder_path, github_repo, 'pyproject.toml')
            with open(pyproject_toml_path, 'rb') as f:
                pyproject_content = tomli.load(f)
        except:
            os.chdir(root_dir)
            typer.echo(f"Failed to `gh clone` the repository. Check the URL: {remote_url}")
            typer.echo("Make sure you have authorized the `gh` CLI by running `gh auth login`")
            raise typer.Exit()    

    if "project" in pyproject_content and "name" in pyproject_content["project"]:
        official_package_name = pyproject_content["project"]["name"]
    else:
        typer.echo("pyproject.toml missing [project][name] field")
        raise typer.Exit()    

    # Set the PIP_SRC environment variable to the install folder path
    os.environ["PIP_SRC"] = install_folder_path
    if pip_install:
        github_full_url_with_egg = github_full_url + "#" + official_package_name
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