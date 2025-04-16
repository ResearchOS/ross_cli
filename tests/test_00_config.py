import pytest

from src.ross_cli.cli import *

def test_config():
    config_command()

def test_version():
    with pytest.raises(typer.Exit):
        version_callback(value=True)