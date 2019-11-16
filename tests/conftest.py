import textwrap
from uuid import uuid4

import pytest


pytest_plugins = ["pytester"]


def rand_id():
    return str(uuid4()).replace("-", "_")


class DoctestFileMaker:
    def __init__(self, testdir):
        self.testdir = testdir

    def makefile(self, ext, *args, **kwargs):
        """
        Similar to `TestDir::makefile` but:

        - only one file will be generated
        - values of args, kwargs are treated as docstring and will be placed into
            generated functions if needed

        Parameters
        ----------
        ext : str
            extension of the file
        filename : str or None
            name of the generated file, will be popped out of kwargs
            (because py2 doesn't support `func(*a, f=1, **kw)` syntax)
        args : list of str
            list of docstrings
        kwargs: dict of str
            dictionary where each key is the name of the function and value is
            docstring of that function
        Returns
        -------

        """
        filename = kwargs.pop("filename", None)
        if not filename:
            filename = "script_{}".format(rand_id())

        # add default function name for each provided docstring
        for docstring in args:
            func_name = "func_{}".format(rand_id())
            kwargs[func_name] = docstring

        # join lines if docstring is iterable
        for func_name, docstring in kwargs.items():
            if isinstance(docstring, (tuple, list)):
                kwargs[func_name] = "\n".join(docstring)

        # generate content based on file extension
        if ext == ".py":
            chunks = ["from __future__ import print_function"]
        else:
            chunks = []
        for func_name, docstring in kwargs.items():
            if ext == ".py":
                chunk = self._make_func_with_doctest(func_name, docstring)
            else:
                chunk = docstring
            chunks.append(chunk)
        content = "\n".join(chunks)

        # make file in temp dir
        return self.testdir.makefile(ext, **{filename: content})

    def makepyfile(self, *args, **kwargs):
        return self.makefile(".py", *args, **kwargs)

    def makerstfile(self, *args, **kwargs):
        return self.makefile(".rst", *args, **kwargs)

    def _make_func_with_doctest(self, func_name, docstring):
        template = textwrap.dedent(
            r"""
            def {}():
                r'''
            {}
                '''
        """
        )
        return template.format(func_name, docstring)

    def test(self, *options, **kwargs):
        """
        Shortcut for testdir.inline_run(...).assertoutcome(...)
        with "--doctest-plus" always in the list of arguments.
        """
        out = self.testdir.inline_run("--doctest-plus", *options)
        out.assertoutcome(**kwargs)
        return out


@pytest.fixture
def docdir(testdir):
    return DoctestFileMaker(testdir)
