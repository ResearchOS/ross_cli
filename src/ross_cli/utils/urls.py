import re
import urllib.request
import urllib.error
import json

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
                data = json.loads(response.read().decode('utf-8'))
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