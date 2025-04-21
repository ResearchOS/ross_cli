import os

import pytest

from ross_cli.cli import *

def test_add_to_index(temp_project_root_directory):
    index_file_url = "https://github.com/ResearchOS/test-index/index.toml"    
    with pytest.raises(typer.Exit) as exc_info:
        add_to_index_command(index_file_url, temp_project_root_directory)
    assert exc_info.value.exit_code in [0, 2]