import glob
import os
from platform import python_version
from textwrap import dedent
import sys

from packaging.version import Version

import pytest

import doctest
from pytest_doctestplus.output_checker import OutputChecker, FLOAT_CMP

try:
    import pytest_asyncio  # noqa: F401
    has_pytest_asyncio = True
except ImportError:
    has_pytest_asyncio = False



pytest_plugins = ['pytester']


PYTEST_LT_6 = Version(pytest.__version__) < Version('6.0.0')


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


def test_float_cmp_dict(testdir):
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
            >>> x = {'a': 1/3., 'b': 2/3.}
            >>> x    # doctest: +FLOAT_CMP
            {'a': 0.333333, 'b': 0.666666}
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
    # These are dummy tests just to check that doctest-plus can parse the
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
            got.append(f'{char} {float(ord(char))}')
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


def test_requires_all(testdir):
    testdir.makeini(
        """
        [pytest]
        doctestplus = enabled
    """)

    # should be ignored
    p = testdir.makefile(
        '.rst',
        """
        .. doctest-requires-all:: foobar

            >>> import foobar

        This is a narrative line, before another doctest snippet

           >>> import foobar
        """
    )
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


@pytest.mark.xfail(reason='known issue, fenced code blocks require an extra trailing newline')
def test_markdown_fenced_code(testdir):
    testdir.makefile('.md', foo="""\
```
>>> 1 + 1
2
```
""")
    testdir.inline_run(
        '--doctest-plus', '--doctest-glob', '*.md'
    ).assertoutcome(passed=1)


def test_markdown_fenced_code_with_extra_newline(testdir):
    testdir.makefile('.md', foo="""\
```
>>> 1 + 1
2

```
""")
    testdir.inline_run(
        '--doctest-plus', '--doctest-glob', '*.md'
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


def test_doctest_float_replacement(tmp_path):
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

    test1_rst = tmp_path / "test1.rst"
    test2_rst = tmp_path / "test2.rst"
    test1_rst.write_text(test1)
    test2_rst.write_text(test2)

    with pytest.raises(doctest.DocTestFailure):
        doctest.testfile(
            test1_rst,
            module_relative=False,
            raise_on_error=True,
            verbose=False,
            encoding="utf-8",
        )

    doctest.testfile(
        test2_rst,
        module_relative=False,
        raise_on_error=True,
        verbose=False,
        encoding="utf-8",
    )


# Note that each entry under doctest_subpackage_requires has different whitespace
# around the = to make sure that all cases work properly.
SUBPACKAGE_REQUIRES_INI = (
    "makeini",
    """
    [pytest]
    doctest_subpackage_requires =
        test/a/* = pytest>1
        test/b/*= pytest>1;averyfakepackage>99999.9
        test/c/*=anotherfakepackage>=22000.1.2
    """
)
SUBPACKAGE_REQUIRES_PYPROJECT = (
    "makepyprojecttoml",
    """
    [tool.pytest.ini_options]
    doctest_subpackage_requires = [
        "test/a/* = pytest>1",
        "test/b/*= pytest>1;averyfakepackage>99999.9",
        "test/c/*=anotherfakepackage>=22000.1.2",
    ]
    """
)


@pytest.fixture()
def subpackage_requires_testdir(testdir, request):
    if request.param[0] == 'makepyprojecttoml' and PYTEST_LT_6:
        return None, None

    config_file = getattr(testdir, request.param[0])(request.param[1])

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

    return config_file, testdir


@pytest.mark.parametrize('subpackage_requires_testdir', [SUBPACKAGE_REQUIRES_INI, SUBPACKAGE_REQUIRES_PYPROJECT], indirect=True)
def test_doctest_subpackage_requires(subpackage_requires_testdir, caplog):
    config_file, testdir = subpackage_requires_testdir
    if config_file is None:
        pytest.skip("pyproject.toml not supported in pytest<6")

    reprec = testdir.inline_run(str(testdir), f"-c={config_file}", "--doctest-plus")
    reprec.assertoutcome(passed=1)
    assert reprec.listoutcomes()[0][0].location[0] == os.path.join('test', 'a', 'testcode.py')
    assert caplog.text == ''


@pytest.mark.parametrize(('import_mode', 'expected'), [
    pytest.param('importlib', dict(passed=2), marks=pytest.mark.skipif(PYTEST_LT_6, reason="importlib import mode not supported on Pytest <6"), id="importlib"),
    pytest.param('append', dict(failed=1), id="append"),
    pytest.param('prepend', dict(failed=1), id="prepend"),
])
def test_import_mode(testdir, import_mode, expected):
    """Test that two files with the same name but in different folders work with --import-mode=importlib."""
    a = testdir.mkdir('a')
    b = testdir.mkdir('b')

    pyfile = dedent("""
        def f():
            '''
            >>> 1
            1
            '''
    """)

    a.join('testcode.py').write(pyfile)
    b.join('testcode.py').write(pyfile)

    reprec = testdir.inline_run(str(testdir), "--doctest-plus", f"--import-mode={import_mode}")
    reprec.assertoutcome(**expected)


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


def test_remote_data_all(testdir):
    testdir.makeini(
        """
        [pytest]
        doctestplus = enabled
    """)

    p = testdir.makefile(
        '.rst',
        """
        This is a narrative docs, which some of the lines requiring remote-data access.
        The first code block always passes, the second is skipped without remote data and the
        last section is skipped due to the all option.

            >>> print("Test")
            Test

        .. doctest-remote-data-all::

            >>> from contextlib import closing
            >>> from urllib.request import urlopen
            >>> with closing(urlopen('https://www.astropy.org')) as remote:
            ...     remote.read()    # doctest: +IGNORE_OUTPUT

        Narrative before a codeblock that should fail normally but with the all option in the
        directive it is skipped over thus producing a passing status.

            >>> print(123)
        """
    )

    testdir.inline_run(p, '--doctest-plus', '--doctest-rst', '--remote-data').assertoutcome(failed=1)
    testdir.inline_run(p, '--doctest-plus', '--doctest-rst').assertoutcome(passed=1)


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


def test_skiptest(testdir):
    testdir.makeini(
        """
        [pytest]
        doctestplus = enabled
    """
    )
    p = testdir.makepyfile(
        """
        class MyClass:
            '''
            >>> import pytest
            >>> pytest.skip("I changed my mind")
            >>> assert False, "This should not be reached"
            '''
            pass
    """
    )
    reprec = testdir.inline_run(p, "--doctest-plus")
    reprec.assertoutcome(skipped=1, failed=0)


@pytest.mark.parametrize('cont_on_fail', [False, True])
def test_fail_two_tests(testdir, cont_on_fail):
    p = testdir.makepyfile(
        """
        class MyClass:
            '''
            .. doctest::

                >>> print(2)
                1

            .. doctest::

                >>> print(3)
                1
            '''
            pass
    """
    )
    arg = ("--doctest-continue-on-failure",) if cont_on_fail else ()
    reprec = testdir.inline_run(p, "--doctest-plus", *arg)
    reprec.assertoutcome(skipped=0, failed=1)
    _, _, failed = reprec.listoutcomes()
    report = failed[0]
    assert "Expected:\n    1\nGot:\n    2" in report.longreprtext
    assert ("Expected:\n    1\nGot:\n    3" in report.longreprtext) is cont_on_fail


@pytest.mark.parametrize('cont_on_fail', [False, True])
def test_fail_data_dependency(testdir, cont_on_fail):
    p = testdir.makepyfile(
        """
        class MyClass:
            '''
            .. doctest::

                >>> import nonexistentmodule as nem
                >>> a = nem.calculate_something()
            '''
            pass
    """
    )
    arg = ("--doctest-continue-on-failure",) if cont_on_fail else ()
    reprec = testdir.inline_run(p, "--doctest-plus", *arg)
    reprec.assertoutcome(skipped=0, failed=1)
    _, _, failed = reprec.listoutcomes()
    # Both lines fail in a single error
    report = failed[0]
    assert " as nem\nUNEXPECTED EXCEPTION: ModuleNotFoundError" in report.longreprtext
    assert ("something()\nUNEXPECTED EXCEPTION: NameError" in report.longreprtext) is cont_on_fail


@pytest.mark.xfail(
        has_pytest_asyncio,
        reason='pytest_asyncio monkey-patches .collect()')
def test_main(testdir):
    pkg = testdir.mkdir('pkg')
    code = dedent(
        '''
        def f():
            raise RuntimeError("This is a CLI, do not execute module while doctesting")

        f()
        '''
    )
    pkg.join('__init__.py').write_text("", "utf-8")
    main_path = pkg.join('__main__.py')
    main_path.write_text(code, "utf-8")

    testdir.inline_run(pkg).assertoutcome(passed=0)
    testdir.inline_run(pkg, '--doctest-plus').assertoutcome(passed=0)


@pytest.mark.xfail(
        python_version() in ('3.11.9', '3.11.10', '3.11.11', '3.12.3'),
        reason='broken by https://github.com/python/cpython/pull/115440')
def test_ufunc(testdir):
    pytest.importorskip('numpy')

    # Create and build example module
    testdir.makepyfile(module1="""
        def foo():
            '''A doctest...

            >>> foo()
            1
            '''
            return 1
        """)
    testdir.makepyfile(module2="""
        import functools
        from _module2 import foo, bar, bat as _bat


        def wrap_func(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper


        bat = wrap_func(_bat)
        """)
    testdir.makepyfile(setup="""
        from setuptools import setup, Extension
        import numpy as np

        ext = Extension('_module2', ['_module2.c'],
                        extra_compile_args=['-std=c99'],
                        include_dirs=[np.get_include()])
        setup(name='example', py_modules=['module1', 'module2'], ext_modules=[ext])
        """)
    testdir.makefile('.c', _module2=r"""
        #define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

        #include <numpy/arrayobject.h>
        #include <numpy/ufuncobject.h>
        #include <Python.h>


        static double ufunc_inner(double a, double b)
        {
            return a + b;
        }


        static void ufunc_loop(
            char **args,
            const npy_intp *dimensions,
            const npy_intp *steps,
            void *NPY_UNUSED(data)
        ) {
            const npy_intp n = dimensions[0];
            for (npy_intp i = 0; i < n; i ++)
            {
                *(double *) &args[2][i * steps[2]] = ufunc_inner(
                *(double *) &args[0][i * steps[0]],
                *(double *) &args[1][i * steps[1]]);
            }
        }


        static PyUFuncGenericFunction ufunc_loops[] = {ufunc_loop};
        static char ufunc_types[] = {NPY_DOUBLE, NPY_DOUBLE, NPY_DOUBLE};
        static void *ufunc_data[] = {NULL};
        static const char ufunc_docstring[] = ">>> foo(1, 2)\n3.0";

        static PyModuleDef moduledef = {
            .m_base = PyModuleDef_HEAD_INIT,
            .m_name = "_module2",
            .m_size = -1
        };


        PyMODINIT_FUNC PyInit__module2(void)
        {
            import_array();
            import_ufunc();

            PyObject *module = PyModule_Create(&moduledef);
            if (!module)
                return NULL;

            /* Add a ufunc _with_ a docstring. */
            PyObject *foo = PyUFunc_FromFuncAndData(
                ufunc_loops, ufunc_data, ufunc_types, 1, 2, 1, PyUFunc_None,
                "foo", ufunc_docstring, 0);
            if (!foo)
            {
                Py_DECREF(module);
                return NULL;
            }
            if (PyModule_AddObject(module, "foo", foo) < 0)
            {
                Py_DECREF(foo);
                Py_DECREF(module);
                return NULL;
            }

            /* Add a ufunc _without_ a docstring. */
            PyObject *bar = PyUFunc_FromFuncAndData(
                ufunc_loops, ufunc_data, ufunc_types, 1, 2, 1, PyUFunc_None,
                "bar", NULL, 0);
            if (!bar)
            {
                Py_DECREF(module);
                return NULL;
            }
            if (PyModule_AddObject(module, "bar", bar) < 0)
            {
                Py_DECREF(bar);
                Py_DECREF(module);
                return NULL;
            }

            /* Add another ufunc _without_ a docstring. */
            PyObject *bat = PyUFunc_FromFuncAndData(
                ufunc_loops, ufunc_data, ufunc_types, 1, 2, 1, PyUFunc_None,
                "bat", NULL, 0);
            if (!bat)
            {
                Py_DECREF(module);
                return NULL;
            }
            if (PyModule_AddObject(module, "bat", bat) < 0)
            {
                Py_DECREF(bat);
                Py_DECREF(module);
                return NULL;
            }

            return module;
        }
        """)
    testdir.run(sys.executable, 'setup.py', 'build')
    build_dir, = glob.glob(str(testdir.tmpdir / 'build/lib.*'))

    result = testdir.inline_run(build_dir, '--doctest-plus', '--doctest-modules')
    result.assertoutcome(passed=1, failed=0)

    result = testdir.inline_run(build_dir, '--doctest-plus', '--doctest-modules', '--doctest-ufunc')
    result.assertoutcome(passed=2, failed=0)


NORCURSEDIRS_INI = (
    "makeini",
    """
    [pytest]
    doctest_norecursedirs =
        "bad_dir"
        "*/bad_file.py"
    """
)
NORCURSEDIRS_PYPROJECT = (
    "makepyprojecttoml",
    """
    [tool.pytest.ini_options]
    doctest_norecursedirs = [
        "bad_dir",
        "*/bad_file.py",
    ]
    """
)


@pytest.fixture()
def norecursedirs_testdir(testdir, request):
    if request.param[0] == 'makepyprojecttoml' and PYTEST_LT_6:
        return None, None

    config_file = getattr(testdir, request.param[0])(request.param[1])

    bad_text = dedent("""
        def f():
            '''
            This should fail doc testing
            >>> 1
            2
            '''
            pass
    """)

    good_text = dedent("""
        def g():
            '''
            This should pass doc testing
            >>> 1
            1
            '''
            pass
    """)

    # Create a bad file that should be by its folder
    bad_subdir = testdir.mkdir("bad_dir")
    bad_file = bad_subdir.join("test_foobar.py")
    bad_file.write_text(bad_text, "utf-8")

    # Create a bad file that should be skipped by its name
    okay_subdir1 = testdir.mkdir("okay_foo_dir")
    bad_file = okay_subdir1.join("bad_file.py")
    bad_file.write_text(bad_text, "utf-8")
    # Create a good file in that directory that doctest won't skip
    good_file1 = okay_subdir1.join("good_file1.py")
    good_file1.write_text(good_text, "utf-8")

    # Create another bad file that should be skipped by its name
    okay_subdir2 = testdir.mkdir("okay_bar_dir")
    bad_file = okay_subdir2.join("bad_file.py")
    bad_file.write_text(bad_text, "utf-8")
    # Create a good file in that directory that doctest won't skip
    good_file2 = okay_subdir2.join("good_file2.py")
    good_file2.write_text(good_text, "utf-8")

    return config_file, testdir


@pytest.mark.parametrize('norecursedirs_testdir', [NORCURSEDIRS_INI, NORCURSEDIRS_PYPROJECT], indirect=True)
def test_doctest_norecursedirs(norecursedirs_testdir):
    config_file, testdir = norecursedirs_testdir
    if config_file is None:
        pytest.skip("pyproject.toml not supported in pytest<6")

    reprec = testdir.inline_run(str(testdir), f"-c={config_file}", "--doctest-plus")
    reprec.assertoutcome(passed=2)


def test_norecursedirs(testdir):
    testdir.makeini(
        """
        [pytest]
        norecursedirs = \"bad_dir\"
        doctestplus = enabled
    """
    )
    subdir = testdir.mkdir("bad_dir")
    badfile = subdir.join("test_foobar.py")
    badfile.write_text("""
        def f():
            '''
            >>> x = 1/3.
            >>> x
            0.333333
            '''
            fail
    """, "utf-8")
    reprec = testdir.inline_run(str(testdir), "--doctest-plus")
    reprec.assertoutcome(failed=0, passed=0)


def test_generate_diff_basic(testdir, capsys):
    p = testdir.makepyfile("""
        def f():
            '''
            >>> print(2)
            4
            >>> print(3)
            5
            '''
            pass
        """)
    with open(p) as f:
        original = f.read()

    testdir.inline_run(p, "--doctest-plus-generate-diff")
    diff = dedent("""
         >>> print(2)
    -    4
    +    2
         >>> print(3)
    -    5
    +    3
    """)
    captured = capsys.readouterr()
    assert diff in captured.out

    testdir.inline_run(p, "--doctest-plus-generate-diff=overwrite")
    captured = capsys.readouterr()
    assert "Applied fix to the following files" in captured.out

    with open(p) as f:
        result = f.read()

    assert result == original.replace("4", "2").replace("5", "3")


def test_generate_diff_multiline(testdir, capsys):
    p = testdir.makepyfile("""
        def f():
            '''
            >>> print(2)
            2
            >>> for i in range(4):
            ...     print(i)
            1
            2
            '''
            pass
        """)
    with open(p) as f:
        original = f.read()

    testdir.inline_run(p, "--doctest-plus-generate-diff")
    diff = dedent("""
         >>> for i in range(4):
         ...     print(i)
    +    0
         1
         2
    +    3
    """)
    captured = capsys.readouterr()
    assert diff in captured.out

    testdir.inline_run(p, "--doctest-plus-generate-diff=overwrite")
    captured = capsys.readouterr()
    assert "Applied fix to the following files" in captured.out

    with open(p) as f:
        result = f.read()

    original_fixed = original.replace("1\n    2", "\n    ".join(["0", "1", "2", "3"]))
    assert result == original_fixed
