from src.ross_cli.cli import *

def test_install(temp_dir_ross_project_github_repo):
    # Tap an index, add a project to the index, and install the project.
    release_type = "patch"
    release_command(release_type, temp_dir_ross_project_github_repo)

    package_name = "test_package"
    install_relative_folder_path = os.path.join("src", "site-packages")
    install_command(package_name, install_relative_folder_path, temp_dir_ross_project_github_repo)