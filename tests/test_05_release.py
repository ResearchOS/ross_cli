from ross_cli.cli import *

def test_release():
    release_type = "patch"
    release_command(release_type)