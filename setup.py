#!/usr/bin/env python

import os
from setuptools import setup

setup(use_scm_version={'write_to': os.path.join('pytest_doctestplus', 'version.py')})
