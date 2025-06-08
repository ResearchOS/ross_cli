import os
from typing import List
import re
import errno
import tempfile

import subprocess
import typer
import tomli

from ..constants import *
from ..git.index import search_indexes_for_package_info
from ..git.github import read_github_file_from_release, download_github_release, get_latest_release_tag, parse_github_url, get_default_branch_name, add_auth_token_to_github_url
from ..utils.venv import get_venv_path_in_dir, get_install_loc_in_venv
from ..utils.urls import check_url_exists

def install(package_name: str, install_folder_path: str = DEFAULT_PIP_SRC_FOLDER_PATH, install_package_root_folder: str = os.getcwd(), _config_file_path: str = DEFAULT_ROSS_CONFIG_FILE_PATH, args: List[str] = []):
    f"""Install a package.
    1. Get the URL from the .toml file (default: {DEFAULT_ROSS_INDICES_FOLDER})
    2. Install the package using pip""" 
    
    full_install_folder_path = os.path.join(install_package_root_folder, install_folder_path)
    
    # Create the install folder if it does not exist
    os.makedirs(full_install_folder_path, exist_ok=True)   

    # Get the release tag, if specified
    tag = None
    if "==" in package_name:
        equals_idx = package_name.find("==")
        tag = package_name[equals_idx+2:]
        package_name = package_name[0:equals_idx]

    pkg_info = search_indexes_for_package_info(package_name, config_file_path=_config_file_path)
    # If a package is not in the ROSS index, then treat it exactly the same as if the user ran "pip install".
    if not pkg_info:
        typer.echo(f"Package {package_name} not found in ROSS index. Attempting to editable install using pip...")        
        try:
            subprocess.run(["pip", "install", package_name] + args, check=True)
        except subprocess.CalledProcessError as e:
            typer.echo(f"Package {package_name} not found in ROSS index, and failed to install it using pip. Aborting.")
            raise typer.Exit()
        return None
    
    # Get the pyproject.toml file from the package's GitHub repository
    remote_url_no_token = pkg_info['url'].replace(".git", "")     
    owner, repo, _ = parse_github_url(remote_url_no_token)
    if tag is None:
        # No tag specified
        tag = get_latest_release_tag(owner, repo)
    if tag is None:
        # No releases in this repository
        tag = get_default_branch_name(remote_url_no_token)
    remote_url_no_token_with_tag = f"{remote_url_no_token}/blob/{tag}"
    remote_url_with_token = add_auth_token_to_github_url(remote_url_no_token_with_tag)           
    repo_url = f"https://github.com/{owner}/{repo}"
    pyproject_toml_url = f"{repo_url}/blob/{tag}/pyproject.toml"
    if not check_url_exists(pyproject_toml_url):
        typer.echo(f"Missing pyproject.toml file for {owner}/{repo}")
        typer.echo(f"Run `ross release` for the package {package_name} to generate this file.")
        raise typer.Exit(code=4)
    pyproject_content = tomli.loads(read_github_file_from_release(pyproject_toml_url, tag=tag))

    if "project" in pyproject_content and "name" in pyproject_content["project"]:
        official_package_name = pyproject_content["project"]["name"]
    else:
        typer.echo("pyproject.toml missing [project][name] field")
        raise typer.Exit()    
        
    # pip install the package
    curr_dir = os.getcwd()
    os.chdir(install_package_root_folder)
    github_full_url = f"git+{remote_url_with_token}" # Add git+ to the front of the URL
    github_full_url_with_egg = github_full_url + "#egg=" + official_package_name
    typer.echo(f"pip installing package {package_name}...")
    github_full_url_with_egg = github_full_url_with_egg.replace("/blob/", "@")
    venv_path = get_venv_path_in_dir(install_package_root_folder)
    if os.name == "nt": # Windows
        pip_path = os.path.join(venv_path, "Scripts", "pip")
    else:
        pip_path = os.path.join(venv_path, "bin", "pip")
    result = subprocess.run([pip_path, "install", github_full_url_with_egg] + args, check=True)    
 
    language = pyproject_content["tool"][CLI_NAME]["language"]

    if "dependencies" not in pyproject_content["tool"][CLI_NAME]:
            pyproject_content["tool"][CLI_NAME]["dependencies"] = []
          
    # MATLAB & R dependencies should install to the venv folder too to keep everything in one place.
    ross_package_url_regex = r'^[a-zA-Z][a-zA-Z0-9_-]*\s@\sgit\+.*'
    for dep in pyproject_content["tool"][CLI_NAME]["dependencies"]:
        if re.search(ross_package_url_regex, dep) is not None:
            # Get the dependency package name
            split_dep = dep.split(" ")
            dep_package_name = split_dep[0]
            # Get the dependency version
            at_idx = [(i, c) for i, c in enumerate(dep) if c == "@"]
            if len(at_idx) != 2:
                typer.echo("Wrong number of '@' in dependency.")
                typer.Exit(code=11)
            version = dep[at_idx[1][0]+1:]
            install(f"{dep_package_name}=={version}", install_package_root_folder=install_package_root_folder, _config_file_path=_config_file_path)
            continue
        if language.lower() == "r":  
            folder_path = install_dep_r(dep, venv_path)            
        elif language.lower() == "matlab":
            folder_path = install_dep_matlab(dep, venv_path)        

    os.chdir(curr_dir) # Revert back to the original working directory

    typer.echo(f"Successfully installed package {package_name}")


def install_dep_r(dep: str, venv_path: str):
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


def install_dep_matlab(dep: str, venv_path: str):
    """Download GitHub repo from the /archive/ endpoint, so that the .git folder is not downloaded.
    Also names the folder as {repository}-{tag} because the MATLAB repo likely does not contain a file documenting its version."""
    if "/blob/" not in dep:
        typer.echo(r"Dependency located on GitHub declared in pyproject.toml must be of the format: https://github.com/{owner}/{repo}/blob/{tag}")
        typer.echo(f"Dependency incorrectly specified as: {dep}")
        raise typer.Exit(code=12)
    
    # Parse the dependency for the owner, repo, and tag.
    # output_dir = os.environ["PIP_SRC"]
    split_url = dep.split("/blob/")
    tag = split_url[1]
    split_repo_url = split_url[0].split("/")
    owner = split_repo_url[-2]
    repo = split_repo_url[-1]
    # Downloads to the root folder    
    with tempfile.TemporaryDirectory() as temp_dir:
        folder_path = download_github_release(owner, repo, tag, temp_dir)
        folder_name = os.path.basename(folder_path) # Get the folder name
        # Figure out where in the virtual environment the package should be moved to.
        install_loc = get_install_loc_in_venv(venv_path)
        # Move the folder into the venv
        install_folder_path = os.path.join(install_loc, folder_name)
        try:
            os.rename(folder_path, install_folder_path)
        except OSError as e:
            if e.errno != errno.ENOTEMPTY:
                raise
    return install_folder_path
