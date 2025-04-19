import os
import subprocess
import re
from importlib.metadata import version

import tomli
import tomli_w
import typer

from ..constants import *
from ..git.index import search_indexes_for_package_info
from ..git.github import read_github_file, get_default_branch_name
from ..utils.urls import is_valid_url, check_url_exists, convert_owner_repo_format_to_url, is_owner_repo_format
from ..utils.rossproject import load_rossproject

def release(release_type: str = None):
    """Release a new version of the package on GitHub."""
    # Create the pyproject.toml file from the rossproject.toml file.
    rossproject_toml = load_rossproject(DEFAULT_ROSSPROJECT_TOML_PATH)

    if not re.match(SEMANTIC_VERSIONING_REGEX, rossproject_toml["version"]):
        typer.echo("Version number does not follow semantic versioning! For example, 'v1.0.0'.")
        typer.echo("See https://semver.org for the full semantic versioning specification.")
        raise typer.Exit()

    version = rossproject_toml["version"]  
    v_char = ""  
    if version[0] == "v":
        v_char = "v"
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
        version = v_char + chars_before + new_num + chars_after
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
    try:
        subprocess.run(["git", "add", DEFAULT_PYPROJECT_TOML_PATH], check = True)
    except:
        pass
    try:
        subprocess.run(["git", "add", DEFAULT_ROSSPROJECT_TOML_PATH], check=True)
    except:
        pass
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
    tag = "v" + version if version[0] != "v" else version
    result = subprocess.run(["gh", "release", "create", tag], check=True, capture_output=True)
    release_url = str(result.stdout.strip())
    if release_url[0] == "b":
        release_url = release_url[1:]
    typer.echo(f"Successfully released to {release_url}")


def build_pyproject_from_rossproject(rossproject_toml: dict) -> dict:
    """Build the pyproject.toml file from the rossproject.toml file."""   

    if "name" not in rossproject_toml:
        typer.echo("'name' field missing from rossproject.toml file!")
        raise typer.Exit()
    
    # Check the name field
    if "-" in rossproject_toml["name"]:
        name = rossproject_toml['name']
        typer.echo(f"Package name {name} contains a '-'.")
        result = input("Replace '-' with '_'?(y/N)")
        if result.lower() in ["y", "yes"]:
            name = name.replace("-", "_")
            rossproject_toml['name'] = name
            with open(DEFAULT_ROSSPROJECT_TOML_PATH, 'wb') as f:
                tomli_w.dump(rossproject_toml, f)
        else:
            raise typer.Exit() 
    
    pyproject_toml = {}
    pyproject_toml["project"]  = {}
    pyproject_toml["project"]["name"] = rossproject_toml["name"] if "name" in rossproject_toml else None
    pyproject_toml["project"]["version"] = rossproject_toml["version"] if "version" in rossproject_toml else None     
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
        typer.echo("Failed to update pyproject.toml file from rossproject.toml file.")
        raise typer.Exit()

    return pyproject_toml


def parse_dependencies(dependencies: list, language: str) -> tuple[list, list]:
    """Parse the dependencies from the rossproject.toml file.
    Returns the project.dependencies list for ROSS packages (any language) & non-ROSS Python packages.
    Returns the tool.ROSS.dependencies list for non-ROSS MATLAB and R packages.
    NOTE: Currently, R packages hosted on CRAN do not have version numbers auto appended"""
    deps = []
    tool_deps = []
    any_invalid = False # True if any of the dependencies are specified in an invalid manner/are not found.
    for dep in dependencies:
        # All languages: If package name in a ROSS index, put the .git URL in project.dependencies
        ross_pkg_info = search_indexes_for_package_info(dep)
        if ross_pkg_info is not None:
            dep = ross_pkg_info["url"]

        # Convert owner/repo format to URL, and add version number
        if is_owner_repo_format(dep):
            dep = convert_owner_repo_format_to_url(dep)
        if is_valid_url(dep):
            dep = add_version_number_to_dep(dep)

        # Put the ROSS package's URL into the project.dependencies table.
        if ross_pkg_info is not None:
            deps.append(dep)
            continue

        if language == "python":        
            # Specified PyPi package name
            if check_package_exists_on_pypi(dep):
                deps.append(dep)
            # Specified GitHub repository URL
            elif check_url_exists(dep):
                # 1. Check if pyproject.toml file exists at URL
                split_url = dep.split('/releases/tag/')
                repo_url = split_url[0]
                tag = split_url[1]
                pyproject_url = f"{repo_url}/blob/{tag}/pyproject.toml"                
                pyproject_toml_exists = check_url_exists(pyproject_url)
                if not pyproject_toml_exists:
                    typer.echo(f"Invalid dependency specification, missing pyproject.toml file in Python package: {dep}")
                    any_invalid = True
                    continue
                # 2. Read pyproject.toml file to get package name
                pyproject = read_github_file(pyproject_url, tag = tag)
                dep_package_name = pyproject["project"]["name"]
                full_dep = dep_package_name + " @ git+" + dep
                deps.append(full_dep)
        elif language == "r":
            # Specified as a GitHub repository or CRAN URL
            if check_url_exists(dep):                
                url = dep                            
            # CRAN package name specified
            else:
                url = f"https://cran.r-project.org/web/packages/{dep}/index.html"            
            if not check_url_exists(url):
                typer.echo(f"Invalid dependency specification, R package not found on GitHub or CRAN: {dep}")
                any_invalid = True
            tool_deps.append(url)
        elif language == "matlab":
            # GitHub repository URL specified
            if check_url_exists(dep):
                tool_deps.append(dep)
            else:
                typer.echo(f"Invalid dependency specification. Invalid MATLAB package GitHub repository URL: {dep}")
                any_invalid = True

    if any_invalid:
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

    package_name = strip_package_version_from_name(package_name)
    url = f"https://pypi.org/pypi/{package_name}/json"
    
    return check_url_exists(url)

def strip_package_version_from_name(package_name_with_version: str) -> str:
    """Return the package name without the version

    Args:
        package_name_with_version (str): The name of a package with its version specifier

    Returns:
        str: _description_
    """

    def find_first_version_char(text: str) -> int:
        first_index = len(text)  # Default to end of string if none found
        for char in POSSIBLE_VERSION_CHARS:
            pos = text.find(char)
            if pos != -1 and pos < first_index:
                first_index = pos
        return first_index if first_index < len(text) else -1
    
    first_version_char_index = find_first_version_char(package_name_with_version)
    return package_name_with_version[0:first_version_char_index]

def add_version_number_to_dep(dep: str) -> str:
    """Make sure that the dependency has a version number associated with it."""

    # Prep the dependency with the proper version number
    if is_valid_url(dep):
        # If specified as URL, it's because it's not in a packaging index.
        version_after_at = None
        if "@" in dep:
            version_after_at = dep[dep.index("@")+1:]
            dep = dep[0:dep.index("@")] # Remove the substring after "@"
        else:
            typer.echo("Version for URL-based packages must be specified in this format:")
            typer.echo("https://github.com/owner/repo.git@v1.0.0")
            raise typer.Exit()
        dep = dep.replace(".git", "")
        url = dep + f"/releases/tag/{version_after_at}"      
        url_exists = True             
        if not check_url_exists(url):
            url_exists = False
            if not version_after_at.startswith('v'):
                version_after_at_with_v = "v" + version_after_at
                url_with_v = dep + f"/releases/tag/{version_after_at_with_v}"                      
                url_exists = True
                if not check_url_exists(url_with_v):
                    url_exists = False
                else:
                    dep = url_with_v
        else:
            dep = url
        if url_exists is False:
            typer.echo(f"URL does not exist: {url}")
            raise typer.Exit()
    elif re.match(SEMANTIC_VERSIONING_REGEX, dep) is None:
        # In PyPI         
        package_version = version(dep)
        package_name = strip_package_version_from_name(dep)
        dep = package_name + "==" + package_version
    else:
        typer.echo("Invalid dependency specification. Must either be a valid GitHub repository URL, or a package name in PyPI")
        raise typer.Exit()
    
    return dep