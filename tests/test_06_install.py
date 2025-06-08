import pytest

from src.ross_cli.cli import *
from src.ross_cli.commands.index import add_to_index
from .conftest import PACKAGE_REPO_NAME

def test_01_install(temp_dir, temp_index_github_repo, temp_config_path):

    # Fails to add this project to the index because the index repository is not tapped.
    with pytest.raises(typer.Exit) as e:
        add_to_index(temp_index_github_repo, package_folder_path=temp_dir, _config_file_path=temp_config_path)
        # add_to_index_command(temp_index_github_repo, package_folder_path=temp_dir)
    assert e.value.exit_code == 5


def test_02_install(temp_dir_with_venv):
    # Install a ROSS package with no dependencies.

    # Install
    package_name = "load_gaitrite"
    install_command(package_name, install_package_root_folder=temp_dir_with_venv)
    # No version tag in the folder name because that's in the pyproject.toml
    assert os.path.exists(os.path.join(temp_dir_with_venv, ".venv", "lib", "python3.13", "site-packages", package_name))


def test_03_install_no_venv(temp_dir):
    # Fails because there's no venv in this folder
    package_name = "load_gaitrite"
    with pytest.raises(typer.Exit) as e:
        install_command(package_name, install_package_root_folder=temp_dir)
    assert e.value.exit_code == 9


def test_04_install_ross_package_with_ross_deps(temp_package_with_ross_dependencies_dir, temp_index_github_repo, temp_config_path):
    # Tests installing a ROSS package that has other ROSS packages as dependencies.
    # e.g. segment-gaitcycles with a dependency on load-gaitrite    

    # Set up by adding the test package to the index.
    try:
        tap.tap_github_repo_for_ross_index(temp_index_github_repo, _config_file_path=temp_config_path)
        # tap_command(temp_index_github_repo)
    except typer.Exit as e:
        pass
    try:
        add_to_index(temp_index_github_repo, package_folder_path=temp_package_with_ross_dependencies_dir, _config_file_path=temp_config_path)
        # add_to_index_command(temp_index_github_repo, package_folder_path=temp_package_with_ross_dependencies_dir)
    except typer.Exit as e:
        pass
    deps = [
        "load_gaitrite",
        "load_xsens",
        "load_delsys",        
    ]
    dep_of_deps = [
        "matlab-toml"
    ]
    release_command(release_type="patch", package_folder_path=temp_package_with_ross_dependencies_dir)
    install.install(PACKAGE_REPO_NAME, install_package_root_folder=temp_package_with_ross_dependencies_dir, _config_file_path=temp_config_path)    
    assert os.path.exists(os.path.join(temp_package_with_ross_dependencies_dir, ".venv", "lib", "python3.13", "site-packages", PACKAGE_REPO_NAME))
    # Check that the dependencies were all installed.
    for dep in deps:
        assert os.path.exists(os.path.join(temp_package_with_ross_dependencies_dir, ".venv", "lib", "python3.13", "site-packages", dep))
    # Check that the dependencies' dependencies were installed.
    for dep in dep_of_deps:
        assert os.path.exists(os.path.join(temp_package_with_ross_dependencies_dir, ".venv", "lib", "python3.13", "site-packages", dep))


def test_05_install_ross_package_missing_rossproject_file(temp_package_with_ross_dependencies_dir, temp_index_github_repo, temp_config_path):
    # Fails because the package being installed is missing a pyproject.toml file.

    # Set up by adding the test package to the index.
    try:
        tap.tap_github_repo_for_ross_index(temp_index_github_repo, _config_file_path=temp_config_path)
        # tap_command(temp_index_github_repo)
    except typer.Exit as e:
        pass
    try:
        add_to_index(temp_index_github_repo, package_folder_path=temp_package_with_ross_dependencies_dir, _config_file_path=temp_config_path)
        # add_to_index_command(temp_index_github_repo, package_folder_path=temp_package_with_ross_dependencies_dir)
    except typer.Exit as e:
        pass

    with pytest.raises(typer.Exit) as e:
        install_command(PACKAGE_REPO_NAME, install_package_root_folder=temp_package_with_ross_dependencies_dir)
    assert e.value.exit_code == 4