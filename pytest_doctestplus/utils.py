import logging
import operator
import re
import subprocess
import sys
from distutils.version import LooseVersion

logger = logging.getLogger(__name__)


class ModuleChecker:
    def __init__(self):
        if LooseVersion(sys.version) < LooseVersion('3.4'):
            import imp
            self._find_module = imp.find_module
            self._find_distribution = self._check_distribution
            self.packages = self.get_packages()
        else:
            import importlib.util
            import pkg_resources
            self._find_module = importlib.util.find_spec
            self._find_distribution = pkg_resources.require
            self.packages = {}

    def get_packages(self):
        packages = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode().splitlines()
        packages = [package.split('==') for package in packages if '==' in package]
        return {name.lower(): version for name, version in packages}

    def compare_versions(self, v1, v2, op):
        op_map = {
            '<': operator.lt,
            '<=': operator.le,
            '>': operator.gt,
            '>=': operator.ge,
            '==': operator.eq,
        }
        if op not in op_map:
            return False
        op = op_map[op]
        return op(LooseVersion(v1), LooseVersion(v2))

    def _check_distribution(self, module):
        """
        Python 2 (and <3.4) compatible version of pkg_resources.require.
        But unlike pkg_resources.require it just checks whether package is
        installed and has required version.
        """
        match = re.match(r'([A-Za-z0-9-_]+)([^A-Za-z0-9-_]+)([\d.]+$)', module)
        if not match:
            return False
        package, cmp, version = match.groups()
        package = package.lower()

        if package in self.packages:
            installed_version = self.packages[package]
            if self.compare_versions(installed_version, version, cmp):
                return True
            else:
                logger.warning(
                    "{} {} is installed. Version {}{} is required".format(
                        package, installed_version, cmp, version
                    )
                )
                return False
        logger.warning("The '{}' distribution was not found and is required by the application".format(package))
        return False

    def find_module(self, module):
        """Search for modules specification."""
        try:
            return self._find_module(module)
        except ImportError:
            return None

    def find_distribution(self, dist):
        """Search for distribution with specified version (eg 'numpy>=1.15')."""
        try:
            return self._find_distribution(dist)
        except Exception as e:
            logger.warning(e)
            return None

    def check(self, module):
        """
        Return True if module with specified version exists.
        >>> ModuleChecker().check('foo>=1.0')
        False
        >>> ModuleChecker().check('pytest>1.0')
        True
        """
        mods = self.find_module(module) or self.find_distribution(module)
        return bool(mods)
