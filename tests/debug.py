
import os

import pytest
# pytest.main(["-v", f"{os.path.join(os.path.dirname(__file__),"test_06_install.py")}::test_04_install_ross_package_with_ross_deps"])
pytest.main(["-v", f"{os.path.join(os.path.dirname(__file__),"test_06_install.py")}::test_01_install"])
# pytest.main(["-v", f"{os.path.join(os.path.dirname(__file__),"test_05_release.py")}::test_20_no_repository_url_field"])