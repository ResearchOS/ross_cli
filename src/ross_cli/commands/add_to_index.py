import os

import tomli
import tomli_w
import typer

from ..git.pyproject import build_pyproject_from_rtoproject

def update_toml_index_file(toml_file_path: str, package_name: str, remote_url: str):
    """Update the .toml file with the new package information.
    1. Check if the .toml file exists
    2. Check if the package already exists in the .toml file
    3. If not, add the package to the .toml file
    4. Save the .toml file"""
    if not os.path.isfile(toml_file_path):
        raise FileNotFoundError(f"{toml_file_path} is not a file or does not exist.")
    
    toml_content = tomli.load(toml_file_path)

    if package_name in toml_content:
        raise ValueError(f"{package_name} already exists in {toml_file_path}")
    
    toml_content[package_name] = {"url": remote_url}

    with open(toml_file_path, "wb") as f:
        tomli_w.dump(toml_content)

def create_package_structure(package_name: str, package_folder_path: str, remote_url: str = None):
    """Create the package structure of files and folders.
        - README.md
        - src/
        - tests/
        - docs/
        .gitignore"""
    paths = {}
    paths["README.md"] = os.path.join(package_folder_path, "README.md")
    paths["src/"] = os.path.join(package_folder_path, "src")
    paths["tests/"] = os.path.join(package_folder_path, "tests")
    paths["docs/"] = os.path.join(package_folder_path, "docs")
    paths[".gitignore"] = os.path.join(package_folder_path, ".gitignore")

    # Create the files and folders if they don't exist
    for field, path in paths.items():
        if not os.path.exists(path):
            if field.endswith("/"):
                os.makedirs(path)
            else:
                # Create a blank file
                with open(path, "w") as f:
                    f.write("")

    # Check if the rtoproject.toml and pyproject.toml files both exist. Return if not.
    paths["rtoproject.toml"] = os.path.join(package_folder_path, "rtoproject.toml")
    paths["pyproject.toml"] = os.path.join(package_folder_path, "pyproject.toml")
    if os.path.isfile(paths["rtoproject.toml"]) or os.path.isfile(paths["pyproject.toml"]):
        typer.echo("rtoproject.toml or pyproject.toml already exists. Not creating either of these files.")
        return 1
    
    # Build the rtoproject.toml file
    rtoproject_toml = {
        "name": package_name,
        "version": "0.1.0",
        "description": f"A new package called {package_name}",
        "language": "python",
        "dependencies": [],
        "authors": []
    }

    if remote_url:
        rtoproject_toml["repository_url"] = remote_url

    with open(paths["rtoproject.toml"], "wb") as f:
        tomli_w.dump(rtoproject_toml, f)

    # Build the pyproject.toml file from the rtoproject.toml file
    pyproject_toml = build_pyproject_from_rtoproject(rtoproject_toml)
    with open(paths["pyproject.toml"], "wb") as f:
        tomli_w.dump(pyproject_toml, f)

    return 0