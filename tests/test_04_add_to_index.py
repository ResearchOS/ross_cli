
import pytest
import typer

from src.ross_cli.cli import *


def test_01_add_to_index(temp_index_github_repo_url_only, temp_dir_ross_project, temp_config_path):  
    # Raise error because there's no indexes in the config file.  
    with pytest.raises(typer.Exit) as exc_info:
        index.add_to_index(temp_index_github_repo_url_only, temp_dir_ross_project, _config_file_path = temp_config_path)
    assert exc_info.value.exit_code == 0


def test_02_add_to_index_after_tap(temp_index_github_repo, temp_dir_ross_project_github_repo, temp_config_path):
    # Succeeds

    # Tap the index repository
    tap.tap_github_repo_for_ross_index(temp_index_github_repo, _config_file_path = temp_config_path)

    # Add the project to the index
    index.add_to_index(temp_index_github_repo, temp_dir_ross_project_github_repo, _config_file_path = temp_config_path)


def test_03_add_to_index_twice(temp_index_github_repo, temp_dir_ross_project_github_repo, temp_config_path):
    # Fails on the second add to index attempt
    tap.tap_github_repo_for_ross_index(temp_index_github_repo, _config_file_path = temp_config_path)

    index.add_to_index(temp_index_github_repo, temp_dir_ross_project_github_repo, _config_file_path = temp_config_path)

    with pytest.raises(typer.Exit) as exc_info:
        index.add_to_index(temp_index_github_repo, temp_dir_ross_project_github_repo, _config_file_path = temp_config_path)

    assert exc_info.value.exit_code == 2