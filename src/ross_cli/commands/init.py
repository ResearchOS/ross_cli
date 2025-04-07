import os

import tomli_w
import typer

from ..constants import *

def init_ross_project():
    """Initialize a new ROSS project in the current directory.
    1. Create a new rossproject.toml file in the current directory.
    2. Create the package files and folders if they don't exist."""
    if os.path.exists(DEFAULT_ROSSPROJECT_TOML_PATH):
        typer.echo("rossproject.toml file already exists in current directory.")
    else:
        # Create a new rossproject.toml file
        with open(DEFAULT_ROSSPROJECT_TOML_PATH, "w") as f:
            tomli_w.dump(DEFAULT_ROSSPROJECT_TOML_CONTENT, f)
        typer.echo(f"rossproject.toml file created at {DEFAULT_ROSSPROJECT_TOML_PATH}.")

    # Create the package structure if the files/folders don't already exist
    for field, path in INIT_PATHS.items():
        if not os.path.exists(path):
            if field.endswith("/"):
                os.makedirs(path, exist_ok=True)
            else:
                # Create a blank file
                with open(path, "w") as f:
                    f.write("")