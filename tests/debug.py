
import sys, os
from pathlib import Path
# sys.path.insert(0, str(Path(__file__).parent.parent.parent)) 
# p = '/Users/mitchelltillman/Desktop/Not_Work/Code/Python_Projects/ross_cli/src'
# sys.path.append(p)

import pytest
# pytest.main(["-v", f"{os.path.join(os.path.dirname(__file__),"test_06_install.py")}::test_04_install_ross_package_with_ross_deps"])
pytest.main(["-v", f"{os.path.join(os.path.dirname(__file__),"test_05_release.py")}::test_17_release_package_with_ross_dependencies"])