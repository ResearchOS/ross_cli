import os
import subprocess

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
    assert processed_dep.startswith("numpy==")
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
    assert processed_dep.startswith("networkx @ git+https://github.com/networkx/networkx@")
    assert processed_tool_dep == []


def test_07_process_non_ross_dependency_owner_repo_python_no_version():
    url = "networkx/networkx"
    language = "python"
    processed_dep, processed_tool_dep = process_non_ross_dependency(url, language)
    assert processed_dep.startswith("networkx @ git+https://github.com/networkx/networkx@")
    assert processed_tool_dep == []


def test_08_process_non_ross_dependency_github_url_python_with_version():
    url = "https://github.com/networkx/networkx@networkx-3.4.2"
    language = "python"
    processed_dep, processed_tool_dep = process_non_ross_dependency(url, language)
    assert processed_dep == "networkx @ git+https://github.com/networkx/networkx@networkx-3.4.2"
    assert processed_tool_dep == []


def test_09_process_non_ross_dependency_owner_repo_python_with_version():
    url = "networkx/networkx@networkx-3.4.2"
    language = "python"
    processed_dep, processed_tool_dep = process_non_ross_dependency(url, language)
    assert processed_dep == "networkx @ git+https://github.com/networkx/networkx@networkx-3.4.2"
    assert processed_tool_dep == []


def test_10_process_non_ross_dependency_owner_repo_python_with_version():
    tag = "networkx-3.4.2"
    url = f"networkx/networkx@{tag}"
    language = "python"
    processed_dep, processed_tool_dep = process_non_ross_dependency(url, language)
    assert processed_dep == "networkx @ git+https://github.com/networkx/networkx@networkx-3.4.2"
    assert processed_tool_dep == []


def test_11_process_non_ross_dependency_github_url_matlab_no_github_release():
    # A github repository that has no releases
    url = "https://github.com/chadagreene/rgb"
    language = "matlab"
    processed_dep, processed_tool_dep = process_non_ross_dependency(url, language)
    assert processed_dep == []
    assert processed_tool_dep.startswith(f"{url}/blob/")


def test_12_process_non_ross_dependency_github_url_matlab_specify_tag_but_no_github_release():
    # A github repository that has no releases
    url = "https://github.com/chadagreene/rgb@v1.0.0"
    language = "matlab"
    with pytest.raises(typer.Exit) as e:
        processed_dep, processed_tool_dep = process_non_ross_dependency(url, language)
    assert e.value.exit_code == 7
    # assert processed_dep == []
    # assert processed_tool_dep == url


def test_13_process_non_ross_dependency_github_url_matlab_with_github_release():
    url = "https://github.com/g-s-k/matlab-toml"
    language = "matlab"
    processed_dep, processed_tool_dep = process_non_ross_dependency(url, language)
    assert processed_dep == []
    assert processed_tool_dep.startswith("https://github.com/g-s-k/matlab-toml/blob/")


def test_14_process_non_ross_dependency_github_url_matlab_with_github_release_wrong_tag():
    # Providing the wrong tag, in a repository that has other releases.
    url = "https://github.com/g-s-k/matlab-toml@1.0.3"
    language = "matlab"
    with pytest.raises(typer.Exit) as e:
        processed_dep, processed_tool_dep = process_non_ross_dependency(url, language)
    assert e.value.exit_code == 7
    # assert processed_dep is None
    # assert processed_tool_dep is None


def test_15_process_non_ross_dependency_github_url_matlab_with_github_release_ok_tag():
    url = "https://github.com/g-s-k/matlab-toml@v1.0.3"
    language = "matlab"
    processed_dep, processed_tool_dep = process_non_ross_dependency(url, language)
    assert processed_dep == []
    assert processed_tool_dep.startswith("https://github.com/g-s-k/matlab-toml/blob/")


def test_16_release_twice(temp_dir_ross_project_github_repo, temp_config_path):
    release_type = None
    # First release
    release.release(release_type="patch", package_folder_path=temp_dir_ross_project_github_repo, _config_file_path=temp_config_path)   
    # Second release
    with pytest.raises(typer.Exit) as e:
        release.release(release_type="patch", package_folder_path=temp_dir_ross_project_github_repo, _config_file_path=temp_config_path)   
    assert e.value.exit_code == 6


def test_17_release_package_with_ross_dependencies(temp_package_with_ross_dependencies_dir, temp_config_path): 
    release.release(release_type="patch", package_folder_path=temp_package_with_ross_dependencies_dir, _config_file_path=temp_config_path)    


def test_18_release_with_dep_version_specified(temp_package_with_ross_dependencies_and_versions_dir, temp_config_path):    
    release.release(release_type="patch", package_folder_path=temp_package_with_ross_dependencies_and_versions_dir, _config_file_path=temp_config_path)   