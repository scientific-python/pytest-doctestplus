#!/usr/bin/env python

import os
import sys
import setuptools
from distutils.version import LooseVersion
from setuptools import setup

# Setuptools 30.3.0 or later is needed for setup.cfg options to be used
if LooseVersion(setuptools.__version__) < LooseVersion('30.3.0'):
    sys.stderr.write("ERROR: sphinx-automodapi requires setuptools 30.3.0 or "
                     "later (found {0})".format(setuptools.__version__))
    sys.exit(1)

<<<<<<< HEAD
def readme():
    with open('README.rst') as ff:
        return ff.read()


setup(
    name='pytest-doctestplus',
    version='0.9.0.dev0',
    license='BSD',
    description='Pytest plugin with advanced doctest features.',
    long_description=readme(),
    long_description_content_type='text/x-rst',
    author='The Astropy Developers',
    author_email='astropy.team@gmail.com',
    url='https://astropy.org',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
    ],
    keywords=['doctest', 'rst', 'pytest', 'py.test'],
    install_requires=['pytest>=4.0', 'pip'],
    python_requires='>=3.6',
    entry_points={
        'pytest11': [
            'pytest_doctestplus = pytest_doctestplus.plugin',
        ],
    },
)
=======
setup(use_scm_version={'write_to': os.path.join('pytest_doctestplus', 'version.py')})
>>>>>>> 686f1a9... Updated package infrastructure to use tox for testing and setuptools_scm for version numbers
