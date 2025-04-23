import pytest
import subprocess

from src.ross_cli.cli import *

def test_config():
    config_command()

def test_version():
    subprocess.run(["pip", "install", "."])
    with pytest.raises(typer.Exit):
        version_callback(value=True)
    try:
        subprocess.run(["pip", "uninstall", "ross_cli", "-y"])
    except:
        pass