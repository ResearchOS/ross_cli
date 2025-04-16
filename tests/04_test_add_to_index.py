import os

from ross_cli.cli import *

def test_add_to_index():
    index_file_url = ""
    package_folder_path = os.getcwd()
    add_to_index_command(index_file_url, package_folder_path)