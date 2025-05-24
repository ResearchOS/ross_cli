#!/usr/bin/env python3
import os
import subprocess
import re
from typing import Tuple
from urllib.parse import urlparse
import json
import base64
from datetime import datetime
import tempfile
import zipfile
import shutil

import typer

from ..utils.urls import is_valid_url, remove_blob_and_branch_from_url

def get_remote_url_from_git_repo(directory="."):
    """
    Extracts all remote URLs from a git repository in the specified directory.
    
    Args:
        directory (str): Path to the git repository directory
        
    Returns:
        dict: Dictionary of remote names and their URLs
        str: Error message if any
    """
    try:
        # Change to the specified directory
        original_dir = os.getcwd()
        os.chdir(directory)
        
        # Check if the directory is a git repository
        if not os.path.isdir('.git'):
            typer.echo("The specified directory is not a git repository.")
            raise typer.Exit()
        
        # Run git remote command to get remotes
        result = subprocess.run(
            ["git", "remote", "-v"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Return to the original directory
        os.chdir(original_dir)
        
        # Parse the output
        remotes = []
        for line in result.stdout.splitlines():
            # Extract remote name, URL and type (fetch/push)
            match = re.match(r'^(\S+)\s+(\S+)\s+\((\w+)\)$', line)
            if match:
                remote_name, url, remote_type = match.groups()
                
                # Only store fetch URLs to avoid duplicates (each remote has both fetch and push)
                if remote_type == 'fetch':
                    remotes.append(url)
        
        if not remotes:
            typer.echo("No remotes found. Please ensure this new local git repository has a remote.")
            typer.echo("The fastest and most reliable way to do this is to run `gh repo create` and follow the prompts")
            raise typer.Exit()
        
        if len(remotes) != 1:
            typer.echo("Multiple remotes found. Please ensure there is only one remote.")
            raise typer.Exit()

        remote = remotes[0] # Get the string, not the list

        if not remote.endswith(".git"):
            raise ValueError("TESTING ONLY. Error! Remote URL should end with '.git'!")
            
        return remote
        
    except subprocess.CalledProcessError as e:
        typer.echo(f"Git command failed: {e.stderr.strip()}")
        raise typer.Exit()
    except Exception as e:
        typer.echo(f"Error: {str(e)}")
        raise typer.Exit()


def parse_github_url(url: str) -> Tuple[str, str, str]:
    """Parse GitHub username and repository name from URL.
    
    Args:
        url: GitHub repository URL (HTTPS or SSH format). Ending with repo name, .git, or file name.
        
    Returns:
        Tuple of (username, repository_name)
        
    Raises:
        ValueError: If URL format is invalid
    """
    # Handle HTTPS URLs (https://github.com/username/repo.git)
    if url.startswith('https://'):
        parts = urlparse(url).path.strip('/').split('/')
        if len(parts) < 2:
            typer.echo(f"Invalid GitHub URL format: {url}")
            raise typer.Exit()
        owner = parts[0]
        repo = parts[1].replace('.git', '')
        file_path = "/".join(parts[2:]) if len(parts) > 2 else None
        return owner, repo, file_path
        
    # Handle SSH URLs (git@github.com:username/repo.git)
    elif url.startswith('git@'):
        pattern = r'git@github\.com:([^/]+)/([^/]+)\.git'
        match = re.match(pattern, url)
        if not match:
            typer.echo(f"Invalid GitHub SSH URL format: {url}")
            raise typer.Exit()
        return match.group(1), match.group(2)
    
    else:
        typer.echo(f"URL must start with 'https://' or 'git@': {url}")
        raise typer.Exit()
    
def get_default_branch_name(remote_url: str) -> str:
    """Get the name of the default branch from the GitHub repository URL"""
    # Get the default branch name
    remote_url = remote_url.replace(".git", "")
    try:
        # Extract owner/repo from remote_url
        owner, repo, file_path = parse_github_url(remote_url)        
        repo_path = f"{owner}/{repo}"
            
        result = subprocess.run(
            ["gh", "api", f"repos/{repo_path}"], 
            capture_output=True, 
            text=True,
            check=True
        )
        default_branch = json.loads(result.stdout)["default_branch"]
    except subprocess.CalledProcessError:
        typer.echo("Failed to get default branch from GitHub repository, falling back to 'main'")
        default_branch = "main"

    return default_branch

def read_github_file_from_release(file_url: str, tag: str = None) -> str:
    """Read a file from GitHub. 
    The file URL is of one of the two following forms:
    1. https://github.com/username/repo/path/to/file.ext (mirrors file structure)
    2. https://github.com/username/repo/blob/main/file.ext (directly copied from GitHub site)
    """

    # If a URL was copied & pasted from looking at the file online.    
    file_url = remove_blob_and_branch_from_url(file_url)

    if not is_valid_url:
        typer.echo(f"Invalid URL {file_url}")
        typer.Exit()

    owner, repo, file_path = parse_github_url(file_url)

    # If the tag is not specified, use the latest release.
    releases_command = ["gh", "api", f"repos/{owner}/{repo}/releases"]
    releases = json.loads(subprocess.run(releases_command, check=True, capture_output=True).stdout)    

    # Get the latest release tag if not specified.
    if len(releases) > 0 and tag is None:
        # Find the index of the latest release
        release_dates = []
        for release in releases:
            release_date = release['published_at']
            release_dates.append(datetime.fromisoformat(release_date.replace('Z', '+00:00')))
        latest_date = max(release_dates)

        # Get the tag of the latest release
        latest_release = releases[release_dates.index(latest_date)]
        tag = latest_release['tag_name']

    if len(releases) == 0:
        api_endpoint = f"/repos/{owner}/{repo}/contents/{file_path}"
    else:        
        api_endpoint = f"/repos/{owner}/{repo}/contents/{file_path}?ref={tag}"
    command = ["gh", "api", api_endpoint]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    content_json = json.loads(result.stdout)
    content = base64.b64decode(content_json["content"]).decode("utf-8")
    return content

def create_empty_file_in_repo(repo_git_url: str, file_path: str, commit_message: str = "Add empty file"):
    """
    Create an empty file in a GitHub repository using the GitHub CLI.
    
    Args:
        repo_git_url (str): GitHub repository URL ending with .git
        file_path (str): Path where the file should be created
        commit_message (str): Commit message for the file creation
    
    Returns:
        dict: GitHub API response data
    """
    # Extract owner and repo name from git URL
    owner, repo, file_path_tmp = parse_github_url(repo_git_url.replace('.git', ''))
    
    # Base64 encode empty content (required by GitHub API)
    empty_content = ""
    encoded_content = base64.b64encode(empty_content.encode()).decode()
    
    # Prepare the gh CLI command
    api_path = f"repos/{owner}/{repo}/contents/{file_path}"
    
    # Build the command
    command = [
        "gh", "api",
        "--method", "PUT",
        api_path,
        "-f", f"message={commit_message}",
        "-f", f"content={encoded_content}"
    ]
    
    # Execute the command
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        # Parse the JSON response
        response_data = json.loads(result.stdout)
        return response_data
    except subprocess.CalledProcessError as e:
        print(f"Error executing GitHub CLI command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        raise

def download_github_release(owner, repository, tag=None, output_dir=None):
    """
    Download a GitHub repository release using GitHub CLI.
    
    Args:
        owner (str): The owner/organization of the repository
        repository (str): The name of the repository
        tag (str, optional): The release tag to download (default: latest release)
        output_dir (str, optional): Directory to extract the repository to
    
    Returns:
        str: Path to the extracted repository
    """
    # Create a temporary directory for the zip file
    with tempfile.TemporaryDirectory(delete=True) as temp_dir:

        # If no tag is specified, get the latest release tag
        if not tag:
            print(f"No tag specified, getting latest release for {owner}/{repository}...")
            result = subprocess.run([
                "gh", "api", 
                f"repos/{owner}/{repository}/releases/latest"
            ], capture_output=True, text=True, check=True)
            
            release_info = json.loads(result.stdout)
            tag = release_info['tag_name']
            print(f"Latest release tag: {tag}")

        # Determine the output directory
        if not output_dir:
            output_dir = os.getcwd()
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        # Use gh cli to download the release zipball
        print(f"Downloading release {tag} from {owner}/{repository} to {output_dir}")
        repo_url = f"https://github.com/{owner}/{repository}.git"
        result = subprocess.run([
            "git", "clone",
            "--depth=1",
            f"--branch={tag}",
            f"--separate-git-dir={temp_dir}",
            repo_url,
            output_dir
        ], check=True, capture_output=True)
        

def get_latest_release_tag(owner, repository):
    """
    Get the latest release tag by release date (not by GitHub's 'latest' endpoint).
    
    Args:
        owner (str): The owner/organization of the repository
        repository (str): The name of the repository
    
    Returns:
        str: The tag name of the latest release
    """
    print(f"Finding latest release by date for {owner}/{repository}...")
    
    # Get all releases
    result = subprocess.run([
        "gh", "api", 
        f"repos/{owner}/{repository}/releases"
    ], capture_output=True, text=True, check=True)
    
    releases = json.loads(result.stdout)
    
    if not releases:
        typer.echo(f"No releases found for {owner}/{repository}.")
        raise typer.Exit(code=4)
    
    # Sort releases by published_at date (newest first)
    sorted_releases = sorted(
        releases, 
        key=lambda r: datetime.strptime(r['published_at'], '%Y-%m-%dT%H:%M:%SZ'),
        reverse=True
    )
    
    latest_release = sorted_releases[0]
    return latest_release['tag_name']