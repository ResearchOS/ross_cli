import os
import tempfile
import subprocess

import pytest

ROSSPROJECT_TOML_CONTENT_TEST = """# ROSS project configuration file
name = "test_package"
version = "0.1.0"
repository_url = "https://github.com/test-owner/test-package"
language = "python"
authors = [

]
dependencies = [
    # "load-gaitrite",
]
readme = "README.md"
"""

INDEX_REPO_NAME = "test-index"
INDEX_REPO_OWNER = "mtillman14"
INDEX_REPO_URL = f"https://github.com/{INDEX_REPO_OWNER}/{INDEX_REPO_NAME}/.git"
INDEX_TOML_REPO_URL = f"https://github.com/{INDEX_REPO_OWNER}/{INDEX_REPO_NAME}/index.toml"

PACKAGE_REPO_NAME = "test-repo"
PACKAGE_REPO_OWNER = "mtillman14"

@pytest.fixture(scope="function")
def temp_config_path():
    """ROSS configuration file path"""
    # Temporary config file
    with tempfile.NamedTemporaryFile(suffix=".toml") as temp_file:
        path = temp_file.name        
        yield path


@pytest.fixture(scope="function")
def temp_dir():
    """Temporary directory"""
    # Folder only
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(scope="function")
def temp_dir_with_git_repo():
    """Temporary directory with git repository"""
    # Folder and git repository    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize a git repository in the temporary directory
        subprocess.run(["git", "init", temp_dir])        
        yield temp_dir


@pytest.fixture(scope="function")
def temp_dir_with_github_repo():
    """Temporary directory with github repository"""
    # Folder and git repository
    temp_dir = tempfile.mkdtemp()  # Create temporary directory
    original_dir = os.getcwd()  # Store original directory
    
    try:
        os.chdir(temp_dir)
        # Initialize git and configure basic settings
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "config", "init.defaultBranch", "main"], check=True)
        
        # Create and configure GitHub repository
        subprocess.run(["gh", "repo", "create", PACKAGE_REPO_NAME, "--private"], check=True)
        subprocess.run(["git", "remote", "add", "origin", 
                      f"https://github.com/{PACKAGE_REPO_OWNER}/{PACKAGE_REPO_NAME}.git"], 
                      check=True)        
        
        # Create initial commit and push
        subprocess.run(["git", "commit", "--allow-empty", "-m", "Initial commit"], check=True)
        subprocess.run(["git", "push"], check=True)
        
        yield temp_dir
        
    finally:
        os.chdir(original_dir)  # Always return to original directory
        try:
            subprocess.run(["gh", "repo", "delete", PACKAGE_REPO_NAME, "--yes"], check=True)
        finally:
            pass


@pytest.fixture(scope="function")
def temp_dir_ross_project():
    """Temporary directory with git repository and ross project structure, but no GitHub repo.
    NOTE: `ross init` requires a GitHub repository to be created first, so this fixture is only helpful so as to not need to create a GitHub repo."""
    # Initialized ross project.
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize a git repository in the temporary directory
        subprocess.run(["git", "init", temp_dir])
        # Create a sample ross project structure
        src_folder = os.path.join(temp_dir, "src")
        os.makedirs(src_folder, exist_ok=True)  # Replace mkdir -p
        
        # Create empty files using Python's open()
        with open(os.path.join(src_folder, "__init__.py"), 'w') as f:
            f.write("")
        with open(os.path.join(temp_dir, "rossproject.toml"), 'w') as f:
            f.write(ROSSPROJECT_TOML_CONTENT_TEST)
        yield temp_dir


@pytest.fixture(scope="function")
def temp_dir_ross_project_github_repo():
    """Temporary directory with git repository and ross project structure, including a GitHub repo"""
    # Folder and git repository
    temp_dir = tempfile.mkdtemp()  # Create temporary directory
    original_dir = os.getcwd()  # Store original directory
    # Initialized ross project.
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            os.chdir(temp_dir)
            # Initialize a git repository in the temporary directory
            subprocess.run(["git", "init", temp_dir])
            subprocess.run(["git", "config", "init.defaultBranch", "main"], check=True)
            
            # Create and configure GitHub repository
            subprocess.run(["gh", "repo", "create", PACKAGE_REPO_NAME, "--private"], check=True)
            subprocess.run(["git", "remote", "add", "origin", 
                        f"https://github.com/{PACKAGE_REPO_OWNER}/{PACKAGE_REPO_NAME}.git"], 
                        check=True)
                        
            # Create a sample ross project structure
            src_folder = os.path.join(temp_dir, "src")
            os.makedirs(src_folder, exist_ok=True)
            project_src_folder = os.path.join(src_folder, "test_package")
            os.makedirs(project_src_folder)

            # Create the content of the GitHub repository
            with open(os.path.join(temp_dir, "README.md"), 'w') as f:
                f.write(f"# {PACKAGE_REPO_NAME}")

            # Create empty files using Python's open()
            with open(os.path.join(project_src_folder, "__init__.py"), 'w') as f:
                f.write("# test_package")
            with open(os.path.join(temp_dir, "rossproject.toml"), 'w') as f:
                f.write(ROSSPROJECT_TOML_CONTENT_TEST)

            # Create initial commit and push
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
            subprocess.run(["git", "push"], check=True)
            yield temp_dir

        finally:
            os.chdir(original_dir)  # Always return to original directory
            try:
                # print("Deleting the GitHub repository...")
                subprocess.run(["gh", "repo", "delete", PACKAGE_REPO_NAME, "--yes"], check=True)
            finally:
                pass

@pytest.fixture(scope="function")
def temp_index_github_repo_url_only():
    """URL for the index GitHub repository, but no actual repository"""
    yield INDEX_TOML_REPO_URL

@pytest.fixture(scope="function")
def temp_index_github_repo():
    """URL for the index GitHub repository, and create the actual repository"""
    try:
        subprocess.run(["gh", "repo", "create", "test-index", "--private"], check=True)
    except:
        pass
    yield INDEX_TOML_REPO_URL
    subprocess.run(["gh", "repo", "delete", "test-index", "--yes"], check=True)