import pytest
from ross_cli.cli import *

def test_01_init(temp_project_root_directory):
    name = "test_package_no_git"
    with pytest.raises(typer.Exit):
        init_command(name, temp_project_root_directory)

def test_02_init_with_git(temp_project_root_directory_with_git_repo):
    name = "test_package"
    # Create package with git
    init_command(name, temp_project_root_directory_with_git_repo)
        
def test_03_init_existing_package(temp_project_root_directory_with_git_repo):
    name = "test_package"
    # Create package first time
    init_command(name, temp_project_root_directory_with_git_repo)
    # Try to create same package again
    with pytest.raises(typer.Exit):
        init_command(name, temp_project_root_directory_with_git_repo)

def test_04_init_empty_name(temp_project_root_directory_with_git_repo):
    name = ""
    with pytest.raises(typer.Exit):
        init_command(name, temp_project_root_directory_with_git_repo)