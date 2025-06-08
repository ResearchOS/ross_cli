import pytest

from src.ross_cli.cli import *
from src.ross_cli.commands.index import add_to_index
from .conftest import PACKAGE_REPO_NAME

def test_01_install(temp_dir, temp_index_github_repo, temp_config_path):

    # Fails to add this project to the index because the index repository is not tapped.
    with pytest.raises(typer.Exit) as e:
        add_to_index(temp_index_github_repo, package_folder_path=temp_dir, _config_file_path=temp_config_path)        
    assert e.value.exit_code == 5


def test_02_install(temp_dir_with_venv, temp_config_path):
    # Install a ROSS package with no dependencies.

    # Install
    package_name = "load_gaitrite"
    install.install(package_name, install_package_root_folder=temp_dir_with_venv, _config_file_path = temp_config_path)
    # No version tag in the folder name because that's in the pyproject.toml
    assert os.path.exists(os.path.join(temp_dir_with_venv, ".venv", "lib", "python3.13", "site-packages", package_name))


def test_03_install_no_venv(temp_dir, temp_config_path):
    # Fails because there's no venv in this folder
    package_name = "load_gaitrite"
    with pytest.raises(typer.Exit) as e:
        install.install(package_name, install_package_root_folder=temp_dir, _config_file_path = temp_config_path)
    assert e.value.exit_code == 9


def test_04_install_ross_package_with_ross_deps(temp_package_with_ross_dependencies_dir, temp_index_github_repo, temp_config_path):
    # Tests installing a ROSS package that has other ROSS packages as dependencies.
    # e.g. segment-gaitcycles with a dependency on load-gaitrite    

    # Set up by adding the test package to the index.
    try:
        tap.tap_github_repo_for_ross_index(temp_index_github_repo, _config_file_path=temp_config_path)        
    except typer.Exit as e:
        pass
    paths = [
        "/Users/mitchelltillman/Desktop/Work/Shirley_Ryan_Postdoc/code/load-delsys",
        "/Users/mitchelltillman/Desktop/Work/Shirley_Ryan_Postdoc/code/load-xsens",
        "/Users/mitchelltillman/Desktop/Work/Shirley_Ryan_Postdoc/code/load-gaitrite"
    ]
    # Add the package being installed to the index
    try:
        add_to_index(temp_index_github_repo, package_folder_path=temp_package_with_ross_dependencies_dir, _config_file_path=temp_config_path)        
    except typer.Exit as e:
        pass
    # Add the package's dependencies to the index
    for path in paths:
        try:            
            add_to_index(temp_index_github_repo, package_folder_path=path, _config_file_path=temp_config_path)                
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
    release.release(release_type="patch", package_folder_path=temp_package_with_ross_dependencies_dir, _config_file_path=temp_config_path)    
    install.install(PACKAGE_REPO_NAME, install_package_root_folder=temp_package_with_ross_dependencies_dir, _config_file_path=temp_config_path)    
    site_packages_folder = os.path.join(temp_package_with_ross_dependencies_dir, ".venv", "lib", "python3.13", "site-packages")
    # Check main package installation
    dep_found = False
    for item in os.listdir(site_packages_folder):
        if item.startswith(PACKAGE_REPO_NAME + "-"):
            dep_found = True
            break
    assert dep_found
    # Check that the dependencies were all installed.
    for dep in deps:
        dep_found = False
        for item in os.listdir(site_packages_folder):
            if item.startswith(dep + "-"):
                dep_found = True
                break
        assert dep_found

    # Check that the dependencies' dependencies were installed.
    for dep in dep_of_deps:
        dep_found = False
        for item in os.listdir(site_packages_folder):
            if item.startswith(dep + "-"):
                dep_found = True
                break
        assert dep_found


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
        install.install(PACKAGE_REPO_NAME, install_package_root_folder=temp_package_with_ross_dependencies_dir, _config_file_path=temp_config_path)   
    assert e.value.exit_code == 4