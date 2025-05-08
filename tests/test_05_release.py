import pytest

from src.ross_cli.cli import *
from src.ross_cli.commands.release import process_non_ross_dependency

def test_01_release(temp_dir_ross_project_github_repo):
    release_type = "patch"
    release_command(release_type, temp_dir_ross_project_github_repo)


def test_02_process_non_ross_dependency():
    # Parse PyPI package
    package_name = "numpy"
    language = "python"
    processed_dep, processed_tool_dep = process_non_ross_dependency(package_name, language)
    assert processed_dep == "numpy==2.2.5"
    assert processed_tool_dep == []


def test_03_parse_dependency():
    # Parse GitHub package
    package_name = "numpy==2.2.5"
    language = "python"
    processed_dep, processed_tool_dep = process_non_ross_dependency(package_name, language)
    assert processed_dep == package_name
    assert processed_tool_dep == [] 


def test_04_parse_dependency_wrong_language():
    # Parse GitHub package
    package_name = "numpy"
    language = "matlab"
    processed_dep, processed_tool_dep = process_non_ross_dependency(package_name, language)
    assert processed_dep == None
    assert processed_tool_dep == None


def test_05_parse_dependency():
    # Parse GitHub package
    package_name = "impossible----package----name"
    language = "python"
    processed_dep, processed_tool_dep = process_non_ross_dependency(package_name, language)
    assert processed_dep == None
    assert processed_tool_dep == None 