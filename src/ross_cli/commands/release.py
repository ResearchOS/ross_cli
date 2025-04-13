import os
import subprocess
import re

import tomli
import tomli_w
import typer

from ..constants import *
from ..git.index import get_package_remote_url
from ..utils.urls import is_valid_url, check_url_exists

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
        version = chars_before + new_num + chars_after
        rossproject_toml["version"] = version

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

    # Write the pyproject.toml file
    with open(DEFAULT_PYPROJECT_TOML_PATH, "wb") as f:
        tomli_w.dump(pyproject_toml_content, f)

    # Write the updated version number back to the rossproject.toml file.
    with open(DEFAULT_ROSSPROJECT_TOML_PATH, 'wb') as f:
        tomli_w.dump(rossproject_toml, f)

    # git push
    subprocess.run(["git", "add", DEFAULT_PYPROJECT_TOML_PATH, DEFAULT_ROSSPROJECT_TOML_PATH], check=True)
    subprocess.run(["git", "commit", "-m", f"Updating version to {rossproject_toml['version']}"])
    try:
        subprocess.run(["git", "push"], check=True)
    except:
        typer.echo("Failed to `git push`, likely because you do not have permission to push to this repository.")
        typer.echo("Try opening a pull request instead, or contact the repository's maintainer(s) to change your permissions.")
        raise typer.Exit()

    # GitHub release
    try:
        subprocess.run(["gh", "--version"], capture_output=True)
    except:
        typer.echo("`gh` CLI not found. Check the official repository for more information: https://github.com/cli/cli")
        raise typer.Exit()
    tag = "v" + version
    result = subprocess.run(["gh", "release", "create", tag], check=True, capture_output=True)
    release_url = result.stdout.strip()
    typer.echo(f"Successfully released to {release_url}")


def build_pyproject_from_rossproject(rossproject_toml: dict) -> dict:
    """Build the pyproject.toml file from the rossproject.toml file."""
    pyproject_toml = {}
    pyproject_toml["project"]  = {}
    pyproject_toml["project"]["name"] = rossproject_toml["name"] if "name" in rossproject_toml else None
    pyproject_toml["project"]["version"] = rossproject_toml["version"] if "version" in rossproject_toml else None
    pyproject_toml["project"]["description"] = rossproject_toml["description"] if "description" in rossproject_toml else None    
    pyproject_toml["project"]["authors"] = rossproject_toml["authors"] if "authors" in rossproject_toml else None
    pyproject_toml["project"]["readme"] = rossproject_toml["readme"] if "readme" in rossproject_toml else None

    # Validate language    
    if rossproject_toml["language"].lower() not in SUPPORTED_LANGUAGES:
        typer.echo(f"Language {rossproject_toml['language']} not supported.")
        typer.echo(f"Supported languages are: {', '.join(SUPPORTED_LANGUAGES)}")
        raise typer.Exit()

    # Set the language
    pyproject_toml["tool"] = {}
    pyproject_toml["tool"][CLI_NAME] = {}
    pyproject_toml["tool"][CLI_NAME]["language"] = rossproject_toml["language"].lower()

    # Define the dependencies based on the language
    dependencies, tool_dependencies = parse_dependencies(rossproject_toml["dependencies"], rossproject_toml["language"])
    pyproject_toml["project"]["dependencies"] = dependencies
    pyproject_toml["tool"][CLI_NAME]["dependencies"] = tool_dependencies

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

def parse_dependencies(dependencies: list, language: str) -> tuple[list, list]:
    """Parse the dependencies from the rossproject.toml file.
    Returns the project.dependencies list for ROSS packages (any language) & non-ROSS Python packages.
    Returns the tool.ROSS.dependencies list for non-ROSS MATLAB and R packages."""
    deps = []
    tool_deps = []    
    for dep in dependencies:
        # All languages: If package name in a ROSS index, put the .git URL in project.dependencies
        remote_url = get_package_remote_url(dep)
        if remote_url is not None:
            if not remote_url.endswith(".git"):
                remote_url = remote_url + ".git"
            deps.append(remote_url)
            continue

        if language == "python":        
            # If package name in PyPi, just put the package name in project.dependencies like standard
            if check_package_exists_on_pypi(dep):
                tool_deps.append(dep)
        elif language == "r":
            if is_valid_url(dep):
                url = dep
            else:
                # If package name in CRAN, put package name in tool.ROSS.dependencies.
                url = f"https://cran.r-project.org/web/packages/{dep}/index.html"
            if check_url_exists(url):
                tool_deps.append(dep)
            else:
                typer.echo("R package not found in CRAN")
                raise typer.Exit()
        elif language == "matlab":
            # If .git URL exists, put URL in tool.ROSS.dependencies
            if check_url_exists(dep):
                tool_deps.append(dep)
            else:
                typer.echo(f"URL not found: {dep}")
                raise typer.Exit()
            
        return deps, tool_deps
    

def check_package_exists_on_pypi(package_name: str) -> bool:
    """
    Check if a package exists on PyPI using only built-in libraries.
    
    Args:
        package_name (str): The name of the package to check
    
    Returns:
        bool: True if the package name exists, False otherwise.
    """
    url = f"https://pypi.org/pypi/{package_name}/json"    
    return check_url_exists(url)