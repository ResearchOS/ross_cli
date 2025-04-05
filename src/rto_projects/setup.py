import os
import subprocess

import tomli_w

from .cli import DEFAULT_INDEX_FILE_PATH
from .git.github import get_remote_urls_from_git_repo

def setup(index_file_path: str = DEFAULT_INDEX_FILE_PATH):
    """Create the index file at the specified location."""
    index_folder_path = os.path.dirname(index_file_path)
    os.makedirs(index_folder_path, exist_ok=True)    

    # Make sure the index folder is a git repository, and create a remote repository if it doesn't exist
    try:        
        # Initialize a new git repository if it doesn't exist
        if not os.path.exists(os.path.join(index_folder_path, ".git")):
            subprocess.run(["git", "init", index_folder_path])

        # Create a remote repository if it doesn't exist
        result = subprocess.run(["git", "remote", "-v"], cwd=index_folder_path, capture_output=True, text=True)
        if not result.stdout:
            print("No remote repository found. Please enter the URL to a remote repository's .git file")
            print("Example: https://www.github.com/username/repo.git")
             # Get the URL from the user
            url = input("URL: ")
            verify = subprocess.run(["git", "ls-remote", url], capture_output=True, text=True)
            if verify.returncode != 0:
                print("Error: Repository does not exist or is not accessible")
                print("Please create the repository on GitHub first")
                return 1
             # Add the remote repository
            subprocess.run(["git", "remote", "add", "origin", url], cwd=index_folder_path)
        else:
            url = get_remote_urls_from_git_repo(index_folder_path)
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return 1    
    
    # Pull the latest changes from the remote repository
    subprocess.run(["git", "pull", "origin"], cwd=index_folder_path)

    # Check if the index file already exists
    if os.path.exists(index_file_path):
        return 1
    
    # Create the index file
    with open(index_file_path, "wb") as f:
        tomli_w.dump({}, f)  # Create an empty TOML file
    print(f"Index file created at {index_file_path}")

    # Add the index file to the local and remote repository        
    subprocess.run(["git", "add", index_file_path], cwd=index_folder_path)
    subprocess.run(["git", "commit", "-m", "Add index file"], cwd=index_folder_path)
    subprocess.run(["git", "push", "origin"], cwd=index_folder_path)