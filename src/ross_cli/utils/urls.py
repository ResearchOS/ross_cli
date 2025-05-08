import re
import urllib.request
import urllib.error
import subprocess

import typer

from ..constants import BLOB_BRANCH_REGEX

def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL"""
    url_pattern = r'''
        ^                           # Start of string
        (?:(?:https?|ftp):\/\/)?   # Protocol (optional)
        (?:[\w-]+\.)+              # Domain name
        [a-zA-Z]{2,}               # Top level domain
        (?:\/[^\s]*)?              # Path (optional)
        $                          # End of string
    '''
    pattern = re.compile(url_pattern, re.VERBOSE)
    return bool(pattern.match(url))


def check_url_exists(url: str) -> bool:
    """Check that the provided URL exists.
    If the URL is a GitHub URL, check if the file exists in the repository.

    Args:
        url (str): The URL to check

    Raises:
        typer.Exit:

    Returns:
        bool: True if the URL exists (response.status == 200), False otherwise.
    """
    from ..git.github import parse_github_url
    exists = True
    if not is_valid_url(url):
        return None
    try:
        # Make HTTP request to PyPI API
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                return True
            exists = False
    except urllib.error.HTTPError as e:
        if e.code == 404:
            exists = False
        else:
            typer.echo(f"Error: HTTP {e.code} - {e.reason}")
            raise typer.Exit()
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit()

    if not exists and "github.com" in url:
        try:
            owner, repo, file_path = parse_github_url(url)
            if file_path is None:
                repos_str = f"repos/{owner}/{repo}"
            else:
                file_path = remove_blob_and_branch_from_url(file_path)
                file_path = file_path.lstrip("/")
                # Release tags are a special case vs. normal file paths
                if "releases/" in file_path:
                    tag = file_path.replace("releases/tag/", "")
                    repos_str = f"repos/{owner}/{repo}/releases/tags/{tag}"                    
                else:
                    repos_str = f"repos/{owner}/{repo}/contents/{file_path}"
            output = subprocess.run(["gh", "api", repos_str], check=True, capture_output=True)
            exists = True
        except subprocess.CalledProcessError as e:
            pass

    return exists
    

def remove_blob_and_branch_from_url(url: str) -> str:
    """Remove the 'blob' and branch name from a GitHub URL.
    e.g. removes "/blob/main", or "/blob/master" from the URL.

    Args:
        url (str): The URL to modify.

    Returns:
        str: The modified URL.
    """
    url = re.sub(BLOB_BRANCH_REGEX, '', url)
    return url
    

def is_owner_repo_format(owner_repo_string: str) -> bool:
    """Check if a string specifies a GitHub repository using owner/repo format."""
    if not ("/" in owner_repo_string and not is_valid_url(owner_repo_string)):
        return False
    
    split_str = owner_repo_string.split("/")
    if len(split_str) != 2:
        return False
    
    return True

def convert_owner_repo_format_to_url(owner_repo_string: str) -> bool:
    """Convert a GitHub repository from owner/repo format to URL format."""

    if is_valid_url(owner_repo_string):
        return owner_repo_string
    
    if not is_owner_repo_format(owner_repo_string):
        return None
    
    split_str = owner_repo_string.split("/")
    url = f"https://github.com/{split_str[0]}/{split_str[1]}"
    return url