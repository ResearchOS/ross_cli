import tempfile
import subprocess

import pytest

@pytest.fixture(scope="session")
def temp_project_root_directory():    
    with tempfile.TemporaryDirectory(delete=False) as temp_dir:
        yield temp_dir

@pytest.fixture(scope="function")
def temp_project_root_directory_with_git_repo():
    with tempfile.TemporaryDirectory(delete=False) as temp_dir:
        # Initialize a git repository in the temporary directory
        subprocess.run(["git", "init", temp_dir])
        yield temp_dir
        # Clean up the git repository after the test session
        subprocess.run(["rm", "-rf", temp_dir])