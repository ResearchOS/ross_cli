import pytest

from src.ross_cli.cli import *

def test_01_install(temp_dir, temp_index_github_repo):

    # Fails to add this project to the index because the index repository is not tapped.
    with pytest.raises(typer.Exit) as e:
        add_to_index_command(temp_index_github_repo, package_folder_path=temp_dir)
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