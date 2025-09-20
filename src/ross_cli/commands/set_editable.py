import os
from pathlib import Path
import subprocess

import typer

from utils.check_install import is_package_installed
from utils.venv import get_install_loc_in_venv, get_venv_path_in_dir
from utils.package_urls import get_installed_package_repo_url
from git.github import clone_repo

def set_editable(package_name: str, root_folder: str = os.getcwd()):
    """Get the git repo for the specified install package"""
    # Verify that the package is properly installed. If already installed in editable mode, also exits with code 19
    if not is_package_installed(package_name):
        raise typer.Exit(code=19)
    
    # Get the package folder path
    venv_path = get_venv_path_in_dir(root_folder)
    package_install_path = Path(get_install_loc_in_venv(venv_path)) / package_name

    # Get URL of package's GitHub repository from .dist-info folder for the ROSS-installed package
    url = get_installed_package_repo_url(package_install_path)
    
    # Clone the GitHub repository for the specified package name into {root_folder}/{ross_packages}/{package_name}
    ross_package_folder = Path(root_folder) / "ross_packages" / package_name
    clone_repo(url, ross_package_folder)

    # Copy the installed package's files from the venv to the cloned repo
    # Look in pyproject.toml to determine the build folder location to copy into.
    copy_installed_package_to_repo(package_install_path, ross_package_folder)

    # Uninstall the package from the venv
    subprocess.run(["pip", "uninstall", "-y", package_name], check=True)

    # Install the package in editable mode from the cloned repo
    install_package_from_repo_editable(ross_package_folder)
