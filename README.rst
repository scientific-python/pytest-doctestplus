==================
pytest-doctestplus
==================

This package contains a plugin for the `pytest`_ framework that provides
advanced doctest support and enables the testing of `reStructuredText`_
(".rst") files. It was originally part of the `astropy`_ core package, but has
been moved to a separate package in order to be of more general use.

.. _pytest: https://pytest.org/en/latest/
.. _astropy: https://astropy.org/en/latest/
.. _reStructuredText: https://en.wikipedia.org/wiki/ReStructuredText


Motivation
----------

This plugin provides advanced features for testing example Python code that is
included in Python docstrings and in standalone documentation files.

Good documentation for developers contains example code. This is true of both
standalone documentation and of documentation that is integrated with the code
itself. Python provides a mechanism for testing code snippets that are provided
in Python docstrings. The unit test framework pytest provides a mechanism for
running doctests against both docstrings in source code and in standalone
documentation files.

This plugin augments the functionality provided by Python and pytest by
providing the following features:

* approximate floating point comparison for doctests that produce floating
  point results (see `Floating Point Comparison`_)
* skipping particular classes, methods, and functions when running doctests (see `Skipping Tests`_)
* handling doctests that use remote data in conjunction with the
  `pytest-remotedata`_ plugin (see `Remote Data`_)
* optional inclusion of ``*.rst`` files for doctests (see `Setup and Configuration`_)

.. _pytest-remotedata: https://github.com/astropy/pytest-remotedata

Installation
------------

The ``pytest-doctestplus`` plugin can be installed using ``pip``::

    $ pip install pytest-doctestplus

It is also possible to install the latest development version from the source
repository::

    $ git clone https://github.com/astropy/pytest-doctestplus
    $ cd pytest-doctestplus
    $ python ./setup.py install

In either case, the plugin will automatically be registered for use with
``pytest``.

Usage
-----

.. _setup:

Setup and Configuration
~~~~~~~~~~~~~~~~~~~~~~~

This plugin provides two command line options: ``--doctest-plus`` for enabling
the advanced features mentioned above, and ``--doctest-rst`` for including
``*.rst`` files in doctest collection.

This plugin can also be enabled by default by adding ``doctest_plus = enabled``
to the ``[tool:pytest]`` section of the package's ``setup.cfg`` file.

The plugin is applied to all directories and files that ``pytest`` collects.
This means that configuring ``testpaths`` and ``norecursedirs`` in
``setup.cfg`` also affects the files that will be discovered by
``pytest-doctestplus``. In addition, this plugin provides a
``doctest_norecursedirs`` configuration variable that indicates directories
that should be ignored by ``pytest-doctestplus`` but do not need to be ignored
by other ``pytest`` features.

Doctest Directives
~~~~~~~~~~~~~~~~~~

The ``pytest-doctestplus`` plugin defines `doctest directives`_ that are used
to control the behavior of particular features. For general information on
directives and how they are used, consult the `documentation`_. The specifics
of the directives that this plugin defines are described in the sections below.

.. _doctest directives: https://docs.python.org/3/library/doctest.html#directives
.. _documentation: https://docs.python.org/3/library/doctest.html#directives

Floating Point Comparison
~~~~~~~~~~~~~~~~~~~~~~~~~

Some doctests may produce output that contains string representations of
floating point values.  Floating point representations are often not exact and
contain roundoffs in their least significant digits.  Depending on the platform
the tests are being run on (different Python versions, different OS, etc.) the
exact number of digits shown can differ.  Because doctests work by comparing
strings this can cause such tests to fail.

To address this issue, the ``pytest-doctestplus`` plugin provides support for a
``FLOAT_CMP`` flag that can be used with doctests.  For example:

.. code-block:: python

  >>> 1.0 / 3.0  # doctest: +FLOAT_CMP
  0.333333333333333311

When this flag is used, the expected and actual outputs are both parsed to find
any floating point values in the strings.  Those are then converted to actual
Python `float` objects and compared numerically.  This means that small
differences in representation of roundoff digits will be ignored by the
doctest.  The values are otherwise compared exactly, so more significant
(albeit possibly small) differences will still be caught by these tests.

Skipping Tests
~~~~~~~~~~~~~~

Doctest provides the ``+SKIP`` directive for skipping statements that should
not be executed when testing documentation. However, it is often useful to be
able to skip docstrings associated with particular functions, methods, classes,
or even entire files.

Skip Unconditionally
^^^^^^^^^^^^^^^^^^^^

The ``pytest-doctestplus`` plugin provides a way to indicate that certain
docstrings should be skipped altogether. This is configured by defining the
variable ``__doctest_skip__`` in each module where tests should be skipped. The
value of ``__doctest_skip__`` should be a list of wildcard patterns for all
functions/classes whose doctests should be skipped.  For example::

   __doctest_skip__ = ['myfunction', 'MyClass', 'MyClass.*']

skips the doctests in a function called ``myfunction``, the doctest for a
class called ``MyClass``, and all *methods* of ``MyClass``.

Module docstrings may contain doctests as well. To skip the module-level
doctests::

    __doctest_skip__  = ['.', 'myfunction', 'MyClass']

To skip all doctests in a module::

   __doctest_skip__ = ['*']

Doctest Dependencies
^^^^^^^^^^^^^^^^^^^^

It is also possible to skip certain doctests depending on whether particular
dependencies are available. This is configured by defining the variable
``__doctest_requires__`` at the module level. The value of this variable is
a dictionary that indicates the modules that are required to run the doctests
associated with particular functions, classes, and methods.

The keys in the dictionary are wildcard patterns like those described above, or
tuples of wildcard patterns, indicating which docstrings should be skipped. The
values in the dictionary are lists of module names that are required in order
for the given doctests to be executed.

Consider the following example::

    __doctest_requires__ = {('func1', 'func2'): ['scipy']}

Having this module-level variable will require ``scipy`` to be importable
in order to run the doctests for functions ``func1`` and ``func2`` in that
module.

Remote Data
~~~~~~~~~~~

The ``pytest-doctestplus`` plugin can be used in conjunction with the
`pytest-remotedata`_ plugin in order to control doctest code that requires
access to data from the internet. In order to make use of these features, the
``pytest-remotedata`` plugin must be installed, and remote data access must
be enabled using the ``--remote-data`` command line option to ``pytest``. See
the `pytest-remotedata plugin documentation`__ for more details.

The following example illustrates how a doctest that uses remote data should be
marked::

    .. code-block:: python
    
        >>> from urlib.request import urlopen
        >>> url = urlopen('http://astropy.org') # doctest: +REMOTE_DATA

The ``+REMOTE_DATA`` directive indicates that the marked statement should only
be executed if the ``--remote-data`` option is given. By default, all
statements marked with ``--remote-data`` will be skipped.

.. _pytest-remotedata: https://github.com/astropy/pytest-remotedata
__ pytest-remotedata_

Development Status
------------------

.. image:: https://travis-ci.org/astropy/pytest-doctestplus.svg
    :target: https://travis-ci.org/astropy/pytest-doctestplus
    :alt: Travis CI Status

.. image:: https://ci.appveyor.com/api/projects/status/vwbkv8vulemhak2p?svg=true 
    :target: https://ci.appveyor.com/project/Astropy/pytest-remotedata/branch/master
    :alt: Appveyor Status

Questions, bug reports, and feature requests can be submitted on `github`_.

.. _github: https://github.com/astropy/pytest-doctestplus

License
-------
This plugin is licensed under a 3-clause BSD style license - see the
``LICENSE.rst`` file.
