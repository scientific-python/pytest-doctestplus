Some Good Test Cases
********************

Some of the example code blocks in this file are perfectly valid and will pass
if they run. Some are not. The intent of this file is to test the directives
that are provided by the `--doctest-rst` option to make sure that the bad ones
get skipped.

Here's One That Works
=====================

This code block should work just fine::

    >>> 1 + 1
    2

This one should work just fine as well::

    >>> x = 5
    >>> x
    5

Here's One That Doesn't
=======================

This code won't run. So let's make sure that it gets skipped:

.. doctest-skip::

    >>> y + z
    42

This one doesn't work either:

.. doctest-skip::

    >>> print(blue)
    'blue'

Good Imports
============

There should be nothing wrong with this code, so we'll let it run::

    >>> import os
    >>> os.path.curdir
    '.'

Make sure the `doctest-requires` directive works for modules that are
available:

.. doctest-requires:: sys

    >>> import sys

Bad Imports
===========

I don't think this module exists, so we should make sure that this code doesn't
run:

.. doctest-requires:: foobar

    >>> import foobar
    >>> foobar.baz(42)
    1


Package version
===============

Code in doctest should run only if version condition is satisfied:

.. doctest-requires:: numpy<=0.1

    >>> import numpy
    >>> assert 0


.. doctest-requires:: pytest>=1.0 pytest>=2.0

    >>> import pytest
