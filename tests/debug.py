
import sys, os
from pathlib import Path
# sys.path.insert(0, str(Path(__file__).parent.parent.parent)) 
# p = '/Users/mitchelltillman/Desktop/Not_Work/Code/Python_Projects/ross_cli/src'
# sys.path.append(p)

import pytest
pytest.main(["-v", f"{os.path.join(os.path.dirname(__file__),"test_05_release.py")}::test_04_parse_dependency_wrong_language"])

# from ross_cli.cli import *
# from ross_cli.commands.tap import tap_github_repo_for_ross_index, untap_ross_index

# REMOTE_URL = "https://github.com/ResearchOS/test-index/"
# temp_config_path = os.path.expanduser("~/Downloads/test_config.toml")
# tap_github_repo_for_ross_index(REMOTE_URL, _config_file_path=temp_config_path)
# untap_ross_index(REMOTE_URL, _config_file_path=temp_config_path)

# Initialize the CLI config
# cli_init_command()

# # Initialize the project
# init_command()

# # Tap an index repository
# index_repo_url = "https://github.com/ResearchOS/test-index"
# tap_command(index_repo_url)
# untap_command(index_repo_url)
# tap_command(index_repo_url)

# Add a project to an index
index_file_url = 'https://github.com/ResearchOS/test-index/blob/main/index.toml'
# index_file_url = 'ResearchOS/test-index'
# add_to_index_command(index_file_url)

# release_command(None)
# install_command("load-gaitrite")