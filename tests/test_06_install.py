from src.ross_cli.cli import *

def test_install(temp_project_root_directory):
    package_name = "ross_cli"
    install_folder_path = os.path.join(temp_project_root_directory, "src", "site-packages")
    install_command(package_name, install_folder_path)