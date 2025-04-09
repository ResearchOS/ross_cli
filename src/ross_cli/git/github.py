#!/usr/bin/env python3
import os
import subprocess
import re
from typing import Tuple
from urllib.parse import urlparse

import typer

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
            typer.echo("No remotes found. Please ensure the repository has a remote.")
            raise typer.Exit()
        
        if len(remotes) != 1:
            typer.echo("Multiple remotes found. Please ensure there is only one remote.")
            raise typer.Exit()

        remote = remotes[0] # Get the string, not the list
            
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
        raise typer.Exit()
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