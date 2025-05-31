import os
import subprocess
import re
from importlib.metadata import version
import json
import urllib.request
from urllib.error import URLError, HTTPError

import tomli
import tomli_w
import typer

from ..constants import *
from ..git.index import search_indexes_for_package_info
from ..git.github import read_github_file_from_release, get_latest_release_tag, parse_github_url, get_remote_url_from_git_repo
from ..utils.urls import is_valid_url, check_url_exists, convert_owner_repo_format_to_url, is_owner_repo_format
from ..utils.rossproject import load_rossproject, convert_hyphen_in_name_to_underscore

def release(release_type: str = None, package_folder_path: str = os.getcwd(), message: str = None):
    """Release a new version of the package on GitHub.""" 
    # Switch to the package folder
    os.chdir(package_folder_path)   
    if not os.path.exists(package_folder_path):
        typer.echo(f"Folder {package_folder_path} does not exist.")
        raise typer.Exit()
    # Create the pyproject.toml file from the rossproject.toml file.
    rossproject_toml_path = os.path.join(package_folder_path, "rossproject.toml")
    pyproject_toml_path = os.path.join(package_folder_path, "pyproject.toml")
    rossproject_toml = load_rossproject(rossproject_toml_path)

    if not re.match(SEMANTIC_VERSIONING_REGEX, rossproject_toml["version"]):
        typer.echo("Version number does not follow semantic versioning! For example, 'v1.0.0'.")
        typer.echo("See https://semver.org for the full semantic versioning specification.")
        raise typer.Exit()

    previous_version = rossproject_toml["version"]  
    version = increment_version(previous_version, release_type)    
    rossproject_toml["version"] = version    

    # Get the new pyproject_toml data
    pyproject_toml_new = build_pyproject_from_rossproject(rossproject_toml)
    if not os.path.exists(pyproject_toml_path):
        pyproject_toml_content_orig = {}
    else:
        with open(pyproject_toml_path, 'rb') as f:
            pyproject_toml_content_orig = tomli.load(f)

    # Overwrite the original data, preserving other fields that may have been added.
    pyproject_toml_content = pyproject_toml_content_orig
    for fld in pyproject_toml_new:
        pyproject_toml_content[fld] = pyproject_toml_new[fld]        

    # Write the pyproject.toml file
    with open(pyproject_toml_path, "wb") as f:
        tomli_w.dump(pyproject_toml_content, f)

    # Write the updated version number back to the rossproject.toml file.
    with open(rossproject_toml_path, 'wb') as f:
        tomli_w.dump(rossproject_toml, f)
        
    # git push    
    try:        
        subprocess.run(["git", "add", pyproject_toml_path], check = True)
    except:
        pass
    try:
        subprocess.run(["git", "add", rossproject_toml_path], check=True)
    except:
        pass
    subprocess.run(["git", "commit", "-m", f"Update version to {rossproject_toml['version']}"])
    try:
        subprocess.run(["git", "push"], check=True)
    except:
        typer.echo("Failed to `git push`, likely because you do not have permission to push to this repository.")
        typer.echo("Try opening a pull request instead, or contact the repository's maintainer(s) to change your permissions.")
        raise typer.Exit()
    
    if message is None:
        message = f"Release {rossproject_toml['version']}"

    # GitHub release
    try:
        subprocess.run(["gh", "--version"], capture_output=True)
    except:
        typer.echo("`gh` CLI not found. Check the official repository for more information: https://github.com/cli/cli")
        raise typer.Exit()
    tag = "v" + version if version[0] != "v" else version
    repo_url = get_remote_url_from_git_repo(package_folder_path)
    owner, repo, _ = parse_github_url(repo_url)
    release_url_to_check = f"https://github.com/{owner}/{repo}/releases/tag/{tag}"
    if check_url_exists(release_url_to_check):
        typer.echo(f"Aborting release. Release {tag} already exists at: {release_url_to_check}")
        raise typer.Exit(code=6)
    result = subprocess.run(["gh", "release", "create", tag, "-n", message], check=True, capture_output=True)
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
    converted_name = convert_hyphen_in_name_to_underscore(rossproject_toml["name"])            
    rossproject_toml["name"] = converted_name
    
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

    # hatch settings
    pyproject_toml["tool"]["hatch"] = {}
    pyproject_toml["tool"]["hatch"]["metadata"] = {}
    pyproject_toml["tool"]["hatch"]["metadata"]["allow-direct-references"] = True

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
        processed_dep, processed_tool_dep = parse_dependency(dep, language)
        if processed_dep is None and processed_tool_dep is None:
            any_invalid = True
            continue
        if processed_dep:
            deps.extend([processed_dep])
        if processed_tool_dep:
            tool_deps.extend([processed_tool_dep])                

    if any_invalid:
        raise typer.Exit()
            
    return deps, tool_deps


def parse_dependency(dep: str, language: str) -> tuple[list, list]:
    """Parse a single dependency from the rossproject.toml file."""
    processed_dep = []
    processed_tool_dep = []
    # All languages: If package is in a ROSS index, put the .git URL in project.dependencies    
    ross_pkg_info = search_indexes_for_package_info(dep)
    is_ross_pkg = False
    if ross_pkg_info is not None:
        is_ross_pkg = True

    # ROSS package specified (name or URL). Put the ROSS package's URL into the project.dependencies table.
    if is_ross_pkg:
        dep = ross_pkg_info["url"].replace(".git", "")        

    # Non-ROSS package specified (name, owner/repo, or URL).
    processed_dep, processed_tool_dep = process_non_ross_dependency(dep, language)
    return processed_dep, processed_tool_dep

def process_non_ross_dependency(dep: str, language: str) -> tuple[list, list]:
    """Process a non-ROSS dependency from the simpler form in the rossproject.toml file to the more complex form in the pyproject.toml file."""
    processed_dep = []
    processed_tool_dep = []
    # Convert owner/repo format to URL
    if is_owner_repo_format(dep):
        dep = convert_owner_repo_format_to_url(dep)
    # Add version number to the dependency    
    dep_with_version = add_version_number_to_dep(dep)
    dep_without_version = strip_package_version_from_name(dep_with_version)
    version = get_version_from_dep(dep_with_version)

    # Dependencies specified as URLs
    if check_url_exists(dep_without_version):
        formatted_dep = format_dep_pyproject_with_version(dep_without_version, version)
        if formatted_dep is None:
            formatted_dep = f"{dep_without_version}/releases/tag/{version}"

        if not check_url_exists(formatted_dep):
            typer.echo(f"Invalid dependency specification, URL does not exist: {formatted_dep}")
            return None, None
        if language == "r" or language == "matlab":
            processed_tool_dep = formatted_dep
        else:
            processed_dep = formatted_dep
        return processed_dep, processed_tool_dep

    if language == "python":        
        # Specified PyPi package name
        if check_package_exists_on_pypi(dep_with_version):
            processed_dep = dep_with_version        
    elif language == "r":                   
        # CRAN package name specified
        url = f"https://cran.r-project.org/web/packages/{dep_with_version}/index.html"            
        if not check_url_exists(url):
            typer.echo(f"Invalid dependency specification, R package not found on GitHub or CRAN: {dep}")
            return None, None
        processed_tool_dep = url
    elif language == "matlab":
        # Package name specified
        typer.echo(f"Invalid dependency specification. Invalid MATLAB package GitHub repository URL: {dep}")
        return None, None

    return processed_dep, processed_tool_dep


def format_dep_pyproject_with_version(dep_without_version: str, version: str) -> str:
    # 1. Check if pyproject.toml file exists at URL
    repo_url = dep_without_version
    tag = version
    pyproject_url = f"{repo_url}/blob/{tag}/pyproject.toml"                
    pyproject_toml_exists = check_url_exists(pyproject_url)
    if not pyproject_toml_exists:
        typer.echo(f"Invalid dependency specification, missing pyproject.toml file in package: {dep_without_version}")
        return None
    # 2. Read pyproject.toml file to get package name
    pyproject_str = read_github_file_from_release(pyproject_url, tag = tag)
    pyproject = tomli.loads(pyproject_str)
    dep_package_name = pyproject["project"]["name"]
    processed_dep = dep_package_name + " @ git+" + dep_without_version + "@" + tag
    return processed_dep
    

def check_package_exists_on_pypi(package_name: str) -> bool:
    """
    Check if a package exists on PyPI using only built-in libraries.
    
    Args:
        package_name (str): The name of the package to check
    
    Returns:
        bool: True if the package name exists, False otherwise.
    """      

    version = get_version_from_dep(package_name)
    if version is None:
        version = ""
    package_name_no_version = strip_package_version_from_name(package_name)
    url = f"https://pypi.org/pypi/{package_name_no_version}/{version}"
    
    return check_url_exists(url)


def find_first_version_char(text: str) -> int:
    """Find the first occurrence of a version character in the text."""
    first_index = len(text)  # Default to end of string if none found
    for char in POSSIBLE_VERSION_CHARS:
        pos = text.find(char)
        if pos != -1 and pos < first_index:
            first_index = pos
    return first_index


def strip_package_version_from_name(package_name_with_version: str) -> str:
    """Return the package name without the version

    Args:
        package_name_with_version (str): The name of a package with its version specifier

    Returns:
        str: _description_
    """    
    
    first_version_char_index = find_first_version_char(package_name_with_version)
    return package_name_with_version[0:first_version_char_index]


def get_version_from_dep(dep: str) -> str:
    """Return the version number from the dependency string."""
    if "@" in dep:
        # If the dependency is a GitHub repository URL, the version number is after the "@"
        version = dep[dep.index("@")+1:]
    else:
        # If the dependency is a PyPI package, the version number is after the first version character
        first_version_char_index = find_first_version_char(dep)
        if first_version_char_index == len(dep):
            # If no version character is found, return None
            return None
        dep = dep[first_version_char_index:]
        # Find the first numeric character in the dependency string
        first_numeric_char_index = re.search(r"\d", dep)
        if first_numeric_char_index is None:
            # If no numeric character is found, return None
            return None
        # Extract the version number from the dependency string
        version = dep[first_numeric_char_index.start():]

    return version


def add_version_number_to_dep(dep: str) -> str:
    """Return the dependency formatted with the version number.
    If the dependency is a GitHub repository, it will be formatted as:
    'https://github.com/owner/repo/.git@<version>'.
    If the dependency is a PyPI package, it will be formatted as:
    '<package_name>==<version>'
    """

    version_num = get_version_from_dep(dep)
    if version_num is not None:
        # If the version number is already specified, return the dependency as is
        return dep

    github_url_string = "https://github.com/{owner}/{repo}/releases/tag/{version}"
    # Prep the dependency with the proper version number
    if is_valid_url(dep):
        # If specified as URL, it's because it's not in a packaging index.
        version_after_at = None
        if "@" in dep:
            version_after_at = dep[dep.index("@")+1:]
            url = dep
            dep = dep[0:dep.index("@")] # Remove the substring after "@"
        else:
            owner, repo, _ = parse_github_url(dep)
            version_after_at = get_latest_release_tag(owner, repo)
            url = github_url_string.format(owner=owner, repo=repo, version=version_after_at)
                 
        url_exists = True             
        if check_url_exists(url):
            dep = f"https://github.com/{owner}/{repo}@{version_after_at}"
        else:
            url_exists = False
            if not version_after_at.startswith('v'):
                version_after_at_with_v = "v" + version_after_at
                url_with_v = dep + f"/releases/tag/{version_after_at_with_v}"                      
                url_exists = True
                if not check_url_exists(url_with_v):
                    url_exists = False
                else:
                    url = github_url_string.format(owner=owner, repo=repo, version=version_after_at_with_v)
            
        if url_exists is False:
            typer.echo(f"URL does not exist: {url}")
            raise typer.Exit()
    else:
        # In PyPI
        try:
            # If the package is installed, get the version from the installed package
            package_version = version(dep)
        except ModuleNotFoundError or ImportError:
            # If the package is not installed, get the version from PyPI
            package_version = get_version_from_pypi(dep)
        
        if package_version is None:
            # If the package is not found, raise an error
            typer.echo(f"Package {dep} not installed or found on PyPI. Aborting release.")
            raise typer.Exit(code = 3)
        
        package_name = strip_package_version_from_name(dep)
        dep = package_name + "==" + package_version
    
    return dep

def get_version_from_pypi(package_name: str) -> str:
    """Get the version number from PyPI for a given package name."""
    try:
        versions = list_package_versions(package_name)
        if not versions:
            raise ValueError("No versions found")
        # Get the latest version
        version = versions[-1]
    except:
        # If the package is not found, raise an error
        version = None
    
    return version

def list_package_versions(package_name):
    """
    List all available versions of a package on PyPI using only standard library.
    
    Args:
        package_name (str): The name of the package
        
    Returns:
        list: Sorted list of available versions
    """
    url = f"https://pypi.org/pypi/{package_name}/json"
    
    try:
        # Open connection to PyPI
        with urllib.request.urlopen(url) as response:
            # Read and decode the response
            data = response.read().decode('utf-8')
            
            # Parse JSON response
            package_data = json.loads(data)
            
            # Extract and sort versions
            versions = list(package_data.get("releases", {}).keys())
            
            # Sort versions numerically (e.g., 1.10.0 comes after 1.2.0)
            def version_key(v):
                try:
                    return [int(x) for x in v.split('.')]
                except ValueError:
                    # Handle non-numeric version parts
                    return [0]
                    
            versions.sort(key=version_key)
            
            return versions
            
    except HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        return []
    except URLError as e:
        print(f"URL Error: {e.reason}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
    

def increment_version(version: str, release_type: str) -> str:
    """Increment the version number based on the release type.
    The version number is expected to be in the format 'vX.Y.Z' or 'X.Y.Z'.
    The release type can be 'major', 'minor', or 'patch'.

    Args:
        version (str): Semantic versioning string
        release_type (str): "major", "minor", or "patch"

    Returns:
        str: The incremented version number
    """
    if release_type is None:
        return version
    
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
    
    version = v_char + chars_before + new_num + chars_after

    return version