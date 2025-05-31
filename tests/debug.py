
import sys, os
from pathlib import Path
# sys.path.insert(0, str(Path(__file__).parent.parent.parent)) 
# p = '/Users/mitchelltillman/Desktop/Not_Work/Code/Python_Projects/ross_cli/src'
# sys.path.append(p)

import pytest
# pytest.main(["-v", f"{os.path.join(os.path.dirname(__file__),"test_02_init.py")}::test_07_init_with_git_and_github"])
# pytest.main(["-v", f"{os.path.join(os.path.dirname(__file__),"test_06_install.py")}::test_02_install"])
pytest.main(["-v", f"{os.path.join(os.path.dirname(__file__),"test_05_release.py")}::test_11_process_non_ross_dependency_github_url_matlab_with_github_release"])
# pytest.main(["-v", f"{os.path.join(os.path.dirname(__file__),"test_04_add_to_index.py")}::test_02_add_to_index_after_tap"])