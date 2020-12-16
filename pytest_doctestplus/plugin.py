# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
This plugin provides advanced doctest support and enables the testing of .rst
files.
"""
import doctest
import fnmatch
import os
import re
import sys
import warnings
from pathlib import Path
from textwrap import indent

import pytest
from packaging.version import Version

from pytest_doctestplus.utils import ModuleChecker

from .output_checker import (FIX, IGNORE_WARNINGS, REMOTE_DATA, SHOW_WARNINGS,
                             OutputChecker)

_pytest_version = Version(pytest.__version__)
PYTEST_GT_5 = _pytest_version > Version('5.9.9')
PYTEST_GE_6_3 = _pytest_version.is_devrelease or _pytest_version >= Version('6.3')

comment_characters = {
    '.txt': '#',
    '.tex': '%',
    '.rst': r'\.\.'
}


# For the IGNORE_WARNINGS and SHOW_WARNINGS option, we create a context manager
# that doesn't require us to add any imports to the example list and contains
# everything that is needed to silence or print warnings.

IGNORE_WARNINGS_CONTEXT = """
class _doctestplus_ignore_all_warnings:

    def __init__(self):
        import warnings
        self._cw = warnings.catch_warnings()

    def __enter__(self, *args, **kwargs):
        result = self._cw.__enter__(*args, **kwargs)
        import warnings
        warnings.simplefilter('ignore')
        return result

    def __exit__(self, *args, **kwargs):
        return self._cw.__exit__(*args, **kwargs)
""".lstrip()


SHOW_WARNINGS_CONTEXT = """
class _doctestplus_show_all_warnings:

    def __init__(self):
        import warnings
        self._cw = warnings.catch_warnings(record=True)

    def __enter__(self, *args, **kwargs):
        self.result = self._cw.__enter__(*args, **kwargs)
        import warnings
        warnings.simplefilter('always')
        return self.result

    def __exit__(self, *args, **kwargs):
        self._cw.__exit__(*args, **kwargs)
        for warn in self.result:
            print(f'{warn._category_name}: {warn.message}')
""".lstrip()


# these pytest hooks allow us to mark tests and run the marked tests with
# specific command line options.
def pytest_addoption(parser):
    parser.addoption("--doctest-plus", action="store_true",
                     help="enable running doctests with additional "
                          "features not found in the normal doctest "
                          "plugin")

    parser.addoption("--doctest-rst", action="store_true",
                     help=(
                         "Enable running doctests in .rst documentation. "
                         "This is no longer recommended, use --doctest-glob instead."
                     ))

    parser.addoption("--text-file-format", action="store",
                     help=(
                        "Text file format for narrative documentation. "
                        "Options accepted are 'txt', 'tex', and 'rst'. "
                        "This is no longer recommended, use --doctest-glob instead."
                     ))

    # Defaults to `atol` parameter from `numpy.allclose`.
    parser.addoption("--doctest-plus-atol", action="store",
                     help="set the absolute tolerance for float comparison",
                     default=1e-08)

    # Defaults to `rtol` parameter from `numpy.allclose`.
    parser.addoption("--doctest-plus-rtol", action="store",
                     help="set the relative tolerance for float comparison",
                     default=1e-05)

    parser.addoption("--doctest-only", action="store_true",
                     help="Test only doctests. Implies usage of doctest-plus.")

    parser.addini("text_file_format",
                  "Default format for docs. "
                  "This is no longer recommended, use --doctest-glob instead.")

    parser.addini("doctest_optionflags", "option flags for doctests",
                  type="args", default=["ELLIPSIS", "NORMALIZE_WHITESPACE"],)

    parser.addini("doctest_plus", "enable running doctests with additional "
                                  "features not found in the normal doctest plugin")

    parser.addini("doctest_norecursedirs",
                  "like the norecursedirs option but applies only to doctest "
                  "collection", type="args", default=())

    parser.addini("doctest_rst",
                  "Run the doctests in the rst documentation",
                  default=False)

    parser.addini("doctest_plus_atol",
                  "set the absolute tolerance for float comparison",
                  default=1e-08)

    parser.addini("doctest_plus_rtol",
                  "set the relative tolerance for float comparison",
                  default=1e-05)

    parser.addini('text_file_comment_chars',
                  help='list of pairs in format file_extension=comment_chars, eg: .rst=..',
                  type='linelist',
                  default=[])

    parser.addini("doctest_subpackage_requires",
                  "A list of paths to skip if requirements are not satisfied. Each item in the list "
                  "should have the syntax path=req1;req2",
                  type='linelist',
                  default=[])


def get_optionflags(parent):
    optionflags_str = parent.config.getini('doctest_optionflags')
    flag_int = 0
    for flag_str in optionflags_str:
        flag_int |= doctest.OPTIONFLAGS_BY_NAME[flag_str]
    return flag_int


def pytest_configure(config):
    doctest_plugin = config.pluginmanager.getplugin('doctest')
    run_regular_doctest = config.option.doctestmodules and not config.option.doctest_plus
    use_doctest_plus = config.getini('doctest_plus') or config.option.doctest_plus or config.option.doctest_only
    if doctest_plugin is None or run_regular_doctest or not use_doctest_plus:
        return

    # We monkey-patch in our replacement doctest OutputChecker.  Not
    # great, but there isn't really an API to replace the checker when
    # using doctest.testfile, unfortunately.
    doctest.OutputChecker = OutputChecker
    OutputChecker.rtol = max(float(config.getini("doctest_plus_rtol")),
                             float(config.getoption("doctest_plus_rtol")))
    OutputChecker.atol = max(float(config.getini("doctest_plus_atol")),
                             float(config.getoption("doctest_plus_atol")))

    use_rst = config.getini('doctest_rst') or config.option.doctest_rst
    file_ext = config.option.text_file_format or config.getini('text_file_format') or 'rst'
    if use_rst:
        config.option.doctestglob.append('*.{}'.format(file_ext))

    # override default comment characters
    ext_comment_pairs = [pair.split('=') for pair in config.getini('text_file_comment_chars')]
    for ext, chars in ext_comment_pairs:
        comment_characters[ext] = chars

    class DocTestModulePlus(doctest_plugin.DoctestModule):
        # pytest 2.4.0 defines "collect".  Prior to that, it defined
        # "runtest".  The "collect" approach is better, because we can
        # skip modules altogether that have no doctests.  However, we
        # need to continue to override "runtest" so that the built-in
        # behavior (which doesn't do whitespace normalization or
        # handling __doctest_skip__) doesn't happen.
        def collect(self):
            # When running directly from pytest we need to make sure that we
            # don't accidentally import setup.py!
            if self.fspath.basename == "setup.py":
                return
            elif self.fspath.basename == "conftest.py":
                if PYTEST_GE_6_3:
                    module = self.config.pluginmanager._importconftest(
                        Path(self.fspath), self.config.getoption("importmode"))
                elif PYTEST_GT_5:
                    module = self.config.pluginmanager._importconftest(
                        self.fspath, self.config.getoption("importmode"))
                else:
                    module = self.config.pluginmanager._importconftest(
                        self.fspath)
            else:
                try:
                    module = self.fspath.pyimport()
                except ImportError:
                    if self.config.getvalue("doctest_ignore_import_errors"):
                        pytest.skip("unable to import module %r" % self.fspath)
                    else:
                        raise

            options = get_optionflags(self) | FIX

            # uses internal doctest module parsing mechanism
            finder = DocTestFinderPlus()
            runner = doctest.DebugRunner(
                verbose=False, optionflags=options, checker=OutputChecker())

            for test in finder.find(module):
                if test.examples:  # skip empty doctests
                    if config.getoption('remote_data', 'none') != 'any':

                        ignore_warnings_context_needed = False
                        show_warnings_context_needed = False

                        for example in test.examples:

                            # If warnings are to be ignored we need to catch them by
                            # wrapping the source in a context manager.
                            if example.options.get(IGNORE_WARNINGS, False):
                                example.source = ("with _doctestplus_ignore_all_warnings():\n"
                                                  + indent(example.source, '    '))
                                ignore_warnings_context_needed = True

                            # Same for SHOW_WARNINGS
                            if example.options.get(SHOW_WARNINGS, False):
                                example.source = ("with _doctestplus_show_all_warnings():\n"
                                                  + indent(example.source, '    '))
                                show_warnings_context_needed = True

                            if example.options.get(REMOTE_DATA):
                                example.options[doctest.SKIP] = True

                        # We insert the definition of the context manager to ignore
                        # warnings at the start of the file if needed.
                        if ignore_warnings_context_needed:
                            test.examples.insert(0, doctest.Example(
                                source=IGNORE_WARNINGS_CONTEXT, want=''))

                        if show_warnings_context_needed:
                            test.examples.insert(0, doctest.Example(
                                source=SHOW_WARNINGS_CONTEXT, want=''))

                    try:
                        yield doctest_plugin.DoctestItem.from_parent(
                            self, name=test.name, runner=runner, dtest=test
                        )
                    except AttributeError:
                        # pytest < 5.4
                        yield doctest_plugin.DoctestItem(
                            test.name, self, runner, test)

    class DocTestTextfilePlus(pytest.Module):

        def collect(self):
            encoding = self.config.getini("doctest_encoding")
            text = self.fspath.read_text(encoding)
            filename = str(self.fspath)
            name = self.fspath.basename
            globs = {"__name__": "__main__"}

            optionflags = get_optionflags(self) | FIX

            runner = doctest.DebugRunner(
                verbose=False, optionflags=optionflags, checker=OutputChecker())

            parser = DocTestParserPlus()
            test = parser.get_doctest(text, globs, name, filename, 0)
            if test.examples:
                try:
                    yield doctest_plugin.DoctestItem.from_parent(
                        self, name=test.name, runner=runner, dtest=test
                    )
                except AttributeError:
                    # pytest < 5.4
                    yield doctest_plugin.DoctestItem(test.name, self, runner, test)

    class DocTestParserPlus(doctest.DocTestParser):
        """
        An extension to the builtin DocTestParser that handles the
        special directives for skipping tests.

        The directives are:

           - ``.. doctest-skip::``: Skip the next doctest chunk.

           - ``.. doctest-requires:: module1, module2``: Skip the next
             doctest chunk if the given modules/packages are not
             installed.

           - ``.. doctest-skip-all``: Skip all subsequent doctests.
        """

        def parse(self, s, name=None):
            result = doctest.DocTestParser.parse(self, s, name=name)

            # result is a sequence of alternating text chunks and
            # doctest.Example objects.  We need to look in the text
            # chunks for the special directives that help us determine
            # whether the following examples should be skipped.

            required = []
            skip_next = False
            skip_all = False

            ext = os.path.splitext(name)[1] if name else '.rst'
            if ext not in comment_characters:
                warnings.warn("file format '{}' is not recognized, assuming "
                              "'{}' as the comment character."
                              .format(ext, comment_characters['.rst']))
                ext = '.rst'
            comment_char = comment_characters[ext]

            ignore_warnings_context_needed = False
            show_warnings_context_needed = False

            for entry in result:

                if isinstance(entry, str) and entry:
                    required = []
                    skip_next = False
                    lines = entry.strip().splitlines()
                    if any([re.match('{} doctest-skip-all'.format(comment_char), x.strip()) for x in lines]):
                        skip_all = True
                        continue

                    if not len(lines):
                        continue

                    # We allow last and second to last lines to match to allow
                    # special environment to be in between, e.g. \begin{python}
                    last_lines = lines[-2:]
                    matches = [re.match(
                        r'{}\s+doctest-skip\s*::(\s+.*)?'.format(comment_char),
                        last_line) for last_line in last_lines]

                    if len(matches) > 1:
                        match = matches[0] or matches[1]
                    else:
                        match = matches[0]

                    if match:
                        marker = match.group(1)
                        if (marker is None or
                                (marker.strip() == 'win32' and
                                 sys.platform == 'win32')):
                            skip_next = True
                            continue

                    matches = [re.match(
                        r'{}\s+doctest-requires\s*::\s+(.*)'.format(comment_char),
                        last_line) for last_line in last_lines]

                    if len(matches) > 1:
                        match = matches[0] or matches[1]
                    else:
                        match = matches[0]

                    if match:
                        # 'a a' or 'a,a' or 'a, a'-> [a, a]
                        required = re.split(r'\s*[,\s]\s*', match.group(1))
                elif isinstance(entry, doctest.Example):

                    # If warnings are to be ignored we need to catch them by
                    # wrapping the source in a context manager.
                    if entry.options.get(IGNORE_WARNINGS, False):
                        entry.source = ("with _doctestplus_ignore_all_warnings():\n"
                                        + indent(entry.source, '    '))
                        ignore_warnings_context_needed = True

                    # Same to show warnings
                    if entry.options.get(SHOW_WARNINGS, False):
                        entry.source = ("with _doctestplus_show_all_warnings():\n"
                                        + indent(entry.source, '    '))
                        show_warnings_context_needed = True

                    has_required_modules = DocTestFinderPlus.check_required_modules(required)
                    if skip_all or skip_next or not has_required_modules:
                        entry.options[doctest.SKIP] = True

                    if config.getoption('remote_data', 'none') != 'any' and entry.options.get(REMOTE_DATA):
                        entry.options[doctest.SKIP] = True

            # We insert the definition of the context manager to ignore
            # warnings at the start of the file if needed.
            if ignore_warnings_context_needed:
                result.insert(0, doctest.Example(source=IGNORE_WARNINGS_CONTEXT, want=''))

            if show_warnings_context_needed:
                result.insert(0, doctest.Example(source=SHOW_WARNINGS_CONTEXT, want=''))

            return result

    config.pluginmanager.register(
        DoctestPlus(
            DocTestModulePlus,
            DocTestTextfilePlus,
            config.option.doctestglob,
        ),
        'doctestplus',
    )
    # Remove the doctest_plugin, or we'll end up testing the .rst files twice.
    config.pluginmanager.unregister(doctest_plugin)


class DoctestPlus(object):
    def __init__(self, doctest_module_item_cls, doctest_textfile_item_cls, file_globs):
        """
        doctest_module_item_cls should be a class inheriting
        `pytest.doctest.DoctestItem` and `pytest.File`.  This class handles
        running of a single doctest found in a Python module.  This is passed
        in as an argument because the actual class to be used may not be
        available at import time, depending on whether or not the doctest
        plugin for py.test is available.
        """
        self._doctest_module_item_cls = doctest_module_item_cls
        self._doctest_textfile_item_cls = doctest_textfile_item_cls
        self._file_globs = file_globs
        # Directories to ignore when adding doctests
        self._ignore_paths = []

    def pytest_ignore_collect(self, path, config):
        """
        Skip paths that match any of the doctest_norecursedirs patterns or
        if doctest_only is True then skip all regular test files (eg test_*.py).
        """
        if PYTEST_GE_6_3:
            dirpath = Path(path).parent
        else:
            dirpath = path.dirpath()
        collect_ignore = config._getconftest_pathlist("collect_ignore", path=dirpath)

        # The collect_ignore conftest.py variable should cause all test
        # runners to ignore this file and all subfiles and subdirectories
        if collect_ignore is not None and path in collect_ignore:
            return True

        if config.option.doctest_only:
            for pattern in config.getini('python_files'):
                if path.check(fnmatch=pattern):
                    return True

        def get_list_opt(name):
            return getattr(config.option, name, None) or []

        for ignore_path in get_list_opt('ignore'):
            ignore_path = os.path.abspath(ignore_path)
            if str(path).startswith(ignore_path):
                return True

        for pattern in get_list_opt('ignore_glob'):
            if path.check(fnmatch=pattern):
                return True

        for pattern in config.getini("doctest_norecursedirs"):
            if path.check(fnmatch=pattern):
                # Apparently pytest_ignore_collect causes files not to be
                # collected by any test runner; for DoctestPlus we only want to
                # avoid creating doctest nodes for them
                self._ignore_paths.append(path)
                break

        for option in config.getini("doctest_subpackage_requires"):
            subpackage_pattern, required = option.split('=', 1)
            if path.check(fnmatch=subpackage_pattern.strip()):
                required = required.strip().split(';')
                if not DocTestFinderPlus.check_required_modules(required):
                    self._ignore_paths.append(path)
                    break

        return False

    def pytest_collect_file(self, path, parent):
        """Implements an enhanced version of the doctest module from py.test
        (specifically, as enabled by the --doctest-modules option) which
        supports skipping all doctests in a specific docstring by way of a
        special ``__doctest_skip__`` module-level variable.  It can also skip
        tests that have special requirements by way of
        ``__doctest_requires__``.

        ``__doctest_skip__`` should be a list of functions, classes, or class
        methods whose docstrings should be ignored when collecting doctests.

        This also supports wildcard patterns.  For example, to run doctests in
        a class's docstring, but skip all doctests in its modules use, at the
        module level::

            __doctest_skip__ = ['ClassName.*']

        You may also use the string ``'.'`` in ``__doctest_skip__`` to refer
        to the module itself, in case its module-level docstring contains
        doctests.

        ``__doctest_requires__`` should be a dictionary mapping wildcard
        patterns (in the same format as ``__doctest_skip__``) to a list of one
        or more modules that should be *importable* in order for the tests to
        run.  For example, if some tests require the scipy module to work they
        will be skipped unless ``import scipy`` is possible.  It is also
        possible to use a tuple of wildcard patterns as a key in this dict::

            __doctest_requires__ = {('func1', 'func2'): ['scipy']}

        """
        for ignore_path in self._ignore_paths:
            if ignore_path.common(path) == ignore_path:
                return None

        if path.ext == '.py':
            if path.basename == 'conf.py':
                return None

            # Don't override the built-in doctest plugin
            try:
                return self._doctest_module_item_cls.from_parent(parent, fspath=path)
            except AttributeError:
                # pytest < 5.4
                return self._doctest_module_item_cls(path, parent)

        elif any([path.check(fnmatch=pat) for pat in self._file_globs]):
            # Ignore generated .rst files
            parts = str(path).split(os.path.sep)

            # Don't test files that start with a _
            if path.basename.startswith('_'):
                return None

            # Don't test files in directories that start with a '_' if those
            # directories are inside docs. Note that we *should* allow for
            # example /tmp/_q/docs/file.rst but not /tmp/docs/_build/file.rst
            # If we don't find 'docs' in the path, we should just skip this
            # check to be safe. We also want to skip any api sub-directory
            # of docs.
            if 'docs' in parts:
                # We index from the end on the off chance that the temporary
                # directory includes 'docs' in the path, e.g.
                # /tmp/docs/371j/docs/index.rst You laugh, but who knows! :)
                # Also, it turns out lists don't have an rindex method. Huh??!!
                docs_index = len(parts) - 1 - parts[::-1].index('docs')
                if any(x.startswith('_') or x == 'api' for x in parts[docs_index:]):
                    return None

            # TODO: Get better names on these items when they are
            # displayed in py.test output
            try:
                return self._doctest_textfile_item_cls.from_parent(parent, fspath=path)
            except AttributeError:
                # pytest < 5.4
                return self._doctest_textfile_item_cls(path, parent)


class DocTestFinderPlus(doctest.DocTestFinder):
    """Extension to the default `doctest.DoctestFinder` that supports
    ``__doctest_skip__`` magic.  See `pytest_collect_file` for more details.
    """

    # Caches the results of import attempts
    _import_cache = {}
    _module_checker = ModuleChecker()

    @classmethod
    def check_required_modules(cls, mods):
        """Check that modules in `mods` list are available.

        Parameters
        ----------
        mods : list of str
            List of modules. Modules can have specified versions (eg 'numpy>=1.15')

        Returns
        -------
        bool
            True if all modules in list are available.
        """
        for mod in mods:
            if mod in cls._import_cache:
                if not cls._import_cache[mod]:
                    return False

            if cls._module_checker.check(mod):
                cls._import_cache[mod] = True
            else:
                cls._import_cache[mod] = False
                return False
        return True

    def find(self, obj, name=None, module=None, globs=None, extraglobs=None):
        tests = doctest.DocTestFinder.find(self, obj, name, module, globs, extraglobs)
        if hasattr(obj, '__doctest_skip__') or hasattr(obj, '__doctest_requires__'):
            if name is None and hasattr(obj, '__name__'):
                name = obj.__name__
            else:
                raise ValueError("DocTestFinder.find: name must be given "
                                 "when obj.__name__ doesn't exist: {!r}"
                                 .format((type(obj),)))

            def test_filter(test):
                for pat in getattr(obj, '__doctest_skip__', []):
                    if pat == '*':
                        return False
                    elif pat == '.' and test.name == name:
                        return False
                    elif fnmatch.fnmatch(test.name, '.'.join((name, pat))):
                        return False

                reqs = getattr(obj, '__doctest_requires__', {})
                for pats, mods in reqs.items():
                    if not isinstance(pats, tuple):
                        pats = (pats,)
                    for pat in pats:
                        if not fnmatch.fnmatch(test.name, '.'.join((name, pat))):
                            continue
                        if not self.check_required_modules(mods):
                            return False
                return True

            tests = list(filter(test_filter, tests))

        return tests
