#!/usr/bin/env python
# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages


def readme():
    with open('README.rst') as ff:
        return ff.read()


setup(
    name='pytest-doctestplus',
    version='0.5.0',
    license='BSD',
    description='Pytest plugin with advanced doctest features.',
    long_description=readme(),
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
    ],
    keywords=['doctest', 'rst', 'pytest', 'py.test'],
    install_requires=['six', 'pytest>=3.0'],
    python_requires='>=2.7',
    entry_points={
        'pytest11': [
            'pytest_doctestplus = pytest_doctestplus.plugin',
        ],
    },
)
