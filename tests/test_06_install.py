import pytest

from src.ross_cli.cli import *

def test_01_install(temp_dir_ross_project_github_repo, temp_index_github_repo):

    # Fails to add this project to the index because the index repository is not tapped.
    with pytest.raises(typer.Exit) as e:
        add_to_index_command(temp_index_github_repo, package_folder_path=temp_dir_ross_project_github_repo)
    assert e.value.exit_code == 5


def test_02_install(temp_dir):
    # Install a ROSS package

    # Install
    package_name = "load_gaitrite"
    install_command(package_name, install_package_root_folder=temp_dir)
    # No version tag in the folder name because that's in the pyproject.toml
    assert os.path.exists(os.path.join(temp_dir, "src", "site-packages", package_name))