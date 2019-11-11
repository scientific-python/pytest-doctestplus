import pytest

import doctest
from pytest_doctestplus.output_checker import OutputChecker, FLOAT_CMP


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


def test_float_cmp_and_ellipsis(testdir):
    testdir.makeini(
        """
        [pytest]
        doctest_optionflags = FLOAT_CMP ELLIPSIS
        doctestplus = enabled
    """)
    # whitespace is normalized by default
    p = testdir.makepyfile(
        """
        from __future__ import print_function
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
    testdir.inline_run(p, "--doctest-plus").assertoutcome(passed=1)

    p = testdir.makepyfile(
        """
        from __future__ import print_function
        def f():
            '''
            >>> for char in ['A', 'B', 'C', 'D', 'E']:
            ...     print(char, float(ord(char)))
            A 65.0
            B 66.0
            ...
            E 69.0
            '''
            pass
    """)
    testdir.inline_run(p, "--doctest-plus").assertoutcome(passed=1)

    p = testdir.makepyfile(
        """
        from __future__ import print_function
        def f():
            '''
            >>> for char in ['A', 'B', 'C', 'D', 'E']:
            ...     print(char, float(ord(char)))
            A 65.0
            ...
            C 67.0
            ...
            E 69.0
            '''
            pass
    """)
    testdir.inline_run(p, "--doctest-plus").assertoutcome(passed=1)

    p = testdir.makepyfile(
        """
        from __future__ import print_function
        def f():
            '''
            >>> for char in ['A', 'B', 'C', 'D', 'E']:
            ...     print(char, float(ord(char)))
            A 65.0
            ...
            E 70.0
            '''
            pass
    """)
    testdir.inline_run(p, "--doctest-plus").assertoutcome(failed=1)


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


class TestFloats:
    def test_normalize_floats(self):
        c = OutputChecker()
        got = "A 65.0\nB 66.0"

        want = "A 65.0\nB 66.0"
        assert c.normalize_floats(want, got, flags=FLOAT_CMP)

        want = "A 65.0\nB   66.0  "
        assert c.normalize_floats(want, got, flags=FLOAT_CMP | doctest.NORMALIZE_WHITESPACE)

        want = "A 65.0\nB 66.01"
        assert not c.normalize_floats(want, got, flags=FLOAT_CMP)

    def test_normalize_with_blank_line(self):
        c = OutputChecker()
        got = "\nA 65.0\nB 66.0"
        want = "<BLANKLINE>\nA 65.0\nB 66.0"
        assert c.normalize_floats(want, got, flags=FLOAT_CMP)
        assert not c.normalize_floats(want, got, flags=FLOAT_CMP | doctest.DONT_ACCEPT_BLANKLINE)

    def test_normalize_with_ellipsis(self):
        c = OutputChecker()
        got = []
        for char in ['A', 'B', 'C', 'D', 'E']:
            got.append('%s %s' % (char, float(ord(char))))
        got = '\n'.join(got)

        want = "A 65.0\nB 66.0\n...G 70.0"
        assert not c.normalize_floats(want, got, flags=doctest.ELLIPSIS | FLOAT_CMP)

        want = "A 65.0\nB 66.0\n..."
        assert c.normalize_floats(want, got, flags=doctest.ELLIPSIS | FLOAT_CMP)

        want = "A 65.0\nB 66.0\n...\nE 69.0"
        assert c.normalize_floats(want, got, flags=doctest.ELLIPSIS | FLOAT_CMP)

        got = "\n" + got
        want = "<BLANKLINE>\nA 65.0\nB 66.0\n..."
        assert c.normalize_floats(want, got, flags=doctest.ELLIPSIS | FLOAT_CMP)

    def test_partial_match(self):
        c = OutputChecker()

        assert not c.partial_match(
            ['1', '2', '3', '4'],
            [['2'], []],
        )
        assert c.partial_match(
            ['1', '2', '3', '4'],
            [[], ['2'], []],
        )
        assert c.partial_match(
            ['1', '2', '3', '4'],
            [['1', '2'], []],
        )
        assert c.partial_match(
            ['1', '2', '3', '4'],
            [['1', '2'], ['4']],
        )
        assert c.partial_match(
            ['1', '2', '3', '4', '5'],
            [['1', '2'], ['4', '5']],
        )
        assert c.partial_match(
            ['1', '2', '3', '4', '5', '6'],
            [['1', '2'], ['4'], ['6']],
        )
        assert c.partial_match(
            [str(i) for i in range(20)],
            [[], ['1', '2'], ['4'], ['6'], []],
        )
        assert not c.partial_match(
            [str(i) for i in range(20)],
            [[], ['1', '2'], ['7'], ['6'], []],
        )


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

    # testing this in case if doctest-requires just ignores everything and pass unconditionally
    p = testdir.makefile(
        '.rst',
        """
        .. doctest-requires:: sys glob, re,math
            >>> import sys
            >>> assert 0
        """
    )
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst').assertoutcome(failed=1)

    # package with version is available
    p = testdir.makefile(
        '.rst',
        """
        .. doctest-requires:: sys pytest>=1.0
            >>> import sys, pytest
        """
    )
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst').assertoutcome(passed=1)

    # package with version is not available
    p = testdir.makefile(
        '.rst',
        """
        .. doctest-requires:: sys pytest<1.0 glob
            >>> import sys, pytest, glob
            >>> assert 0
        """
    )
    # passed because 'pytest<1.0' was not satisfied and 'assert 0' was not evaluated
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst').assertoutcome(passed=1)


def test_ignore_warning_module(testdir):

    # First check that we get a warning if we don't add the IGNORE_WARNING
    # directive
    p = testdir.makepyfile(
        """
        def myfunc():
            '''
            >>> import warnings
            >>> warnings.warn('A warning occurred', UserWarning)
            '''
            pass
        """)
    reprec = testdir.inline_run(p, "--doctest-plus", "-W error")
    reprec.assertoutcome(failed=1, passed=0)

    # Now try with the IGNORE_WARNING directive
    p = testdir.makepyfile(
        """
        def myfunc():
            '''
            >>> import warnings
            >>> warnings.warn('A warning occurred', UserWarning)  # doctest: +IGNORE_WARNING
            '''
            pass
        """)
    reprec = testdir.inline_run(p, "--doctest-plus", "-W error")
    reprec.assertoutcome(failed=0, passed=1)


def test_ignore_warning_rst(testdir):

    # First check that we get a warning if we don't add the IGNORE_WARNING
    # directive
    p = testdir.makefile(".rst",
        """
        ::
            >>> import warnings
            >>> warnings.warn('A warning occurred', UserWarning)
        """)
    reprec = testdir.inline_run(p, "--doctest-plus", "--doctest-rst",
                                "--text-file-format=rst", "-W error")
    reprec.assertoutcome(failed=1, passed=0)

    # Now try with the IGNORE_WARNING directive
    p = testdir.makefile(".rst",
        """
        ::
            >>> import warnings
            >>> warnings.warn('A warning occurred', UserWarning)  # doctest: +IGNORE_WARNING
        """)
    reprec = testdir.inline_run(p, "--doctest-plus", "--doctest-rst",
                                "--text-file-format=rst", "-W error")
    reprec.assertoutcome(failed=0, passed=1)