import os
import subprocess
import base64
import re

import tomli
import tomli_w
import typer

from ..constants import *
from ..git.github import get_remote_url_from_git_repo, read_github_file_from_release, get_default_branch_name, parse_github_url, create_empty_file_in_repo
from ..utils.config import load_config
from ..utils.rossproject import load_rossproject
from ..utils.urls import check_url_exists, is_owner_repo_format, is_valid_url, remove_blob_and_branch_from_url
    
def add_to_index(index_file_url: str, package_folder_path: str, _config_file_path: str = DEFAULT_ROSS_CONFIG_FILE_PATH) -> None:
    """Add the specified package to the specified index.
    The index file URL should manipulated to be of the form: https://github.com/owner/repo/blob/default_branch/index.toml
    It can be specified as any of:
    1. The GitHub repo URL
    2. The GitHub owner/repo
    3. The URL to the index.toml file, e.g. https://github.com/owner/repo/index.toml
    4. The URL with the branch name, e.g. https://github.com/owner/repo/blob/default_branch/index.toml""" 
    ###################################################################   
    ########## Check that the preconditions are met ###################
    ###################################################################    

    # Check if the package folder path is valid
    if not os.path.exists(package_folder_path):
        typer.echo(f"Folder {package_folder_path} does not exist.")
        raise typer.Exit()
    if not os.path.isdir(package_folder_path):
        typer.echo(f"Path {package_folder_path} is not a directory.")
        raise typer.Exit()

    # Check if the package folder is a git repository
    if not os.path.exists(os.path.join(package_folder_path, ".git")):
        typer.echo(f"Folder {package_folder_path} is not a git repository.")
        raise typer.Exit()
    
    # Check for the rossproject.toml file
    rossproject_toml_path = os.path.join(package_folder_path, "rossproject.toml")
    if not os.path.exists(rossproject_toml_path):
        typer.echo(f"Folder {package_folder_path} is missing a rossproject.toml file")
        raise typer.Exit()    
    
    ########### Check if the index file URL is valid ######################
    # Make sure the index_file_url is a properly formatted URL to the index.toml file.    
    index_file_url = index_file_url.replace(".git", "")
    file_path = None    
    if is_owner_repo_format(index_file_url):
        parts = index_file_url.split("/")
        owner = parts[0]
        repo = parts[1]        
    elif is_valid_url(index_file_url):
        owner, repo, file_path = parse_github_url(index_file_url)
    else:
        typer.echo("Improperly formatted index specification!")
        raise typer.Exit()
    if file_path is None:   
        file_path = "index.toml"

    repo_url = f"https://github.com/{owner}/{repo}"
    if not re.search(BLOB_BRANCH_REGEX, index_file_url):
        branch_name = get_default_branch_name(repo_url)
        index_file_url = f"https://github.com/{owner}/{repo}/blob/{branch_name}/{file_path}"
    else:
        index_file_url = f"https://github.com/{owner}/{repo}/{file_path}"

    # Check if the index file URL exists
    if not check_url_exists(index_file_url):
        typer.echo(f"Index file URL {index_file_url} does not exist. Creating a new index file.")
        index_file_url_no_branch = remove_blob_and_branch_from_url(index_file_url)
        owner, repo, file_path = parse_github_url(index_file_url_no_branch)
        index_remote_url = f"https://github.com/{owner}/{repo}.git"
        index_relative_path = file_path
        try:
            create_empty_file_in_repo(index_remote_url, index_relative_path)
        except subprocess.CalledProcessError as e:
            typer.echo(f"Failed to create index file: {e}")
            raise typer.Exit()
    
    ####### Check that the config has the specified index in it #######
    config = load_config(_config_file_path)
    if "index" not in config or len(config["index"]) == 0:
        typer.echo(f"No indexes found in the config file.")
        raise typer.Exit()
    index_file_url_in_config = False
    for index in config["index"]:
        if repo_url + ".git" in index["url"]:
            index_file_url_in_config = True
            break
    if not index_file_url_in_config:
        owner, repo, _ = parse_github_url(index_file_url)
        url = f"https://github.com/{owner}/{repo}"
        typer.echo(f"Index file URL {url} is not tapped!")
        typer.echo(f"Please tap the index using the command: `ross tap {url}`")
        raise typer.Exit(code=5)

    # Get the package name from the rossproject.toml file    
    rossproject_content = load_rossproject(rossproject_toml_path)
    package_name = rossproject_content["name"]
    
    # Get the remote URL from the git repository
    remote_url = get_remote_url_from_git_repo(package_folder_path)

    # Download the content of the index.toml file directly from GitHub.
    index_content = tomli.loads(read_github_file_from_release(index_file_url))

    if "package" not in index_content:
        index_content["package"] = []

    # Check if the package is already in the index
    for package in index_content["package"]:
        if remote_url == package["url"]:    
            typer.echo(f"Package {package_name} already exists in the index.")    
            raise typer.Exit(2)    
    
    # Add the package to the index
    index_content["package"].append(
        {
            "name": package_name,
            "url": remote_url
        }
    )

    # Configuration
    if branch_name is None:
        branch_name = get_default_branch_name(index_file_url.replace("/index.toml", ""))
    index_file_url_no_https = index_file_url.replace("https://", "").replace(f"/blob/{branch_name}", "")
    parts = index_file_url_no_https.split("/")
    username = parts[1]
    repo = parts[2]
    file_path = '/'.join(parts[3:])
    new_content = tomli_w.dumps(index_content)
    commit_message = f"Update {file_path}"

    # Step 1: Get the SHA of the current file
    get_sha_cmd = ["gh", "api", f"repos/{username}/{repo}/contents/{file_path}", "-q", ".sha"]
    sha_result = subprocess.run(get_sha_cmd, check=True, capture_output=True, text=True)
    file_sha = sha_result.stdout.strip()

    # Step 2: Encode the new content to base64
    encoded_content = base64.b64encode(new_content.encode()).decode()

    # Step 3: Update the file
    update_cmd = [
        "gh", "api",
        "--method", "PUT",
        f"repos/{username}/{repo}/contents/{file_path}",
        "-f", f"message={commit_message}",
        "-f", f"content={encoded_content}",
        "-f", f"sha={file_sha}"
    ]

    update_result = subprocess.run(update_cmd, check=True, capture_output=True, text=True)

    typer.echo(f"Successfully added package {package_name} to index at {index_file_url}")


def remove_from_index(index_file_url: str, package_folder_path: str, _config_file_path: str = DEFAULT_ROSS_CONFIG_FILE_PATH) -> None:
    """Remove the specified package from the specified index.
    The index file URL should manipulated to be of the form:
    """
    ###################################################################   
    ########## Check that the preconditions are met ###################
    ###################################################################    

    # Check if the package folder path is valid
    if not os.path.exists(package_folder_path):
        typer.echo(f"Folder {package_folder_path} does not exist.")
        raise typer.Exit()
    if not os.path.isdir(package_folder_path):
        typer.echo(f"Path {package_folder_path} is not a directory.")
        raise typer.Exit()

    # Check if the package folder is a git repository
    if not os.path.exists(os.path.join(package_folder_path, ".git")):
        typer.echo(f"Folder {package_folder_path} is not a git repository.")
        raise typer.Exit()
    
    # Check for the rossproject.toml file
    rossproject_toml_path = os.path.join(package_folder_path, "rossproject.toml")
    if not os.path.exists(rossproject_toml_path):
        typer.echo(f"Folder {package_folder_path} is missing a rossproject.toml file")
        raise typer.Exit()    
    
    ########### Check if the index file URL is valid ######################
    # Make sure the index_file_url is a properly formatted URL to the index.toml file.    
    index_file_url = index_file_url.replace(".git", "")
    file_path = None    
    if is_owner_repo_format(index_file_url):
        parts = index_file_url.split("/")
        owner = parts[0]
        repo = parts[1]        
    elif is_valid_url(index_file_url):
        owner, repo, file_path = parse_github_url(index_file_url)
    else:
        typer.echo("Improperly formatted index specification!")
        raise typer.Exit()
    if file_path is None:   
        file_path = "index.toml"

    repo_url = f"https://github.com/{owner}/{repo}"
    if not re.search(BLOB_BRANCH_REGEX, index_file_url):
        branch_name = get_default_branch_name(repo_url)
        index_file_url = f"https://github.com/{owner}/{repo}/blob/{branch_name}/{file_path}"
    else:
        index_file_url = f"https://github.com/{owner}/{repo}/{file_path}"

    # Check if the index file URL exists
    if not check_url_exists(index_file_url):
        typer.echo(f"Index file URL {index_file_url} does not exist.")
        raise typer.Exit()
    
    ####### Check that the config has the specified index in it #######
    config = load_config(_config_file_path)
    if "index" not in config or len(config["index"]) == 0:
        typer.echo(f"No indexes found in the config file.")
        raise typer.Exit()
    index_file_url_in_config = False
    for index in config["index"]:
        if repo_url + ".git" in index["url"]:
            index_file_url_in_config = True
            break
    if not index_file_url_in_config:
        typer.echo(f"Index file URL {index_file_url} is not tapped!")
        typer.echo(f"Please tap the index using the command: `ross tap {index_file_url}`")
        raise typer.Exit()

    # Get the package name from the rossproject.toml file    
    rossproject_content = load_rossproject(rossproject_toml_path)
    package_name = rossproject_content["name"]
    
    # Get the remote URL from the git repository
    remote_url = get_remote_url_from_git_repo(package_folder_path)

    # Download the content of the index.toml file directly from GitHub.
    index_content = tomli.loads(read_github_file_from_release(index_file_url))

    if "package" not in index_content:
        index_content["package"] = []

    # for package in index_content["package"]:
    #     if remote_url == package["url"]: