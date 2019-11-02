import pytest

pytest_plugins = ['pytester']


def test_ignored_whitespace(testdir):
    testdir.makeini(
        """
        [pytest]
        doctest_optionflags = ELLIPSIS NORMALIZE_WHITESPACE
        doctestplus = enabled
    """
    )
    p = testdir.makepyfile(
        """
        class MyClass(object):
            '''
            >>> a = "foo    "
            >>> print(a)
            foo
            '''
            pass
    """
    )
    reprec = testdir.inline_run(p, "--doctest-plus")
    reprec.assertoutcome(passed=1)


def test_non_ignored_whitespace(testdir):
    testdir.makeini(
        """
        [pytest]
        doctest_optionflags = ELLIPSIS
        doctestplus = enabled
    """
    )
    p = testdir.makepyfile(
        """
        class MyClass(object):
            '''
            >>> a = "foo    "
            >>> print(a)
            foo
            '''
            pass
    """
    )
    reprec = testdir.inline_run(p, "--doctest-plus")
    reprec.assertoutcome(failed=1, passed=0)


def test_float_cmp(testdir):
    testdir.makeini(
        """
        [pytest]
        doctest_optionflags = ELLIPSIS
        doctestplus = enabled
    """
    )
    p = testdir.makepyfile(
        """
        def f():
            '''
            >>> x = 1/3.
            >>> x
            0.333333
            '''
            fail
        def g():
            '''
            >>> x = 1/3.
            >>> x    # doctest: +FLOAT_CMP
            0.333333
            '''
            pass
    """
    )
    reprec = testdir.inline_run(p, "--doctest-plus")
    reprec.assertoutcome(failed=1, passed=1)


def test_float_cmp_list(testdir):
    testdir.makeini(
        """
        [pytest]
        doctest_optionflags = ELLIPSIS
        doctestplus = enabled
    """
    )
    p = testdir.makepyfile(
        """
        def g():
            '''
            >>> x = [1/3., 2/3.]
            >>> x    # doctest: +FLOAT_CMP
            [0.333333, 0.666666]
            '''
            pass
    """
    )
    reprec = testdir.inline_run(p, "--doctest-plus")
    reprec.assertoutcome(failed=0, passed=1)


def test_float_cmp_global(testdir):
    testdir.makeini("""
        [pytest]
        doctest_optionflags = FLOAT_CMP
        doctestplus = enabled
    """)
    p = testdir.makepyfile("""
        def f():
            '''
            >>> x = 1/3.
            >>> x
            0.333333
            '''
            pass
    """)
    testdir.inline_run(p, "--doctest-plus").assertoutcome(passed=1)

    p = testdir.makepyfile("""
        def f():
            '''
            >>> x = 2/7.
            >>> x
            0.285714
            '''
            pass
    """)
    testdir.inline_run(p, "--doctest-plus").assertoutcome(passed=1)

    p = testdir.makepyfile("""
        def f():
            '''
            >>> x = 1/13.
            >>> x
            0.076923
            '''
            pass
    """)
    testdir.inline_run(p, "--doctest-plus").assertoutcome(passed=1)

    p = testdir.makepyfile("""
        def f():
            '''
            >>> x = 1/13.
            >>> x
            0.07692
            '''
            pass
    """)
    testdir.inline_run(p, "--doctest-plus").assertoutcome(failed=1)  # not close enough


@pytest.mark.xfail(reason='FLOAT_CMP and ELLIPSIS are not currently compatible')
def test_float_cmp_and_ellipsis(testdir):
    testdir.makeini(
        """
        [pytest]
        doctest_optionflags = FLOAT_CMP ELLIPSIS
        doctestplus = enabled
    """)
    p = testdir.makepyfile(
        """
        def f():
            '''
            >>> for char in ['A', 'B', 'C', 'D', 'E']:
            ...     print(char, float(ord(char)))
            A 65.0
            B 66.0
            ...
            '''
            pass
    """)
    reprec = testdir.inline_run(p, "--doctest-plus")
    reprec.assertoutcome(passed=1)


def test_allow_bytes_unicode(testdir):
    testdir.makeini(
        """
        [pytest]
        doctestplus = enabled
    """
    )
    # These are dummy tests just to check tht doctest-plus can parse the
    # ALLOW_BYTES and ALLOW_UNICODE options. It doesn't actually implement
    # these options.
    p = testdir.makepyfile(
        """
        def f():
            '''
            >>> 1 # doctest: +ALLOW_BYTES
            1
            >>> 1 # doctest: +ALLOW_UNICODE
            1
            '''
            pass
    """
    )
    reprec = testdir.inline_run(p, "--doctest-plus")
    reprec.assertoutcome(passed=1)


def test_requires(testdir):
    testdir.makeini(
        """
        [pytest]
        doctestplus = enabled
    """)

    # should be ignored
    p = testdir.makefile(
        '.rst',
        """
        .. doctest-requires:: foobar

            >>> import foobar
        """
    )
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst').assertoutcome(passed=1)

    # should run as expected
    p = testdir.makefile(
        '.rst',
        """
        .. doctest-requires:: sys

            >>> import sys
        """
    )
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst').assertoutcome(passed=1)

    # testing this in case if doctest-requires just ignores everything
    p = testdir.makefile(
        '.rst',
        """
        .. doctest-requires:: sys

            >>> import sys
            >>> assert 0
        """
    )
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst').assertoutcome(failed=1)
