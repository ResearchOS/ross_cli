#!/usr/bin/env python3
import os
import subprocess
import re

def get_remote_urls_from_git_repo(directory="."):
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
            Exception("The specified directory is not a git repository.")
        
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
        remotes = {}
        for line in result.stdout.splitlines():
            # Extract remote name, URL and type (fetch/push)
            match = re.match(r'^(\S+)\s+(\S+)\s+\((\w+)\)$', line)
            if match:
                remote_name, url, remote_type = match.groups()
                
                # Only store fetch URLs to avoid duplicates (each remote has both fetch and push)
                if remote_type == 'fetch':
                    remotes[remote_name] = url
        
        if not remotes:
            Exception("No remotes found. Please ensure the repository has a remote.")
        
        if len(remotes) != 1:
            Exception("Multiple remotes found. Please ensure there is only one remote.")

        remote = remotes[0] # Get the string, not the list
            
        return remote, None
        
    except subprocess.CalledProcessError as e:
        Exception(f"Git command failed: {e.stderr.strip()}")
    except Exception as e:
        Exception(f"Error: {str(e)}")

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
            Exception("The specified directory is not a git repository.")
        
        # Run git push command
        subprocess.run(
            ["git", "push", "origin"],
            check=True
        )
        
        # Return to the original directory
        os.chdir(original_dir)
        
    except subprocess.CalledProcessError as e:
        Exception(f"Git command failed: {e.stderr.strip()}")
    except Exception as e:
        Exception(f"Error: {str(e)}")