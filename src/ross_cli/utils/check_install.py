import re

import typer

from ..pip_version_regex import _VERSION_PATTERN
from ..constants import CANONICAL_PACKAGE_NAME_REGEX

VERSION_REGEX = re.compile(r"^\s*" + _VERSION_PATTERN + r"\s*$", re.VERBOSE | re.IGNORECASE)


def canonicalize_package_name(package_name: str) -> str:
    """Canonicalize the package name according to PEP 440"""
    package_name = re.sub(r'[-_.]+', '-', package_name.lower())
    if not re.match(CANONICAL_PACKAGE_NAME_REGEX, package_name, re.IGNORECASE):
        raise typer.Exit(exit_code=16)