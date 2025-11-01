import sys
from packaging.version import Version
from platform import python_version

import pytest

PYTEST_LT_8_5 = Version(pytest.__version__) < Version('8.5.0.dev')


# Windows + Python 3.14.0 + pytest-dev have ResourceWarning, see
# https://github.com/scientific-python/pytest-doctestplus/issues/305
def pytest_runtestloop(session):
    if sys.platform == 'win32' and python_version() == "3.14.0" and not PYTEST_LT_8_5:
        session.add_marker(pytest.mark.filterwarnings('ignore::ResourceWarning'))
