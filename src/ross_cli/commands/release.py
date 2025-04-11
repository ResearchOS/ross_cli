import os
import subprocess
import re

import tomli
import tomli_w
import typer

from ..constants import *

def release(release_type: str = None):
    """Release a new version of the package on GitHub."""
    # Create the pyproject.toml file from the rossproject.toml file.
    if not os.path.exists(DEFAULT_ROSSPROJECT_TOML_PATH):
        typer.echo("Missing rossproject.toml file")
        raise typer.Exit()
    with open(DEFAULT_ROSSPROJECT_TOML_PATH, "rb") as f:
        rossproject_toml = tomli.load(f)

    if not re.match(SEMANTIC_VERSIONING_REGEX, rossproject_toml["version"]):
        typer.echo("Version number does not follow semantic versioning! For example, 'v1.0.0'.")
        typer.echo("See https://semver.org for the full semantic versioning specification.")
        raise typer.Exit()

    version = rossproject_toml["version"]    
    if version[0] == "v":
        version = version[1:]
    dot_indices = [m.start() for m in re.finditer(r"\.", version)]
    if release_type == "patch":
        chars_before = version[0:dot_indices[1]+1]
        new_num = str(int(version[dot_indices[1]+1:]) + 1)
        chars_after = ""
    elif release_type == "minor":
        chars_before = version[0:dot_indices[0]+1]
        new_num = str(int(version[dot_indices[0]+1:dot_indices[1]]) + 1)
        chars_after = ".0"
    elif release_type == "major":
        chars_before = ""
        new_num = str(int(version[0:dot_indices[0]]) + 1)
        chars_after = ".0.0"
    
    if release_type is not None:
        rossproject_toml["version"] = chars_before + new_num + chars_after

    # Get the new pyproject_toml data
    pyproject_toml_new = build_pyproject_from_rossproject(rossproject_toml)
    if not os.path.exists(DEFAULT_PYPROJECT_TOML_PATH):
        pyproject_toml_content_orig = {}
    else:
        with open(DEFAULT_PYPROJECT_TOML_PATH, 'rb') as f:
            pyproject_toml_content_orig = tomli.load(f)

    # Overwrite the original data, preserving other fields that may have been added.
    pyproject_toml_content = pyproject_toml_content_orig
    for fld in pyproject_toml_new:
        pyproject_toml_content[fld] = pyproject_toml_new[fld]

    with open(DEFAULT_PYPROJECT_TOML_PATH, "wb") as f:
        tomli_w.dump(pyproject_toml_content, f)

    # git push
    subprocess.run(["git", "add", DEFAULT_PYPROJECT_TOML_PATH], check=True)
    subprocess.run(["git", "commit", "-m", f"Updating version to {rossproject_toml['version']}"])
    try:
        subprocess.run(["git", "push"], check=True)
    except:
        typer.echo("Failed to `git push`, likely because you do not have permission to push to this repository.")
        typer.echo("Try opening a pull request instead, or contact the repository's maintainer(s) to change your permissions.")
        return

    # GitHub release
    try:
        subprocess.run(["gh", "--version"], capture_output=True)
    except:
        typer.echo("`gh` CLI not found. Check the official repository for more information: https://github.com/cli/cli")
        return
    tag = "v" + version
    subprocess.run(["gh", "release", "create", tag], check=True)

    # Write the updated version number back to the rossproject.toml file.
    with open(DEFAULT_ROSSPROJECT_TOML_PATH, 'wb') as f:
        tomli_w.dump(rossproject_toml, f)


def build_pyproject_from_rossproject(rossproject_toml: dict) -> dict:
    """Build the pyproject.toml file from the rossproject.toml file."""
    pyproject_toml = {}
    pyproject_toml["project"]  = {}
    pyproject_toml["project"]["name"] = rossproject_toml["name"] if "name" in rossproject_toml else None
    pyproject_toml["project"]["version"] = rossproject_toml["version"] if "version" in rossproject_toml else None
    pyproject_toml["project"]["description"] = rossproject_toml["description"] if "description" in rossproject_toml else None
    pyproject_toml["project"]["dependencies"] = rossproject_toml["dependencies"] if "dependencies" in rossproject_toml else None
    pyproject_toml["project"]["authors"] = rossproject_toml["authors"] if "authors" in rossproject_toml else None
    pyproject_toml["project"]["readme"] = rossproject_toml["readme"] if "readme" in rossproject_toml else None

    pyproject_toml["build-system"] = {}
    pyproject_toml["build-system"]["requires"] = ["hatchling"]
    pyproject_toml["build-system"]["build-backend"] = "hatchling.build"

    any_missing = False
    for fld in pyproject_toml["project"]:
        if pyproject_toml["project"][fld] is None:
            typer.echo(f"rossproject.toml field {fld} is missing!")
            any_missing = True

    if any_missing:
        raise typer.Exit()

    return pyproject_toml