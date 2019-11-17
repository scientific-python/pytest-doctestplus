import doctest
from distutils.version import LooseVersion
from textwrap import dedent

import pytest


def test_ignored_whitespace(testdir, docdir):
    testdir.makeini("""\
        [pytest]
        doctest_optionflags = ELLIPSIS NORMALIZE_WHITESPACE
        doctestplus = enabled
    """)
    p = docdir.makepyfile("""\
        >>> a = "foo    "
        >>> print(a)
        foo
    """)
    docdir.test(p, passed=1)


def test_non_ignored_whitespace(testdir, docdir):
    testdir.makeini("""\
        [pytest]
        doctest_optionflags = ELLIPSIS
        doctestplus = enabled
    """)
    p = docdir.makepyfile("""\
        >>> a = "foo    "
        >>> print(a)
        foo
    """)
    docdir.test(p, failed=1)


def test_float_cmp(testdir, docdir):
    testdir.makeini("""\
        [pytest]
        doctest_optionflags = ELLIPSIS
        doctestplus = enabled
    """)
    p = docdir.makepyfile(
        foo="""
            >>> x = 1/3.
            >>> x
            0.333333
        """,
        bar="""
            >>> x = 1/3.
            >>> x    # doctest: +FLOAT_CMP
            0.333333
        """,
    )
    docdir.test(p, failed=1, passed=1)


def test_float_cmp_list(testdir, docdir):
    testdir.makeini("""\
        [pytest]
        doctest_optionflags = ELLIPSIS
        doctestplus = enabled
    """)
    p = docdir.makepyfile("""\
        >>> x = [1/3., 2/3.]
        >>> x    # doctest: +FLOAT_CMP
        [0.333333, 0.666666]
    """)
    docdir.test(p, passed=1)


def test_float_cmp_global(testdir, docdir):
    testdir.makeini("""\
        [pytest]
        doctest_optionflags = FLOAT_CMP
        doctestplus = enabled
    """)
    p = docdir.makepyfile("""\
        >>> x = 1/3.
        >>> x
        0.333333
    """)
    docdir.test(p, passed=1)

    p = docdir.makepyfile("""\
        >>> x = 2/7.
        >>> x
        0.285714
    """)
    docdir.test(p, passed=1)

    p = docdir.makepyfile("""\
        >>> x = 1/13.
        >>> x
        0.076923
    """)
    docdir.test(p, passed=1)

    p = docdir.makepyfile("""\
        >>> x = 1/13.
        >>> x
        0.07692
    """)
    docdir.test(p, failed=1)


def test_float_cmp_and_ellipsis(testdir, docdir):
    testdir.makeini("""\
        [pytest]
        doctest_optionflags = FLOAT_CMP ELLIPSIS
        doctestplus = enabled
    """)
    # whitespace is normalized by default
    p = docdir.makepyfile("""\
        >>> for char in ['A', 'B', 'C', 'D', 'E']:
        ...     print(char, float(ord(char)))
        A 65.0
        B 66.0
        ...
    """)
    docdir.test(p, passed=1)

    p = docdir.makepyfile("""\
        >>> for char in ['A', 'B', 'C', 'D', 'E']:
        ...     print(char, float(ord(char)))
        A 65.0
        B 66.0
        ...
        E 69.0
    """)
    docdir.test(p, passed=1)

    p = docdir.makepyfile("""\
        >>> for char in ['A', 'B', 'C', 'D', 'E']:
        ...     print(char, float(ord(char)))
        A 65.0
        ...
        C 67.0
        ...
        E 69.0
    """)
    docdir.test(p, passed=1)

    p = docdir.makepyfile("""\
        >>> for char in ['A', 'B', 'C', 'D', 'E']:
        ...     print(char, float(ord(char)))
        A 65.0
        ...
        E 70.0
    """)
    docdir.test(p, failed=1)


def test_allow_bytes_unicode(docdir):
    # These are dummy tests just to check tht doctest-plus can parse the
    # ALLOW_BYTES and ALLOW_UNICODE options. It doesn't actually implement
    # these options.
    p = docdir.makepyfile("""\
        >>> 1 # doctest: +ALLOW_BYTES
        1
        >>> 1 # doctest: +ALLOW_UNICODE
        1
    """)
    docdir.test(p, passed=1)


def test_requires(docdir):
    # should be ignored
    p = docdir.makerstfile("""\
        .. doctest-requires:: foobar
            >>> import foobar
    """)
    docdir.test(p, "--doctest-rst", passed=1)

    # should run as expected
    p = docdir.makerstfile("""\
        .. doctest-requires:: sys
            >>> import sys
    """)
    docdir.test(p, "--doctest-rst", passed=1)

    # testing this in case if doctest-requires just ignores everything
    # and pass unconditionally
    p = docdir.makerstfile("""\
        .. doctest-requires:: sys glob, re,math
            >>> import sys
            >>> assert 0
    """)
    docdir.test(p, "--doctest-rst", failed=1)

    # package with version is available
    p = docdir.makerstfile("""\
        .. doctest-requires:: sys pytest>=1.0
            >>> import sys, pytest
    """)
    docdir.test(p, "--doctest-rst", passed=1)

    # package with version is not available
    p = docdir.makerstfile("""\
        .. doctest-requires:: sys pytest<1.0 glob
            >>> import sys, pytest, glob
            >>> assert 0
    """)
    # passed because 'pytest<1.0' was not satisfied and 'assert 0' was not evaluated
    docdir.test(p, "--doctest-rst", passed=1)


def test_ignore_warnings_module(docdir):
    # First check that we get a warning if we don't add the IGNORE_WARNINGS
    # directive
    p = docdir.makepyfile("""\
        >>> import warnings
        >>> warnings.warn('A warning occurred', UserWarning)
    """)
    docdir.test(p, "-W error", failed=1)

    # Now try with the IGNORE_WARNINGS directive
    p = docdir.makepyfile("""\
        >>> import warnings
        >>> warnings.warn(  # doctest: +IGNORE_WARNINGS
        ...   'A warning occurred', UserWarning
        ... )
    """)
    docdir.test(p, "-W error", passed=1)


def test_ignore_warnings_rst(docdir):
    # First check that we get a warning if we don't add the IGNORE_WARNINGS
    # directive
    p = docdir.makerstfile("""\
        >>> import warnings
        >>> warnings.warn('A warning occurred', UserWarning)
    """)
    docdir.test(p, "--doctest-rst", "--text-file-format=rst", "-W error", failed=1)

    # Now try with the IGNORE_WARNINGS directive
    p = docdir.makerstfile("""\
        >>> import warnings
        >>> warnings.warn(
        ...   'A warning occurred', UserWarning
        ... )  # doctest: +IGNORE_WARNINGS
    """)
    docdir.test(p, "--doctest-rst", "--text-file-format=rst", "-W error", passed=1)


def test_doctest_glob(testdir, docdir):
    docdir.makerstfile(
        """
        >>> 1 + 1
        2
        """,
        filename="foo_1",
    )
    docdir.makerstfile(
        """
        >>> 1 + 1
        2
        """,
        filename="foo_2",
    )
    docdir.makefile(
        ".txt",
        """
        >>> 1 + 1
        2
        """,
        filename="foo_3",
    )
    docdir.makerstfile(
        """
        >>> 1 + 1
        2
        """,
        filename="bar_2",
    )

    testdir.inline_run().assertoutcome(passed=0)
    docdir.test(passed=0)
    docdir.test("--doctest-rst", passed=3)
    docdir.test("--doctest-rst", "--text-file-format", "txt", passed=1)
    docdir.test("--doctest-glob", "*.rst", passed=3)
    docdir.test("--doctest-glob", "*.rst", "--doctest-glob", "*.txt", passed=4)
    docdir.test("--doctest-glob", "foo_*.rst", passed=2)
    docdir.test("--doctest-glob", "foo_*.txt", passed=1)


def test_text_file_comments(docdir):
    docdir.makefile(".rst", ".. >>> 1 + 1\n3")
    docdir.makefile(".tex", "% >>> 1 + 1\n3")
    docdir.makefile(".txt", "# >>> 1 + 1\n3")

    docdir.test(
        "--doctest-glob",
        "*.rst",
        "--doctest-glob",
        "*.tex",
        "--doctest-glob",
        "*.txt",
        passed=3,
    )


def test_text_file_comment_chars(testdir, docdir):
    # override default comment chars
    testdir.makeini("""\
        [pytest]
        text_file_extensions =
            .rst=#
            .tex=#
    """)
    docdir.makefile(".rst", "# >>> 1 + 1\n3")
    docdir.makefile(".tex", "# >>> 1 + 1\n3")
    docdir.test("--doctest-glob", "*.rst", "--doctest-glob", "*.tex", passed=2)


def test_ignore_option(docdir):
    docdir.makepyfile(
        """
        >>> 1+1
        2
        """,
        filname="foo",
    )
    docdir.makepyfile(
        """
        >>> 1+1
        2
        """,
        filename="bar",
    )
    docdir.makerstfile(
        """
        >>> 1+1
        2""",
        filename="foo",
    )

    docdir.test(passed=2)
    docdir.test("--doctest-rst", passed=3)
    docdir.test("--doctest-rst", "--ignore", ".", passed=0)
    docdir.test("--doctest-rst", "--ignore", "bar.py", passed=2)


if LooseVersion("4.3.0") <= LooseVersion(pytest.__version__):
    def test_ignore_glob_option(docdir):
        docdir.makepyfile(
            """
            >>> 1+1
            2
            """,
            filename="foo",
        )
        docdir.makepyfile(
            """
            >>> 1+1
            2
            """,
            filename="bar",
        )
        docdir.makerstfile(
            """
            >>> 1+1
            2""",
            filename="foo",
        )

        docdir.test("--doctest-rst", "--ignore-glob", "foo*", passed=1)
        docdir.test("--doctest-rst", "--ignore-glob", "bar*", passed=2)
        docdir.test("--doctest-rst", "--ignore-glob", "*.rst", passed=2)


def test_doctest_only(testdir, docdir):
    # regular python files with doctests
    docdir.makepyfile(">>> 1 + 1\n2")
    docdir.makepyfile(">>> 1 + 1\n3")
    # regular test files
    testdir.makepyfile(test_foo="def test_foo(): pass")
    testdir.makepyfile(test_bar="def test_bar(): pass")
    # rst files
    docdir.makerstfile(">>> 1 + 1\n2")
    docdir.makerstfile(">>> 1 + 1\n3")
    docdir.makerstfile(">>> 1 + 2\n3")

    # regular tests
    testdir.inline_run().assertoutcome(passed=2)
    # regular + doctests
    docdir.test(passed=3, failed=1)
    # regular + doctests + doctest in rst files
    docdir.test("--doctest-rst", passed=5, failed=2)
    # only doctests in python files, implicit usage of doctest-plus
    docdir.test("--doctest-only", passed=1, failed=1)
    # only doctests in python files
    docdir.test("--doctest-only", "--doctest-rst", passed=3, failed=2)


def test_doctest_float_replacement(tmpdir):
    test1 = dedent("""
        This will demonstrate a doctest that fails due to a few extra decimal
        places::

            >>> 1.0 / 3.0
            0.333333333333333311
    """)

    test2 = dedent("""
        This is the same test, but it should pass with use of
        +FLOAT_CMP::

            >>> 1.0 / 3.0  # doctest: +FLOAT_CMP
            0.333333333333333311
    """)

    test1_rst = tmpdir.join('test1.rst')
    test2_rst = tmpdir.join('test2.rst')
    test1_rst.write(test1)
    test2_rst.write(test2)

    with pytest.raises(doctest.DocTestFailure):
        doctest.testfile(str(test1_rst), module_relative=False,
                         raise_on_error=True, verbose=False, encoding='utf-8')

    doctest.testfile(str(test2_rst), module_relative=False,
                     raise_on_error=True, verbose=False, encoding='utf-8')
