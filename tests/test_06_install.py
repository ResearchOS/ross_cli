import pytest

from src.ross_cli.cli import *

def test_01_install(temp_dir_ross_project_github_repo, temp_index_github_repo):

    # Fails to add this project to the index because the index repository is not tapped.
    with pytest.raises(typer.Exit) as e:
        add_to_index_command(temp_index_github_repo, package_folder_path=temp_dir_ross_project_github_repo)
    assert e.value.exit_code == 5


def test_02_install(temp_dir_ross_project_github_repo, temp_index_github_repo):
    # Tap the index repository
    remote_url = 'https://github.com/mtillman14/test-index'
    tap_command(remote_url)

    # Add this project to the index
    add_to_index_command(temp_index_github_repo, package_folder_path=temp_dir_ross_project_github_repo)
    
    # Tap an index, add a project to the index, and install the project.
    release_type = "patch"
    release_command(release_type, temp_dir_ross_project_github_repo)

    package_name = "test_package"
    install_relative_folder_path = os.path.join("src", "site-packages")
    install_command(package_name, install_relative_folder_path, temp_dir_ross_project_github_repo)