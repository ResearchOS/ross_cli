import os
from typing import List
import shutil

import subprocess
import typer
import tomli

from ..constants import *
from ..git.index import search_indexes_for_package_info
from ..git.github import read_github_file_from_release, download_github_release, get_latest_release_tag

def install(package_name: str, install_folder_path: str = DEFAULT_PIP_SRC_FOLDER_PATH, install_package_root_folder: str = os.getcwd(), args: List[str] = []):
    f"""Install a package.
    1. Get the URL from the .toml file (default: {DEFAULT_ROSS_INDICES_FOLDER})
    2. Install the package using pip""" 
    
    full_install_folder_path = os.path.join(install_package_root_folder, install_folder_path)
    
    # Create the install folder if it does not exist
    os.makedirs(full_install_folder_path, exist_ok=True)   

    os.environ["PIP_SRC"] = full_install_folder_path

    pkg_info = search_indexes_for_package_info(package_name)
    # If a package is not in the ROSS index, then treat it exactly the same as if the user ran "pip install".
    if not pkg_info:
        typer.echo(f"Package {package_name} not found in ROSS index. Attempting to editable install using pip...")        
        try:
            subprocess.run(["pip", "install", "-e", package_name] + args, check=True)
        except subprocess.CalledProcessError as e:
            typer.echo(f"Package {package_name} not found in ROSS index, and failed to install it using pip. Aborting.")
            raise typer.Exit()
        return None
    
    # Get the pyproject.toml file from the package's GitHub repository
    auth_token = subprocess.run(["gh", "auth", "token"], capture_output=True, check=True).stdout.decode().strip()    
    remote_url_no_token = pkg_info['url'].replace(".git", "")
    remote_url_no_token_split = remote_url_no_token.split("/")
    owner = remote_url_no_token_split[-2]
    repo = remote_url_no_token_split[-1]
    tag = get_latest_release_tag(owner, repo)
    remote_url_no_token_with_tag = f"{remote_url_no_token}/blob/{tag}"
    remote_url = remote_url_no_token_with_tag.replace("https://", f"https://{auth_token}@")
    split_url = remote_url.split('/blob/')
    repo_url = split_url[0]
    pyproject_toml_url = f"{repo_url}/blob/{tag}/pyproject.toml"    
    
    pyproject_content = tomli.loads(read_github_file_from_release(pyproject_toml_url, tag=tag))

    if "project" in pyproject_content and "name" in pyproject_content["project"]:
        official_package_name = pyproject_content["project"]["name"]
    else:
        typer.echo("pyproject.toml missing [project][name] field")
        raise typer.Exit()    
        
    curr_dir = os.getcwd()
    os.chdir(install_package_root_folder)
    github_full_url = f"git+{remote_url}" # Add git+ to the front of the URL
    github_full_url_with_egg = github_full_url + "#egg=" + official_package_name
    typer.echo(f"pip installing package {package_name}...")
    github_full_url_with_egg = github_full_url_with_egg.replace("/blob/", "@")
    result = subprocess.run(["pip", "install", "-e", github_full_url_with_egg] + args, check=True)
    os.chdir(curr_dir) # Revert back to the original working directory
 
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
    """Download GitHub repo from the /archive/ endpoint, so that the .git folder is not downloaded.
    Also names the folder as {repository}-{tag} because the MATLAB repo likely does not contain a file documenting its version."""
    if "/blob/" not in dep:
        typer.echo(f"MATLAB dependency not specified as a release URL: {dep}")
        raise typer.Exit()
    
    # Parse the dependency for the owner, repo, and tag.
    output_dir = os.environ["PIP_SRC"]
    split_url = dep.split("/blob/")
    tag = split_url[1]
    split_repo_url = split_url[0].split("/")
    owner = split_repo_url[-2]
    repo = split_repo_url[-1]
    download_github_release(owner, repo, tag, output_dir)