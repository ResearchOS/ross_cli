
import sys
from pathlib import Path
# sys.path.insert(0, str(Path(__file__).parent.parent.parent)) 
p = '/Users/mitchelltillman/Desktop/Not_Work/Code/Python_Projects/ross_cli/src'
sys.path.append(p)

from ross_cli.cli import *

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
# index_file_url = 'https://github.com/ResearchOS/test-index/blob/main/index.toml'
# add_to_index_command(index_file_url)

# release_command(None)
install_command("load-gaitrite")