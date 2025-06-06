import os
from pathlib import Path

import typer

def get_venv_path_in_dir(root_folder: str) -> str:
    """Return the full path to a virtual environment folder.
    Currently only works with Python's default virtual environments `python -m venv`"""
    root_folder = Path(root_folder)
    
    venv_folders = []
    for item in root_folder.iterdir():
        if not item.is_dir():
            continue
        pyvenv_cfg = item / "pyvenv.cfg"
        if pyvenv_cfg.exists():
            venv_folders.append(item)   

    if len(venv_folders) > 1:
        typer.echo(f"More than one venv found in {root_folder}")
        raise typer.Exit(code=8)
    
    if len(venv_folders) == 0:
        typer.echo(f"No venv found in {root_folder}")
        raise typer.Exit(code=9)
    
    return str(venv_folders[0])


def get_install_loc_in_venv(venv_path: str):
    """Get the folder path to the parent folder where the packages are installed.
    venv_path/lib/pythonx.xx/site-packages"""
    lib_path = Path(os.path.join(venv_path, "lib"))
    python_folder = None
    for item in lib_path.iterdir():
        if not item.is_dir():
            continue
        if item.name.startswith("python"):
            python_folder = os.path.join(str(lib_path), item)
            break

    if python_folder is None:
        typer.echo("No Python folder found in the venv!")
        raise typer.Exit()
    
    site_pkgs_folder = os.path.join(python_folder, "site-packages")
    if not os.path.exists(site_pkgs_folder):
        typer.echo(f"Missing folder in venv: {site_pkgs_folder}")
        raise typer.Exit()
    
    return site_pkgs_folder