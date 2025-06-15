import pytest

from tests.conftest import get_owner_from_github_username
from src.ross_cli.cli import *

REPO = 'test-index'
OWNER = get_owner_from_github_username() # For multi-user testability
REMOTE_URL = f"https://github.com/{OWNER}/{REPO}/"

def test_01_tap_with_invalid_url():
    invalid_url = "invalid-url"
    with pytest.raises(typer.Exit):
        tap_command(invalid_url)


def test_02_tap(temp_config_path):    
    tap.tap_github_repo_for_ross_index(REMOTE_URL, _config_file_path=temp_config_path)


def test_03_untap_without_tap(temp_config_path):
    with pytest.raises(typer.Exit):
        tap.untap_ross_index(REMOTE_URL, _config_file_path=temp_config_path)


def test_04_untap_after_tap(temp_config_path):
    tap.tap_github_repo_for_ross_index(REMOTE_URL, _config_file_path=temp_config_path)
    tap.untap_ross_index(REMOTE_URL, _config_file_path=temp_config_path)


def test_05_tap_twice(temp_config_path):
    tap.tap_github_repo_for_ross_index(REMOTE_URL, _config_file_path=temp_config_path)
    
    # No error raised the second time, just returns early
    tap.tap_github_repo_for_ross_index(REMOTE_URL, _config_file_path=temp_config_path)


def test_06_tap_with_repo_user(temp_config_path):
    tap.tap_github_repo_for_ross_index(f"{OWNER}/{REPO}", _config_file_path=temp_config_path)