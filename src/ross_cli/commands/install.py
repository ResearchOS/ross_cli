import os
from typing import List
from urllib.request import urlopen

import subprocess
import typer
import tomli

from ..constants import *
from ..git.index import search_indexes_for_package_info
from ..git.github import read_github_file

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

    os.environ["PIP_SRC"] = install_folder_path 

    pkg_info = search_indexes_for_package_info(package_name)
    if not pkg_info:
        # If not found in the ROSS indexes, install it using pip.
        subprocess.run(["pip", "install", "-e", package_name] + args)
        raise typer.Exit()
    
    auth_token = subprocess.run(["gh", "auth", "token"], capture_output=True, check=True).stdout.decode().strip()
    auth_token = str(auth_token).replace('\\\\n')
    remote_url_no_token = pkg_info['url']
    remote_url = remote_url_no_token.replace("https://", f"https://{auth_token}@")
    url_parts = remote_url.split("/")
    github_user = url_parts[-2]
    github_repo = url_parts[-1].replace(".git", "")    
    pyproject_toml_url = f"https://{auth_token}@github.com/{github_user}/{github_repo}/pyproject.toml"    
    
    pyproject_content = tomli.loads(read_github_file(pyproject_toml_url))

    if "project" in pyproject_content and "name" in pyproject_content["project"]:
        official_package_name = pyproject_content["project"]["name"]
    else:
        typer.echo("pyproject.toml missing [project][name] field")
        raise typer.Exit()    
        
    github_full_url = f"git+{remote_url}" # Add git+ to the front of the URL
    github_full_url_with_egg = github_full_url + "#egg=" + official_package_name
    typer.echo(f"pip installing package {package_name}...")
    subprocess.run(["pip", "install", "-e", github_full_url_with_egg] + args, check=True)

    is_r = False
    try:
        if pyproject_content["tool"][CLI_NAME]["language"] == "R":
            is_r = True
    except:
        pass

    if is_r:
        if "dependencies" not in pyproject_content["tool"][CLI_NAME]:
            pyproject_content["tool"][CLI_NAME]["dependencies"] = []

        for dep in pyproject_content["tool"][CLI_NAME]["dependencies"]:
            # Run R's `install.packages()` command                
            if "/" not in package_name:      
                print(f"Trying CRAN installation for {package_name}...")
                command = ["Rscript", "-e", f"install.packages('{dep}')"] 
                subprocess.run(command, check=True)
            else:
                print(f"Installing from GitHub: {package_name}")
                # Install devtools if needed.
                devtools_cmd = ["Rscript", "-e", "if(!require('devtools')) install.packages('devtools', repos='https://cloud.r-project.org')"]
                subprocess.run(devtools_cmd, check=True, capture_output=True)

                # Install from GitHub
                command = ["Rscript", "-e", f"devtools::install_github('{package_name}')"]
                subprocess.run(command, check=True)

    typer.echo(f"Successfully installed package {package_name}")