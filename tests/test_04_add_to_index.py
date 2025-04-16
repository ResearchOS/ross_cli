import os

import pytest

from ross_cli.cli import *

def test_add_to_index():
    index_file_url = "https://github.com/ResearchOS/test-index/index.toml"
    package_folder_path = os.getcwd()
    with pytest.raises(typer.Exit) as exc_info:
        add_to_index_command(index_file_url, package_folder_path)
    assert exc_info.value.exit_code in [0, 2]