import os
import subprocess
import shutil

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


def test_16_release_twice(temp_dir_ross_project_github_repo, temp_config_path, gh_protocol):
    release_type = None
    # First release
    release.release(release_type="patch", package_folder_path=temp_dir_ross_project_github_repo, _config_file_path=temp_config_path)   
    # Second release
    with pytest.raises(typer.Exit) as e:
        release.release(release_type=None, package_folder_path=temp_dir_ross_project_github_repo, _config_file_path=temp_config_path)   
    assert e.value.exit_code == 6


def test_17_release_package_with_ross_dependencies_that_are_not_in_any_index(temp_package_with_ross_dependencies_dir, temp_config_path, gh_protocol): 
    with pytest.raises(typer.Exit) as e:
        release.release(release_type="patch", package_folder_path=temp_package_with_ross_dependencies_dir, _config_file_path=temp_config_path)    
    assert e.value.exit_code == 3


# def test_18_release_package_with_ross_dependencies(temp_package_with_ross_dependencies_dir_added_to_index, temp_config_path, gh_protocol): 
#     """TODO: IN THE FIRST INPUT FIXTURE, CREATE THE DEPENDENCIES' FOLDERS AND REPOS, AND ADD THEM TO THE INDEX REPO."""
#     release.release(release_type="patch", package_folder_path=temp_package_with_ross_dependencies_dir_added_to_index, _config_file_path=temp_config_path)        


# def test_19_release_with_dep_version_specified(temp_package_with_ross_dependencies_and_versions_dir, temp_config_path, gh_protocol):    
#     """TODO: IN THE FIRST INPUT FIXTURE, CREATE THE DEPENDENCIES' FOLDERS AND REPOS, AND ADD THEM TO THE INDEX REPO."""
#     release.release(release_type="patch", package_folder_path=temp_package_with_ross_dependencies_and_versions_dir, _config_file_path=temp_config_path)   


def test_20_release_with_wrong_folder_structure(temp_dir_ross_project_github_repo, temp_config_path, gh_protocol):
    # Remove the "src" folder.
    src_folder = os.path.join(temp_dir_ross_project_github_repo, "src")
    shutil.rmtree(src_folder)
    with pytest.raises(typer.Exit) as e:
        release.release(release_type="patch", package_folder_path=temp_dir_ross_project_github_repo, _config_file_path=temp_config_path)
    assert e.value.exit_code == 14


def test_21_no_repository_url_field(temp_dir_ross_project_github_repo, temp_config_path, gh_protocol):
    rossproject_toml_path = os.path.join(temp_dir_ross_project_github_repo, "rossproject.toml")
    with open(rossproject_toml_path, 'rb') as f:
        rossproject = tomli.load(f)

    if "repository_url" in rossproject:
        del rossproject["repository_url"]

    with open(rossproject_toml_path, 'wb') as f:
        tomli_w.dump(rossproject, f)

    release.release(release_type="patch", package_folder_path=temp_dir_ross_project_github_repo, _config_file_path=temp_config_path)


def test_22_validate_author_fields_string_only(temp_dir_ross_project_github_repo, temp_config_path, gh_protocol):
    rossproject_toml_path = os.path.join(temp_dir_ross_project_github_repo, "rossproject.toml")
    with open(rossproject_toml_path, 'rb') as f:
        rossproject = tomli.load(f)

    rossproject["authors"] = [
        "Mitchell"
    ]
    with open(rossproject_toml_path, 'wb') as f:
        tomli_w.dump(rossproject, f)

    with pytest.raises(typer.Exit) as e:
        release.release(release_type="patch", package_folder_path=temp_dir_ross_project_github_repo, _config_file_path=temp_config_path)
    assert e.value.exit_code == 15

    
def test_23_validate_author_fields_wrong_email(temp_dir_ross_project_github_repo, temp_config_path, gh_protocol):
    rossproject_toml_path = os.path.join(temp_dir_ross_project_github_repo, "rossproject.toml")
    with open(rossproject_toml_path, 'rb') as f:
        rossproject = tomli.load(f)

    rossproject["authors"] = [
        {"name": "Mitchell", "email": "test"}
    ]
    with open(rossproject_toml_path, 'wb') as f:
        tomli_w.dump(rossproject, f)

    with pytest.raises(typer.Exit) as e:
        release.release(release_type="patch", package_folder_path=temp_dir_ross_project_github_repo, _config_file_path=temp_config_path)
    assert e.value.exit_code == 15


def test_24_validate_author_fields_passes(temp_dir_ross_project_github_repo, temp_config_path, gh_protocol):
    rossproject_toml_path = os.path.join(temp_dir_ross_project_github_repo, "rossproject.toml")
    with open(rossproject_toml_path, 'rb') as f:
        rossproject = tomli.load(f)

    rossproject["authors"] = [
        {"name": "Mitchell", "email": "test.email@gmail.com"}
    ]
    with open(rossproject_toml_path, 'wb') as f:
        tomli_w.dump(rossproject, f)

    release.release(release_type="patch", package_folder_path=temp_dir_ross_project_github_repo, _config_file_path=temp_config_path)