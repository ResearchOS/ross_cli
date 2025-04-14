#!/usr/bin/env python3
import os
import subprocess
import re
from typing import Tuple
from urllib.parse import urlparse
import json
import base64

import typer

from ..utils.urls import is_valid_url

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

def git_push_to_remote(directory="."):
    """
    Pushes changes in the specified directory to the remote.
    
    Args:
        directory (str): Path to the git repository directory
    """
    try:
        # Change to the specified directory
        original_dir = os.getcwd()
        os.chdir(directory)
        
        # Check if the directory is a git repository
        if not os.path.isdir('.git'):
            typer.echo("The specified directory is not a git repository.")
            raise typer.Exit()
        
        # Run git push command
        subprocess.run(
            ["git", "push", "origin"],
            check=True
        )
        
        # Return to the original directory
        os.chdir(original_dir)
        
    except subprocess.CalledProcessError as e:
        typer.echo(f"Git command failed: {e.stderr.strip()}")
        raise typer.Exit()
    except typer.echo as e:        
        typer.echo(f"Error: {str(e)}")
        raise typer.Exit()

def parse_github_url(url: str) -> Tuple[str, str]:
    """Parse GitHub username and repository name from URL.
    
    Args:
        url: GitHub repository URL (HTTPS or SSH format)
        
    Returns:
        Tuple of (username, repository_name)
        
    Raises:
        ValueError: If URL format is invalid
    """
    # Handle HTTPS URLs (https://github.com/username/repo.git)
    if url.startswith('https://'):
        parts = urlparse(url).path.strip('/').split('/')
        if len(parts) != 2:
            typer.echo(f"Invalid GitHub URL format: {url}")
            raise typer.Exit()
        return parts[0], parts[1].replace('.git', '')
        
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
    try:
        # Extract owner/repo from remote_url
        url_parts = remote_url.split("/")
        repo_path = f"{url_parts[-2]}/{url_parts[-1]}"
        if repo_path.endswith(".git"):
            repo_path = repo_path[:-4]
            
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

def read_github_file(file_url: str) -> str:
    """Read a file from GitHub. 
    The file URL is of one of the two following forms:
    1. https://github.com/username/repo/path/to/file.ext (mirrors file structure)
    2. https://github.com/username/repo/blob/main/file.ext (directly copied from GitHub site)
    """

    file_url = file_url.replace("blob/main", "")

    GITHUB_COM_STR = "github.com/"
    HTTPS_GITHUB_COM_STR = "https://github.com/"
    if GITHUB_COM_STR not in file_url:
        typer.echo("Invalid GitHub URL")
        raise typer.Exit()

    # Standardize the URL prefix
    github_com_index = file_url.index(GITHUB_COM_STR)
    file_url = file_url.replace(file_url[0:github_com_index + len(GITHUB_COM_STR)], HTTPS_GITHUB_COM_STR)

    if not is_valid_url:
        typer.echo(f"Invalid URL {file_url}")

    path_part = file_url[len(HTTPS_GITHUB_COM_STR):]

    # Split the remaining path
    parts = path_part.split('/', 2)  # Split into max 3 parts
    if len(parts) < 3:
        typer.echo("URL doesn't have enough components")
        raise typer.Exit()
    
    username = parts[0]
    repo_name = parts[1]
    file_path = parts[2]

    api_endpoint = f"/repos/{username}/{repo_name}/contents/{file_path}"
    command = ["gh", "api", api_endpoint]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    content_json = json.loads(result.stdout)
    content = base64.b64decode(content_json["content"]).decode("utf-8")
    return content

def create_empty_file_in_repo(repo_git_url, file_path, commit_message="Add empty file"):
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
    path_parts = urlparse(repo_git_url).path.strip('/').split('/')
    if path_parts[-1].endswith('.git'):
        path_parts[-1] = path_parts[-1][:-4]  # Remove .git suffix
    
    owner = path_parts[-2]
    repo = path_parts[-1]
    
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