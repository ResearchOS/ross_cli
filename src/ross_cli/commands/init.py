import os

import typer

from ..constants import *
from ..git.github import get_remote_url_from_git_repo

def init_ross_project():
    """Initialize a new ROSS project in the current directory.
    1. Create a new rossproject.toml file in the current directory.
    2. Create the package files and folders if they don't exist."""
    if os.path.exists(DEFAULT_ROSSPROJECT_TOML_PATH):
        typer.echo("rossproject.toml file already exists in current directory.")
    else:
        # Create a new rossproject.toml file
        repository_url = get_remote_url_from_git_repo(".")
        # Remove the .git suffix from the URL
        if repository_url.endswith(".git"):
            repository_url = repository_url[:-4]
        toml_str_content = DEFAULT_ROSSPROJECT_TOML_STR.format(repository_url=repository_url, DEFAULT_PACKAGE_NAME=DEFAULT_PACKAGE_NAME)
        with open(DEFAULT_ROSSPROJECT_TOML_PATH, "wb") as f:
            f.write(toml_str_content.encode("utf-8"))
        typer.echo(f"rossproject.toml file created at {DEFAULT_ROSSPROJECT_TOML_PATH}.")

    # Create the package structure if the files/folders don't already exist
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

    typer.echo("\nROSS project initialized successfully.")