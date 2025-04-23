from src.ross_cli.cli import *

def test_release(temp_dir_ross_project):
    release_type = "patch"
    release_command(release_type, temp_dir_ross_project)