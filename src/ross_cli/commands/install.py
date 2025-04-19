import os
from typing import List
from urllib.request import urlopen

import subprocess
import typer
import tomli

from ..constants import *
from ..git.index import search_indexes_for_package_info
from ..git.github import read_github_file, download_github_release, get_latest_release_tag

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
    # If a package is not in the ROSS index, then treat it exactly the same as if the user ran "pip install".
    if not pkg_info:
        subprocess.run(["pip", "install", "-e", package_name] + args)
        raise typer.Exit()
    
    auth_token = subprocess.run(["gh", "auth", "token"], capture_output=True, check=True).stdout.decode().strip()    
    remote_url_no_token = pkg_info['url'].replace(".git", "")
    remote_url_no_token_split = remote_url_no_token.split("/")
    owner = remote_url_no_token_split[-2]
    repo = remote_url_no_token_split[-1]
    tag = get_latest_release_tag(owner, repo)
    remote_url_no_token_with_tag = f"{remote_url_no_token}/releases/tag/{tag}"
    remote_url = remote_url_no_token_with_tag.replace("https://", f"https://{auth_token}@")
    split_url = remote_url.split('/releases/tag/')
    repo_url = split_url[0]
    pyproject_toml_url = f"{repo_url}/blob/{tag}/pyproject.toml"    
    
    pyproject_content = tomli.loads(read_github_file(pyproject_toml_url, tag=tag))

    if "project" in pyproject_content and "name" in pyproject_content["project"]:
        official_package_name = pyproject_content["project"]["name"]
    else:
        typer.echo("pyproject.toml missing [project][name] field")
        raise typer.Exit()    
        
    github_full_url = f"git+{remote_url}" # Add git+ to the front of the URL
    github_full_url_with_egg = github_full_url + "#egg=" + official_package_name
    typer.echo(f"pip installing package {package_name}...")
    github_full_url_with_egg = github_full_url_with_egg.replace("/releases/tag/", "@")
    subprocess.run(["pip", "install", "-e", github_full_url_with_egg] + args, check=True)

    language = pyproject_content["tool"][CLI_NAME]["language"]

    if "dependencies" not in pyproject_content["tool"][CLI_NAME]:
            pyproject_content["tool"][CLI_NAME]["dependencies"] = []
          
    for dep in pyproject_content["tool"][CLI_NAME]["dependencies"]:
        if language.lower() == "r":  
            install_dep_r(dep)            
        elif language.lower() == "matlab":
            install_dep_matlab(dep)

    typer.echo(f"Successfully installed package {package_name}")

def install_dep_r(dep: str):
    # Run R's `install.packages()` command                
    if "cran.r-project.org" in dep:      
        print(f"Trying CRAN installation for {dep}...")
        command = ["Rscript", "-e", f"install.packages('{dep}')"] 
        subprocess.run(command, check=True)
    else:
        print(f"Installing from GitHub: {dep}")
        # Install devtools if needed.
        devtools_cmd = ["Rscript", "-e", "if(!require('devtools')) install.packages('devtools', repos='https://cloud.r-project.org')"]
        subprocess.run(devtools_cmd, check=True, capture_output=True)

        # Install from GitHub
        command = ["Rscript", "-e", f"devtools::install_github('{dep}')"]
        subprocess.run(command, check=True)

def install_dep_matlab(dep: str):

    if "/releases/tag" not in dep:
        typer.echo(f"MATLAB dependency not specified as a release URL: {dep}")
        raise typer.Exit()
    
    # Parse the dependency for the owner, repo, and tag.
    output_dir = os.environ["PIP_SRC"]
    split_url = dep.split("/releases/tag/")
    tag = split_url[1]
    split_repo_url = split_url[0].split("/")
    owner = split_repo_url[-2]
    repo = split_repo_url[-1]
    download_github_release(owner, repo, tag, output_dir)