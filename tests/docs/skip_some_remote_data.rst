:orphan:

Some test cases for remote data
*******************************

We only run tests on this file when ``remote-data`` is not opted in as most
of the code examples below should fail if not skipped.


Remote data block code sandwiched in block codes
================================================

This code block should work just fine::

    >>> 1 + 1
    2

This should be skipped when remote data is not requested
otherwise the test should fail::

.. doctest-remote-data::

    >>> 1 + 3
    2

This code block should work just fine::

    >>> 1 + 1
    2


Remote data followed by plain block code
========================================

This one should be skipped when remote data is not requested
otherwise the test should fail::

.. doctest-remote-data::

    >>> 1 + 3
    2

This code block should work just fine::

    >>> 1 + 1
    2


Several blocks of Remote data
=============================

The three block codes should be skipped when remote data
is not requested otherwise the tests should fail:

.. doctest-remote-data::

    >>> 1 + 3
    2

.. doctest-remote-data::

    >>> 1 + 4
    2

.. doctest-remote-data::

    >>> 1 + 5
    2

Composite directive with remote data
====================================

This should be skipped otherwise the test should fail::

.. doctest-remote-data::

    >>> 1 + 1
    3
    >>> import warnings
    >>> warnings.warn('A warning occurred', UserWarning)  # doctest: +IGNORE_WARNINGS
