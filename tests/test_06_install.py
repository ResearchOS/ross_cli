from src.ross_cli.cli import *

def test_install(temp_dir_ross_project_github_repo):
    package_name = "ross_cli"
    install_folder_path = os.path.join(temp_dir_ross_project_github_repo, "src", "site-packages")
    install_command(package_name, install_folder_path)