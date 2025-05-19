
import typer
import tomli

from ..constants import *

def load_rossproject(rossproject_toml_path: str) -> dict:
    """Load the rossproject.toml from file and validate it."""
    # Check if the file exists
    if not os.path.exists(rossproject_toml_path):
        typer.echo(f"File does not exist: {rossproject_toml_path}")
        raise typer.Exit()
    
    # Load the file.
    with open(rossproject_toml_path, 'rb') as f:
        rossproject = tomli.load(f)

    # Validate the file contents
    fields_ok = True
    for field in ROSSPROJECT_REQUIRED_FIELDS:
        if field not in rossproject:
            typer.echo(f"Missing field '{field}' from {rossproject_toml_path}")
            fields_ok = False

    if not fields_ok:
        raise typer.Exit()
    
    return rossproject


def convert_hyphen_in_name_to_underscore(name: str) -> str:
    """Convert hyphen in package name to underscore"""
    corrected_name = name.replace("-", "_")
    return corrected_name