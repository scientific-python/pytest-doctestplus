from functools import partial
import textwrap

import pytest


def _wrap_docstring_in_func(func_name, docstring):
    template = textwrap.dedent(r"""
        def {}():
            r'''
        {}
            '''
    """)
    return template.format(func_name, docstring)


@pytest.fixture
def makepyfile(testdir):
    """Fixture for making python files with single function and docstring."""
    def make(*args, **kwargs):
        func_name = kwargs.pop('func_name', 'f')
        # content in args and kwargs is treated as docstring
        wrap = partial(_wrap_docstring_in_func, func_name)
        args = map(wrap, args)
        kwargs = dict(zip(kwargs.keys(), map(wrap, kwargs.values())))
        return testdir.makepyfile(*args, **kwargs)

    return make


@pytest.fixture
def maketestfile(makepyfile):
    """Fixture for making python test files with single function and docstring."""
    def make(*args, **kwargs):
        func_name = kwargs.pop('func_name', 'test_foo')
        return makepyfile(*args, func_name=func_name, **kwargs)

    return make


@pytest.fixture
def makerstfile(testdir):
    """Fixture for making rst files with specified content."""
    def make(*args, **kwargs):
        return testdir.makefile('.rst', *args, **kwargs)

    return make
