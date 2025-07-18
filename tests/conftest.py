import os
import tempfile
import subprocess

import pytest
import tomli
import tomli_w

from src.ross_cli.cli import init_command
from src.ross_cli.commands import index, tap

PACKAGE_REPO_NAME = "test_repo"

ROSSPROJECT_TOML_CONTENT_TEST = """# ROSS project configuration file
name = "{PACKAGE_REPO_NAME}"
version = "0.1.0"
language = "python"
authors = [

]
dependencies = [
    # "load-gaitrite",
]
readme = "README.md"
"""

def get_owner_from_github_username():
    result = subprocess.run("gh api user --jq .login", shell=True, capture_output=True, check=True)
    OWNER = result.stdout.decode().strip()
    return OWNER

INDEX_REPO_NAME = "index"
OWNER = get_owner_from_github_username() # For multi-user testability
INDEX_TOML_REPO_URL = f"https://github.com/{OWNER}/{INDEX_REPO_NAME}/index.toml"

def create_github_repo(temp_dir: str, index: bool = False):
    os.chdir(temp_dir)
    # Initialize git and configure basic settings
    subprocess.run(["git", "init"], check=True)
    
    # Create and configure GitHub repository
    if index:
        repo_name = INDEX_REPO_NAME
    else:
        repo_name = PACKAGE_REPO_NAME
    try:
        subprocess.run(["gh", "repo", "create", repo_name, "--private"], check=True)        
    except subprocess.CalledProcessError as e:
        pass # Repo already exists because test was aborted.    
    try:
        subprocess.run(["git", "remote", "add", "origin", 
                    f"https://github.com/{OWNER}/{repo_name}.git"], 
                    check=True)        
    except subprocess.CalledProcessError as e:
        pass
    try:
        subprocess.run("git branch --set-upstream-to=origin/main main", shell=True)
    except subprocess.CalledProcessError as e:
        pass
    
    # Create initial commit and push
    subprocess.run(["git", "pull"])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "--allow-empty", "-m", "Initial commit"], check=True)
    subprocess.run(["git", "push"], check=True)

##########################################################
######################## FIXTURES ########################
##########################################################

# @pytest.fixture(scope="session", params=["https", "ssh"])
@pytest.fixture(scope="session", params=["https"])
def gh_protocol(request):
    """Configure gh CLI to use either https or ssh protocol"""
    protocol = request.param
    
    # Store original config
    original_config = subprocess.run(
        ["gh", "config", "get", "git_protocol"], 
        capture_output=True, text=True
    ).stdout.strip()
    
    # Set new protocol
    subprocess.run(["gh", "config", "set", "git_protocol", protocol])
    
    yield protocol
    
    # Restore original config
    if original_config:
        subprocess.run(["gh", "config", "set", "git_protocol", original_config])

@pytest.fixture(scope="function")
def temp_config_path():
    """ROSS configuration file path"""
    # Temporary config file
    with tempfile.NamedTemporaryFile(suffix=".toml") as temp_file:
        path = temp_file.name        
        yield path


@pytest.fixture(scope="function")
def temp_dir():
    """Temporary directory"""
    # Folder only
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(scope="function")
def temp_dir_with_venv():
    """Temporary directory"""
    # Folder only
    with tempfile.TemporaryDirectory() as temp_dir:        
        os.chdir(temp_dir)
        subprocess.run(["python3", "-m", "venv", ".venv"])
        yield temp_dir


@pytest.fixture(scope="function")
def temp_dir_with_git_repo():
    """Temporary directory with git repository"""
    # Folder and git repository    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize a git repository in the temporary directory
        subprocess.run(["git", "init", temp_dir])        
        yield temp_dir


@pytest.fixture(scope="function")
def temp_dir_with_github_repo():
    """Temporary directory with github repository"""
    # Reset GitHub repo
    try:
        subprocess.run(["gh", "repo", "delete", PACKAGE_REPO_NAME, "--yes"], check=True)
    except subprocess.CalledProcessError as e:
        pass
    # Folder and git repository
    temp_dir = tempfile.mkdtemp()  # Create temporary directory    
    
    try:
        create_github_repo(temp_dir)
        yield temp_dir
    finally:        
        try:
            subprocess.run(["gh", "repo", "delete", PACKAGE_REPO_NAME, "--yes"], check=True)
        except subprocess.CalledProcessError:
            pass


@pytest.fixture(scope="function")
def temp_dir_ross_project():
    """Temporary directory with git repository and ross project structure, but no GitHub repo.
    NOTE: `ross init` requires a GitHub repository to be created first, so this fixture is only helpful so as to not need to create a GitHub repo."""
    # Initialized ross project.
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize a git repository in the temporary directory
        subprocess.run(["git", "init", temp_dir])
        # Create a sample ross project structure
        src_folder = os.path.join(temp_dir, "src")
        os.makedirs(src_folder, exist_ok=True)  # Replace mkdir -p
        
        # Create empty files using Python's open()
        with open(os.path.join(src_folder, "__init__.py"), 'w') as f:
            f.write("")
        with open(os.path.join(temp_dir, "rossproject.toml"), 'w') as f:
            f.write(ROSSPROJECT_TOML_CONTENT_TEST.format(PACKAGE_REPO_OWNER=OWNER, PACKAGE_REPO_NAME=PACKAGE_REPO_NAME))
        yield temp_dir


@pytest.fixture(scope="function")
def temp_dir_ross_project_github_repo():
    """Temporary directory with git repository and ross project structure, including a GitHub repo"""
    # Reset the GitHub repo status
    try:
        subprocess.run(["gh", "repo", "delete", PACKAGE_REPO_NAME, "--yes"], check=True)
    except subprocess.CalledProcessError as e:
        pass
    # Initialized ross project.
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            create_github_repo(temp_dir)
                        
            # Create a sample ross project structure
            src_folder = os.path.join(temp_dir, "src")
            os.makedirs(src_folder, exist_ok=True)
            project_src_folder = os.path.join(src_folder, PACKAGE_REPO_NAME)
            os.makedirs(project_src_folder)

            # Create the content of the GitHub repository
            with open(os.path.join(temp_dir, "README.md"), 'w') as f:
                f.write(f"# {PACKAGE_REPO_NAME}")

            # Create empty files using Python's open()
            with open(os.path.join(project_src_folder, "__init__.py"), 'w') as f:
                f.write("# test_package")
            with open(os.path.join(temp_dir, "rossproject.toml"), 'w') as f:
                f.write(ROSSPROJECT_TOML_CONTENT_TEST.format(PACKAGE_REPO_OWNER=OWNER, PACKAGE_REPO_NAME=PACKAGE_REPO_NAME))

            # Create initial commit and push
            subprocess.run(["git", "pull"])
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
            subprocess.run(["git", "push"], check=True)
            yield temp_dir

        finally:            
            try:
                subprocess.run(["gh", "repo", "delete", PACKAGE_REPO_NAME, "--yes"], check=True)
            except subprocess.CalledProcessError as e:
                pass


@pytest.fixture(scope="function")
def temp_index_github_repo_url_only():
    """URL for the index GitHub repository, but no actual repository"""
    yield INDEX_TOML_REPO_URL


@pytest.fixture(scope="function")
def temp_index_github_repo():
    """URL for the index GitHub repository, and create the actual repository"""
    try:
        subprocess.run(["gh", "repo", "create", INDEX_REPO_NAME, "--private"], check=True)
    except subprocess.CalledProcessError as e:
        pass
    yield INDEX_TOML_REPO_URL
    subprocess.run(["gh", "repo", "delete", INDEX_REPO_NAME, "--yes"], check=True)
    

@pytest.fixture(scope="function")
def temp_package_with_ross_dependencies_dir(temp_dir_ross_project_github_repo):    

    # 1. Write ross dependencies to rossproject.toml
    init_command(PACKAGE_REPO_NAME, package_path=temp_dir_ross_project_github_repo)
    rossproject_path = os.path.join(temp_dir_ross_project_github_repo, "rossproject.toml")
    with open(rossproject_path, 'rb') as f:
        rossproject = tomli.load(f)
    rossproject["dependencies"] = [
        "load_gaitrite",
        "load_xsens",
        "load_delsys"
    ]
    rossproject["language"] = "matlab"
    with open(rossproject_path, 'wb') as f:
        tomli_w.dump(rossproject, f)

    # 2. Create git repo and github repository    
    subprocess.run(["git", "pull"])
    subprocess.run("python3 -m venv .venv", shell=True) # Add the .venv
    subprocess.run("git add .", shell=True)
    subprocess.run("git commit -m 'Added ROSS dependencies'", shell=True)
    subprocess.run(f"git push -u origin main", shell=True)
    yield temp_dir_ross_project_github_repo


@pytest.fixture(scope="function")
def temp_package_with_ross_dependencies_dir_added_to_index(temp_dir_ross_project_github_repo, temp_config_path):    
    """Replica of the `temp_package_with_ross_dependencies_dir` fixture, but adds the packages to the index repository."""

    # 1. Write ross dependencies to rossproject.toml
    init_command(PACKAGE_REPO_NAME, package_path=temp_dir_ross_project_github_repo)
    rossproject_path = os.path.join(temp_dir_ross_project_github_repo, "rossproject.toml")
    with open(rossproject_path, 'rb') as f:
        rossproject = tomli.load(f)
    rossproject["dependencies"] = [
        "load_gaitrite",
        "load_xsens",
        "load_delsys"
    ]
    rossproject["language"] = "matlab"
    with open(rossproject_path, 'wb') as f:
        tomli_w.dump(rossproject, f)

    # 2. Add the package to the index repository    
    create_github_repo(temp_dir_ross_project_github_repo, index=True)
    INDEX_REPO_URL = f"https://github.com/{OWNER}/{INDEX_REPO_NAME}"
    tap.tap_github_repo_for_ross_index(index_remote_url=INDEX_REPO_URL, _config_file_path=temp_config_path)
    index.add_to_index(index_file_url=INDEX_TOML_REPO_URL, package_folder_path=temp_dir_ross_project_github_repo, _config_file_path=temp_config_path)    

    # 2. Create git repo and github repository    
    subprocess.run(["git", "pull"])
    subprocess.run("python3 -m venv .venv", shell=True) # Add the .venv
    subprocess.run("git add .", shell=True)
    subprocess.run("git commit -m 'Added ROSS dependencies'", shell=True)
    subprocess.run(f"git push -u origin main", shell=True)
    yield temp_dir_ross_project_github_repo


@pytest.fixture(scope="function")
def temp_package_with_ross_dependencies_and_versions_dir(temp_dir_ross_project_github_repo):    

    # 1. Write ross dependencies to rossproject.toml
    init_command(PACKAGE_REPO_NAME, package_path=temp_dir_ross_project_github_repo)
    rossproject_path = os.path.join(temp_dir_ross_project_github_repo, "rossproject.toml")
    with open(rossproject_path, 'rb') as f:
        rossproject = tomli.load(f)
    rossproject["dependencies"] = [
        "load_gaitrite==0.1.3",
        "load_xsens==0.1.1",
        "load_delsys==0.1.1"
    ]
    rossproject["language"] = "matlab"
    with open(rossproject_path, 'wb') as f:
        tomli_w.dump(rossproject, f)

    # 2. Create git repo and github repository    
    subprocess.run(["git", "pull"])
    subprocess.run("python3 -m venv .venv", shell=True) # Add the .venv
    subprocess.run("git add .", shell=True)
    subprocess.run("git commit -m 'Added ROSS dependencies'", shell=True)
    subprocess.run(f"git push -u origin main", shell=True)
    yield temp_dir_ross_project_github_repo