import os
from distutils.version import LooseVersion
from textwrap import dedent

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
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst').assertoutcome(skipped=1)

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
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst').assertoutcome(skipped=1)


def test_ignore_warnings_module(testdir):

    # First check that we get a warning if we don't add the IGNORE_WARNINGS
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

    # Now try with the IGNORE_WARNINGS directive
    p = testdir.makepyfile(
        """
        def myfunc():
            '''
            >>> import warnings
            >>> warnings.warn('A warning occurred', UserWarning)  # doctest: +IGNORE_WARNINGS
            '''
            pass
        """)
    reprec = testdir.inline_run(p, "--doctest-plus", "-W error")
    reprec.assertoutcome(failed=0, passed=1)


def test_ignore_warnings_rst(testdir):

    # First check that we get a warning if we don't add the IGNORE_WARNINGS
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

    # Now try with the IGNORE_WARNINGS directive
    p = testdir.makefile(".rst",
                         """
        ::
            >>> import warnings
            >>> warnings.warn('A warning occurred', UserWarning)  # doctest: +IGNORE_WARNINGS
        """)
    reprec = testdir.inline_run(p, "--doctest-plus", "--doctest-rst",
                                "--text-file-format=rst", "-W error")
    reprec.assertoutcome(failed=0, passed=1)


def test_show_warnings_module(testdir):

    p = testdir.makepyfile(
        """
        def myfunc():
            '''
            >>> import warnings
            >>> warnings.warn('A warning occurred', UserWarning)  # doctest: +SHOW_WARNINGS
            UserWarning: A warning occurred
            '''
            pass
        """)
    reprec = testdir.inline_run(p, "--doctest-plus", "-W error")
    reprec.assertoutcome(failed=0, passed=1)

    # Make sure it fails if warning message is missing
    p = testdir.makepyfile(
        """
        def myfunc():
            '''
            >>> import warnings
            >>> warnings.warn('A warning occurred', UserWarning)  # doctest: +SHOW_WARNINGS
            '''
            pass
        """)
    reprec = testdir.inline_run(p, "--doctest-plus", "-W error")
    reprec.assertoutcome(failed=1, passed=0)


def test_show_warnings_rst(testdir):

    p = testdir.makefile(".rst",
                         """
        ::
            >>> import warnings
            >>> warnings.warn('A warning occurred', UserWarning)  # doctest: +SHOW_WARNINGS
            UserWarning: A warning occurred
        """)
    reprec = testdir.inline_run(p, "--doctest-plus", "--doctest-rst",
                                "--text-file-format=rst", "-W error")
    reprec.assertoutcome(failed=0, passed=1)

    # Make sure it fails if warning message is missing
    p = testdir.makefile(".rst",
                         """
        ::
            >>> import warnings
            >>> warnings.warn('A warning occurred', UserWarning)  # doctest: +SHOW_WARNINGS
        """)
    reprec = testdir.inline_run(p, "--doctest-plus", "--doctest-rst",
                                "--text-file-format=rst", "-W error")
    reprec.assertoutcome(failed=1, passed=0)

    # Make sure it fails if warning message is missing
    p = testdir.makefile(".rst",
                         """
        ::
            >>> import warnings
            >>> warnings.warn('A warning occurred', UserWarning)  # doctest: +SHOW_WARNINGS
            Warning: Another warning occurred
        """)
    reprec = testdir.inline_run(p, "--doctest-plus", "--doctest-rst",
                                "--text-file-format=rst", "-W error")
    reprec.assertoutcome(failed=1, passed=0)


def test_doctest_glob(testdir):
    testdir.makefile(
        '.md',
        foo_1=">>> 1 + 1\n2",
    )
    testdir.makefile(
        '.rst',
        foo_2=">>> 1 + 1\n2",
    )
    testdir.makefile(
        '.rst',
        foo_3=">>> 1 + 1\n2",
    )
    testdir.makefile(
        '.txt',
        foo_4=">>> 1 + 1\n2",
    )
    testdir.makefile(
        '.rst',
        bar_2=">>> 1 + 1\n2",
    )

    testdir.inline_run().assertoutcome(passed=0)
    testdir.inline_run('--doctest-plus').assertoutcome(passed=0)
    testdir.inline_run('--doctest-plus', '--doctest-rst').assertoutcome(passed=3)
    testdir.inline_run(
        '--doctest-plus', '--doctest-rst', '--text-file-format', 'txt'
    ).assertoutcome(passed=1)
    testdir.inline_run(
        '--doctest-plus', '--doctest-glob', '*.rst'
    ).assertoutcome(passed=3)
    testdir.inline_run(
        '--doctest-plus', '--doctest-glob', '*.rst', '--doctest-glob', '*.txt'
    ).assertoutcome(passed=4)
    testdir.inline_run(
        '--doctest-plus', '--doctest-glob', '*.rst', '--doctest-glob', '*.txt',
        '--doctest-glob', '*.md'
    ).assertoutcome(passed=5)
    testdir.inline_run(
        '--doctest-plus', '--doctest-glob', 'foo_*.rst'
    ).assertoutcome(passed=2)
    testdir.inline_run(
        '--doctest-plus', '--doctest-glob', 'foo_*.md'
    ).assertoutcome(passed=1)
    testdir.inline_run(
        '--doctest-plus', '--doctest-glob', 'foo_*.txt'
    ).assertoutcome(passed=1)


def test_text_file_comments(testdir):
    testdir.makefile(
        '.md',
        foo_1="<!-- >>> 1 + 1 -->\n3",
    )
    testdir.makefile(
        '.rst',
        foo_2=".. >>> 1 + 1\n3",
    )
    testdir.makefile(
        '.tex',
        foo_3="% >>> 1 + 1\n3",
    )
    testdir.makefile(
        '.txt',
        foo_4="# >>> 1 + 1\n3",
    )

    testdir.inline_run(
        '--doctest-plus',
        '--doctest-glob', '*.md',
        '--doctest-glob', '*.rst',
        '--doctest-glob', '*.tex',
        '--doctest-glob', '*.txt'
    ).assertoutcome(passed=0)


def test_text_file_comment_chars(testdir):
    # override default comment chars
    testdir.makeini(
        """
        [pytest]
        text_file_extensions =
            .rst=#
            .tex=#
    """
    )
    testdir.makefile(
        '.rst',
        foo_1="# >>> 1 + 1\n3",
    )
    testdir.makefile(
        '.tex',
        foo_2="# >>> 1 + 1\n3",
    )
    testdir.inline_run(
        '--doctest-plus',
        '--doctest-glob', '*.rst',
        '--doctest-glob', '*.tex',
        '--doctest-glob', '*.txt'
    ).assertoutcome(passed=0)


def test_ignore_option(testdir):
    testdir.makepyfile(foo="""
        def f():
            '''
            >>> 1+1
            2
            '''
            pass
    """)
    testdir.makepyfile(bar="""
        def f():
            '''
            >>> 1+1
            2
            '''
            pass
    """)
    testdir.makefile('.rst', foo='>>> 1+1\n2')

    testdir.inline_run('--doctest-plus').assertoutcome(passed=2)
    testdir.inline_run('--doctest-plus', '--doctest-rst').assertoutcome(passed=3)
    testdir.inline_run(
        '--doctest-plus', '--doctest-rst', '--ignore', '.'
    ).assertoutcome(passed=0)
    testdir.inline_run(
        '--doctest-plus', '--doctest-rst', '--ignore', 'bar.py'
    ).assertoutcome(passed=2)


if LooseVersion('4.3.0') <= LooseVersion(pytest.__version__):
    def test_ignore_glob_option(testdir):
        testdir.makepyfile(foo="""
            def f():
                '''
                >>> 1+1
                2
                '''
                pass
        """)
        testdir.makepyfile(bar="""
            def f():
                '''
                >>> 1+1
                2
                '''
                pass
        """)
        testdir.makefile('.rst', foo='>>> 1+1\n2')

        testdir.inline_run(
            '--doctest-plus', '--doctest-rst', '--ignore-glob', 'foo*'
        ).assertoutcome(passed=1)
        testdir.inline_run(
            '--doctest-plus', '--doctest-rst', '--ignore-glob', 'bar*'
        ).assertoutcome(passed=2)
        testdir.inline_run(
            '--doctest-plus', '--doctest-rst', '--ignore-glob', '*.rst'
        ).assertoutcome(passed=2)


def test_doctest_only(testdir, makepyfile, maketestfile, makerstfile):
    # regular python files with doctests
    makepyfile(p1='>>> 1 + 1\n2')
    makepyfile(p2='>>> 1 + 1\n3')
    # regular test files
    maketestfile(test_1='foo')
    maketestfile(test_2='bar')
    # rst files
    makerstfile(r1='>>> 1 + 1\n2')
    makerstfile(r3='>>> 1 + 1\n3')
    makerstfile(r2='>>> 1 + 2\n3')

    # regular tests
    testdir.inline_run().assertoutcome(passed=2)
    # regular + doctests
    testdir.inline_run("--doctest-plus").assertoutcome(passed=3, failed=1)
    # regular + doctests + doctest in rst files
    testdir.inline_run("--doctest-plus", "--doctest-rst").assertoutcome(passed=5, failed=2)
    # only doctests in python files, implicit usage of doctest-plus
    testdir.inline_run("--doctest-only").assertoutcome(passed=1, failed=1)
    # only doctests in python files
    testdir.inline_run("--doctest-only", "--doctest-rst").assertoutcome(passed=3, failed=2)


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


def test_doctest_subpackage_requires(testdir, caplog):

    # Note that each entry below has different whitespace around the = to
    # make sure that all cases work properly.

    testdir.makeini(
        """
        [pytest]
        doctest_subpackage_requires =
            test/a/* = pytest>1
            test/b/*= pytest>1;averyfakepackage>99999.9
            test/c/*=anotherfakepackage>=22000.1.2
    """
    )
    test = testdir.mkdir('test')
    a = test.mkdir('a')
    b = test.mkdir('b')
    c = test.mkdir('c')

    pyfile = dedent("""
        def f():
            '''
            >>> 1
            1
            '''
            pass
    """)

    a.join('testcode.py').write(pyfile)
    b.join('testcode.py').write(pyfile)
    c.join('testcode.py').write(pyfile)

    reprec = testdir.inline_run(test, "--doctest-plus")
    reprec.assertoutcome(passed=1)
    assert reprec.listoutcomes()[0][0].location[0] == os.path.join('test', 'a', 'testcode.py')
    assert caplog.text == ''


def test_doctest_skip(testdir):
    testdir.makeini(
        """
        [pytest]
        doctestplus = enabled
    """)

    p = testdir.makefile(
        '.rst',
        """
        .. doctest-skip::

            >>> import asdf
            >>> asdf.open('file.asdf')  # doctest: +IGNORE_WARNINGS
        """
    )
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst').assertoutcome(skipped=1)


# We repeat all testst including remote data with and without it opted in
def test_remote_data_url(testdir):
    testdir.makeini(
        """
        [pytest]
        doctestplus = enabled
    """)

    p = testdir.makefile(
        '.rst',
        """
        # This test should be skipped when remote data is not requested.
        .. doctest-remote-data::

            >>> from contextlib import closing
            >>> from urllib.request import urlopen
            >>> with closing(urlopen('https://www.astropy.org')) as remote:
            ...     remote.read()    # doctest: +IGNORE_OUTPUT
        """
    )
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst', '--remote-data').assertoutcome(passed=1)
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst').assertoutcome(skipped=1)


def test_remote_data_float_cmp(testdir):
    testdir.makeini(
        """
        [pytest]
        doctestplus = enabled
    """)

    p = testdir.makefile(
        '.rst',
        """
        #This test is skipped when remote data is not requested
        .. doctest-remote-data::

            >>> x = 1/3.
            >>> x    # doctest: +FLOAT_CMP
            0.333333
        """
    )
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst', '--remote-data').assertoutcome(passed=1)
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst').assertoutcome(skipped=1)


def test_remote_data_ignore_whitespace(testdir):
    testdir.makeini(
        """
        [pytest]
        doctest_optionflags = NORMALIZE_WHITESPACE
        doctestplus = enabled
    """)

    p = testdir.makefile(
        '.rst',
        """
        #This test should be skipped when remote data is not requested, and should
        #pass when remote data is requested
        .. doctest-remote-data::

            >>> a = "foo         "
            >>> print(a)
            foo
        """
    )
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst', '--remote-data').assertoutcome(passed=1)
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst').assertoutcome(skipped=1)


def test_remote_data_ellipsis(testdir):
    testdir.makeini(
        """
        [pytest]
        doctest_optionflags = ELLIPSIS
        doctestplus = enabled
    """)

    p = testdir.makefile(
        '.rst',
        """
        # This test should be skipped when remote data is not requested, and should
        # pass when remote data is requested
        .. doctest-remote-data::

            >>> a = "freedom at last"
            >>> print(a)
            freedom ...
        """
    )
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst', '--remote-data').assertoutcome(passed=1)
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst').assertoutcome(skipped=1)


def test_remote_data_requires(testdir):
    testdir.makeini(
        """
        [pytest]
        doctestplus = enabled
    """)

    p = testdir.makefile(
        '.rst',
        """
        # This test should be skipped when remote data is not requested.
        # It should also be skipped instead of failing when remote data is requested because
        # the module required does not exist
        .. doctest-remote-data::
        .. doctest-requires:: does-not-exist

            >>> 1 + 1
            3
        """
    )
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst', '--remote-data').assertoutcome(skipped=1)
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst').assertoutcome(skipped=1)


def test_remote_data_ignore_warnings(testdir):
    testdir.makeini(
        """
        [pytest]
        doctestplus = enabled
    """)

    p = testdir.makefile(
        '.rst',
        """
        # This test should be skipped if remote data is not requested.
        .. doctest-remote-data::

            >>> import warnings
            >>> warnings.warn('A warning occurred', UserWarning)  # doctest: +IGNORE_WARNINGS
        """
    )
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst', '--remote-data').assertoutcome(passed=1)
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst').assertoutcome(skipped=1)
