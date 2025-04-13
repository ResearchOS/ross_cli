import os

import typer

from ..constants import *
from ..git.github import get_remote_url_from_git_repo

def init_ross_project(package_name: str):
    """Initialize a new ROSS project in the current directory.
    1. Create a new rossproject.toml file in the current directory.
    2. Create the package files and folders if they don't exist."""
    # Ensure there is a .git file in this folder
    folder_name = os.path.dirname(DEFAULT_ROSSPROJECT_TOML_PATH)
    git_file_path = os.path.join(folder_name, '.git')
    if not os.path.exists(git_file_path):
        typer.echo("This folder does not contain a git repo! Please create one first.")
        raise typer.Exit()
    
    # Create the README.md file so there's something to commit
    readme_key = "README.md"
    if readme_key in INIT_PATHS:
        if not os.path.exists(INIT_PATHS[readme_key]):
            with open(INIT_PATHS[readme_key], "w") as f:
                f.write("")
        del INIT_PATHS[readme_key] # So the README isn't overwritten.
    
    repository_url = get_remote_url_from_git_repo(".")
    
    # If no package name provided, automatically set it.
    if package_name is None:        
        url_parts = repository_url.split("/")
        repo_name = url_parts[-1]
        package_name = repo_name[:-4] # Remove the '.git' suffix
    
    # Create the rossproject.toml file
    if os.path.exists(DEFAULT_ROSSPROJECT_TOML_PATH):
        typer.echo("rossproject.toml file already exists in current directory.")
    else:
        # Remove the .git suffix from the URL
        repository_url_no_git = repository_url[:-4]
        # Write a new rossproject.toml file        
        toml_str_content = DEFAULT_ROSSPROJECT_TOML_STR.format(repository_url=repository_url_no_git, DEFAULT_PACKAGE_NAME=package_name)
        with open(DEFAULT_ROSSPROJECT_TOML_PATH, "wb") as f:
            f.write(toml_str_content.encode("utf-8"))
        typer.echo(f"rossproject.toml file created at {DEFAULT_ROSSPROJECT_TOML_PATH}.")

    # Create the package structure. Only if the files/folders don't already exist
    for field, path in INIT_PATHS.items():
        if not os.path.exists(path):
            if field.endswith("/"):
                os.makedirs(path, exist_ok=True)
                typer.echo(f"Created folder: {field}")
            else:
                # Create a blank file
                with open(path, "w") as f:
                    f.write("")
                typer.echo(f"Created file: {field}")

    # Continue initializing the project structure.
    # Create the project name subfolder, and the __init__.py file.
    project_name_subfolder = os.path.join(INIT_PATHS["src/"], package_name)
    os.makedirs(project_name_subfolder, exist_ok=True)
    init_py_file = os.path.join(project_name_subfolder, '__init__.py')
    with open(init_py_file, 'w') as f:
        f.write("")

    typer.echo("\nROSS project initialized successfully.")