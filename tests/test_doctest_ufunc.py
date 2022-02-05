# -*- coding: utf-8 -*-
import sys
import glob

import pytest

pytest.importorskip('numpy')

pytest_plugins = ['pytester']


def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*--doctest-ufunc*Enable running doctests in '
        'docstrings of Numpy ufuncs.',
    ])


def test_example(testdir):
    # Create and build example module
    testdir.copy_example('tests/ufunc_example/_module2.c')
    testdir.copy_example('tests/ufunc_example/module1.py')
    testdir.copy_example('tests/ufunc_example/module2.py')
    testdir.copy_example('tests/ufunc_example/setup.py')
    testdir.run(sys.executable, 'setup.py', 'build')
    build_dir, = glob.glob(str(testdir.tmpdir / 'build/lib.*'))

    # Run pytest without doctests: 0 tests run
    result = testdir.runpytest(build_dir)
    result.assert_outcomes(passed=0, failed=0)

    # Run pytest with doctests: 1 test run
    result = testdir.runpytest(build_dir, '--doctest-modules')
    result.assert_outcomes(passed=1, failed=0)

    # Run pytest with doctests including ufuncs: 2 tests run
    result = testdir.runpytest(build_dir, '--doctest-plus', '--doctest-modules', '--doctest-ufunc')
    result.assert_outcomes(passed=2, failed=0)
