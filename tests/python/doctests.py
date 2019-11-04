# Licensed under a 3-clause BSD style license - see LICENSE.rst

__doctest_skip__ = [
    'skip_this_test',
    'ClassWithSomeBadDocTests.this_test_fails',
    'ClassWithAllBadDocTests.*',
]

__doctest_requires__ = {
    'depends_on_foobar': ['foobar'],
    'depends_on_foobar_submodule': ['foobar.baz'],
    'depends_on_two_modules': ['os', 'foobar'],
}


def this_test_works():
    """
    This test should be executed by --doctest-plus and should pass.

    >>> 1 + 1
    2
    """


def skip_this_test():
    """
    This test will cause a failure if __doctest_skip__ is not working properly.

    >>> x + y
    2
    """


def depends_on_real_module():
    """
    This test should be executed by --doctest-plus and should pass.

    >>> import os
    >>> os.path.curdir
    '.'
    """


def depends_on_foobar():
    """
    This test will cause a failure if __doctest_requires__ is not working.

    >>> import foobar
    >>> foobar.foo.bar('baz')
    42
    """


def depends_on_foobar_submodule():
    """
    This test will cause a failure if __doctest_requires__ is not working.

    >>> import foobar.baz
    >>> foobar.baz.bar('baz')
    42
    """


def depends_on_two_modules():
    """
    This test will cause a failure if __doctest_requires__ is not working.

    >>> import os
    >>> import foobar
    >>> foobar.foo.bar(os.path.curdir)
    'The meaning of life'
    """


class ClassWithSomeBadDocTests(object):
    def this_test_works():
        """
        This test should be executed by --doctest-plus and should pass.

        >>> 1 + 1
        2
        """

    def this_test_fails():
        """
        This test will cause a failure if __doctest_skip__ is not working.

        >>> x + y
        5
        """


class ClassWithAllBadDocTests(object):
    def this_test_fails(self):
        """
        This test will cause a failure if __doctest_skip__ is not working.

        >>> x + y
        5
        """

    def this_test_also_fails(self):
        """
        This test will cause a failure if __doctest_skip__ is not working.

        >>> print(blue)
        'blue'
        """
