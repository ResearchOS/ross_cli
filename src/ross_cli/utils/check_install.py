import re
import platform
from pathlib import Path

import typer

from ..pip_version_regex import _VERSION_PATTERN
from ..constants import CANONICAL_PACKAGE_NAME_REGEX
from ..utils.venv import get_install_loc_in_venv, get_venv_path_in_dir

VERSION_REGEX = re.compile(r"^\s*" + _VERSION_PATTERN + r"\s*$", re.VERBOSE | re.IGNORECASE)


def canonicalize_package_name(package_name: str) -> str:
    """Canonicalize the package name according to PEP 440"""
    package_name = re.sub(r'[-_.]+', '-', package_name.lower())
    if not re.match(CANONICAL_PACKAGE_NAME_REGEX, package_name, re.IGNORECASE):
        raise typer.Exit(code=16)
    return package_name


def is_package_installed(package_name: str, venv_folder: Path) -> bool:
    """Check if a package has been installed."""
    package_name = canonicalize_package_name(package_name)
    system = platform.system()
    if system == "Windows":
        package_folder = venv_folder / "Scripts" / package_name
    else:
        package_folder = venv_folder / "lib" / package_name

    return package_folder.exists()