import os

import typer

from ..constants import *
from ..git.github import get_remote_url_from_git_repo
from ..utils.rossproject import convert_hyphen_in_name_to_underscore

def init_ross_project(package_name: str, package_folder_path: str = os.getcwd()):
    """Initialize a new ROSS project in the specified directory.
    1. Create a new rossproject.toml file in the specified directory.
    2. Create the package files and folders if they don't exist.
    NOTE: This function is intended to be run with one argument (package name) with CLI.
    But the second argument is included for flexibility, and for testing purposes."""
    # Ensure there is a .git file in this folder
    rossproject_toml_path = os.path.join(package_folder_path, "rossproject.toml")
    package_folder_path = os.path.dirname(rossproject_toml_path)
    git_file_path = os.path.join(package_folder_path, '.git')
    if not os.path.exists(git_file_path):
        typer.echo("This folder does not contain a git repo! Please create one first.")
        raise typer.Exit()
    
    repository_url = get_remote_url_from_git_repo(package_folder_path)
    if repository_url is None:
        typer.echo("This folder does not contain a remote GitHub repository! Please create one first.")
        raise typer.Exit()
    
    # If no package name provided, automatically set it.
    if package_name is None or package_name == "":        
        url_parts = repository_url.split("/")
        repo_name = url_parts[-1]
        package_name = repo_name.replace(".git", "") # Remove the '.git' suffix

    # Replace hyphens with underscores in the package name
    package_name = convert_hyphen_in_name_to_underscore(package_name)  
    
    # Create the rossproject.toml file
    if os.path.exists(rossproject_toml_path):
        typer.echo("rossproject.toml file already exists in current directory.")
    else:    
        # Write a new rossproject.toml file        
        toml_str_content = DEFAULT_ROSSPROJECT_TOML_STR.format(DEFAULT_PACKAGE_NAME=package_name)
        with open(rossproject_toml_path, "wb") as f:
            f.write(toml_str_content.encode("utf-8"))
        typer.echo(f"rossproject.toml file created at {rossproject_toml_path}.")

    # Create the package structure. Only if the files/folders don't already exist
    for field, path in INIT_PATHS.items():
        full_path = os.path.join(package_folder_path, path)
        if not os.path.exists(full_path):
            if field.endswith("/"):
                os.makedirs(full_path, exist_ok=True)
                typer.echo(f"Created folder: {field}")
            else:
                # Create a blank file
                with open(full_path, "w") as f:
                    f.write("")
                typer.echo(f"Created file: {field}")

    # Continue initializing the project structure.
    # Create the project name subfolder, and the __init__.py file.
    project_name_subfolder = os.path.join(package_folder_path, INIT_PATHS["src/"], package_name)
    os.makedirs(project_name_subfolder, exist_ok=True)
    init_py_file = os.path.join(project_name_subfolder, '__init__.py')
    with open(init_py_file, 'w') as f:
        f.write("")

    # Initialize the content of the .gitignore, one per line
    gitignore_content = f""".DS_Store
src/site-packages/*
.venv/    
    """
    with open(os.path.join(package_folder_path, INIT_PATHS[".gitignore"]), 'w') as f:
        f.write(gitignore_content)

    typer.echo("\nROSS project initialized successfully.")