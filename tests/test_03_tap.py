import pytest

from src.ross_cli.cli import *

from .conftest import OWNER, INDEX_REPO_NAME

REMOTE_URL = f"https://github.com/{OWNER}/{INDEX_REPO_NAME}/"

def test_01_tap_with_invalid_url(gh_protocol):
    invalid_url = "invalid-url"
    with pytest.raises(typer.Exit):
        tap_command(invalid_url)


def test_02_tap(temp_config_path, temp_index_github_repo, gh_protocol):    
    tap.tap_github_repo_for_ross_index(REMOTE_URL, _config_file_path=temp_config_path)


def test_03_untap_without_tap(temp_config_path, gh_protocol):
    with pytest.raises(typer.Exit):
        tap.untap_ross_index(REMOTE_URL, _config_file_path=temp_config_path)


def test_04_untap_after_tap(temp_config_path, temp_index_github_repo, gh_protocol):
    tap.tap_github_repo_for_ross_index(REMOTE_URL, _config_file_path=temp_config_path)
    tap.untap_ross_index(REMOTE_URL, _config_file_path=temp_config_path)


def test_05_tap_twice(temp_config_path, temp_index_github_repo, gh_protocol):
    tap.tap_github_repo_for_ross_index(REMOTE_URL, _config_file_path=temp_config_path)
    
    # No error raised the second time, just returns early
    tap.tap_github_repo_for_ross_index(REMOTE_URL, _config_file_path=temp_config_path)


def test_06_tap_with_repo_user(temp_config_path, temp_index_github_repo, gh_protocol):
    tap.tap_github_repo_for_ross_index(f"{OWNER}/{INDEX_REPO_NAME}", _config_file_path=temp_config_path)