
import os

import pytest
# pytest.main(["-v", f"{os.path.join(os.path.dirname(__file__),"test_06_install.py")}::test_05_install_ross_package_missing_rossproject_file"])
pytest.main(["-v", f"{os.path.join(os.path.dirname(__file__),"test_05_release.py")}::test_18_release_with_dep_version_specified"])