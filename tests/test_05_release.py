from ross_cli.cli import *

def test_release(temp_project_root_directory):
    release_type = "patch"
    release_command(release_type, temp_project_root_directory)