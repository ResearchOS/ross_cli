from ross_cli.cli import *

def test_config():
    config_command()

def test_version():
    version_callback(value=True)