# Licensed under a 3-clause BSD style license - see LICENSE.rst

# Skip all tests in this file since they'll all fail
__doctest_skip__ = ['*']


def bad_doctest():
    """
    This test will fail if __doctest_skip__ is not working properly.

    >>> x + y
    5
    """


def another_bad_doctest():
    """
    This test will fail if __doctest_skip__ is not working properly.

    >>> import foobar
    >>> foobar.baz()
    5
    """


def yet_another_bad_doctest():
    """
    This test will fail if __doctest_skip__ is not working properly.

    >>> NOT VALID PYTHON, RIGHT
    >>> + 7
    42
    """
