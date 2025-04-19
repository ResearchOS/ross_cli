import re
import urllib.request
import urllib.error

import typer

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

    Args:
        url (str): The URL to check

    Raises:
        typer.Exit:

    Returns:
        bool: True if the URL exists (response.status == 200), False otherwise.
    """
    
    try:
        # Make HTTP request to PyPI API
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                return True
            return False
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        else:
            typer.echo(f"Error: HTTP {e.code} - {e.reason}")
            raise typer.Exit()
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit()
    

def is_owner_repo_format(owner_repo_string: str) -> bool:
    """Check if a string specifies a GitHub repository using owner/repo format."""
    if not ("/" in owner_repo_string and not is_valid_url(owner_repo_string)):
        return False
    
    split_str = owner_repo_string.split("/")
    if len(split_str) != 2:
        return False
    
    # Has file name
    # if "." in split_str[1]:
    #     return False
    
    return True

def convert_owner_repo_format_to_url(owner_repo_string: str) -> bool:
    """Convert a GitHub repository from owner/repo format to URL format."""

    if is_valid_url(owner_repo_string):
        return owner_repo_string
    
    if not is_owner_repo_format(owner_repo_string):
        return None
    
    split_str = owner_repo_string.split("/")
    # if "." in split_str[1]:
    #     prd_index = split_str[1].index(".")
    #     split_str[1] = split_str[1][0:prd_index]
    url = f"https://github.com/{split_str[0]}/{split_str[1]}"
    return url