import pytest

from src.ross_cli.cli import *
from src.ross_cli.commands.release import process_non_ross_dependency

def test_01_release(temp_dir_ross_project_github_repo):
    release_type = "patch"
    release_command(release_type, temp_dir_ross_project_github_repo)


def test_02_process_non_ross_dependency_python_package_name_no_version():
    # Parse PyPI package
    package_name = "numpy"
    language = "python"
    processed_dep, processed_tool_dep = process_non_ross_dependency(package_name, language)
    assert processed_dep == "numpy==2.2.5"
    assert processed_tool_dep == []


def test_03_process_non_ross_dependency_python_package_name_with_version():
    # Parse GitHub package
    package_name = "numpy==2.2.5"
    language = "python"
    processed_dep, processed_tool_dep = process_non_ross_dependency(package_name, language)
    assert processed_dep == package_name
    assert processed_tool_dep == [] 


def test_04_process_non_ross_dependency_package_name_wrong_language():
    # Parse GitHub package
    package_name = "numpy"
    language = "matlab"
    processed_dep, processed_tool_dep = process_non_ross_dependency(package_name, language)
    assert processed_dep == None
    assert processed_tool_dep == None


def test_05_process_non_ross_dependency_wrong_name_python():
    # Parse GitHub package
    package_name = "impossible----package----name"
    language = "python"
    with pytest.raises(typer.Exit):
        processed_dep, processed_tool_dep = process_non_ross_dependency(package_name, language)


def test_06_process_non_ross_dependency_github_url_python_no_version():
    url = "https://github.com/networkx/networkx"
    language = "python"
    processed_dep, processed_tool_dep = process_non_ross_dependency(url, language)
    print(processed_dep)


def test_07_process_non_ross_dependency_owner_repo_python_no_version():
    url = "networkx/networkx"
    language = "python"
    processed_dep, processed_tool_dep = process_non_ross_dependency(url, language)
    print(processed_dep)


def test_08_process_non_ross_dependency_github_url_python_with_version():
    url = "https://github.com/networkx/networkx@networkx-3.4.2"
    language = "python"
    processed_dep, processed_tool_dep = process_non_ross_dependency(url, language)
    print(processed_dep)


def test_09_process_non_ross_dependency_owner_repo_python_with_version():
    url = "networkx/networkx@networkx-3.4.2"
    language = "python"
    processed_dep, processed_tool_dep = process_non_ross_dependency(url, language)
    print(processed_dep)


def test_10_process_non_ross_dependency_github_url_matlab_no_github_release():
    url = "https://github.com/chadagreene/rgb"
    langauge = "matlab"
    with pytest.raises(typer.Exit) as e:
        processed_dep, processed_tool_dep = process_non_ross_dependency(url, langauge)
    assert e.value.exit_code == 4