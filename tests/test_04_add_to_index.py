import os

import pytest
import typer

# from ross_cli.cli import *
from src.ross_cli.cli import *
from .conftest import temp_config_path_no_delete

INDEX_FILE_URL = "https://github.com/ResearchOS/test-index/index.toml"
config_file_path = temp_config_path_no_delete()


def test_01_add_to_index(temp_dir_ross_project, temp_config_path):  
    # Raise error because there's no indexes in the config file.  
    with pytest.raises(typer.Exit) as exc_info:
        index.add_to_index(INDEX_FILE_URL, temp_dir_ross_project, _config_file_path = temp_config_path)
    assert exc_info.value.exit_code == 0

def test_02_add_to_index_after_tap(temp_dir_ross_project, temp_config_path):
    # Raises error because there's no remote GitHub repository.

    # Tap the index repository
    tap.tap_github_repo_for_ross_index(INDEX_FILE_URL, _config_file_path = temp_config_path)

    # Add the project to the index
    with pytest.raises(typer.Exit) as exc_info:
        index.add_to_index(INDEX_FILE_URL, temp_dir_ross_project, _config_file_path = temp_config_path)
    assert exc_info.value.exit_code == 0

def test_03_add_to_index_after_tap_and_github_repo(temp_dir_ross_project, temp_config_path):
    # Succeeds because the project is in a GitHub repository.
    # Tap the index repository
    tap.tap_github_repo_for_ross_index(INDEX_FILE_URL, _config_file_path = temp_config_path)
    # Create a sample GitHub repository
    # TODO: gh repo create

    # Add the project to the index
    index.add_to_index(INDEX_FILE_URL, temp_dir_ross_project, _config_file_path = temp_config_path)

def test_02_add_to_index_twice(temp_dir_ross_project, temp_config_path):
    with pytest.raises(typer.Exit) as exc_info:
        index.add_to_index(INDEX_FILE_URL, temp_dir_ross_project, _config_file_path = temp_config_path)
    assert exc_info.value.exit_code == 0

    index.add_to_index(INDEX_FILE_URL, temp_dir_ross_project, _config_file_path = temp_config_path)