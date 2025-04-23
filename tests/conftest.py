import os
import tempfile
import subprocess

import pytest

ROSSPROJECT_TOML_CONTENT_TEST = """# ROSS project configuration file
name = "test-package"
version = "0.1.0"
repository_url = "https://github.com/test-owner/test-package"
language = "python"
authors = [

]
dependencies = [
    "load-gaitrite",
]
readme = "README.md"
"""

@pytest.fixture(scope="function")
def temp_config_path():
    # Temporary config file
    with tempfile.NamedTemporaryFile(suffix=".toml") as temp_file:
        path = temp_file.name        
        yield path


@pytest.fixture(scope="function")
def temp_dir():
    # Folder only
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(scope="function")
def temp_dir_with_git_repo():
    # Folder and git repository    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize a git repository in the temporary directory
        subprocess.run(["git", "init", temp_dir])
        yield temp_dir


@pytest.fixture(scope="function")
def temp_dir_ross_project():
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