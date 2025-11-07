:orphan:

.. doctest-requires-all:: asdfasdfasdf

.. _label_to_check_that_no_content_works_probably_unnecessary:

Some Bad Test Cases
*******************

All of the example code blocks in this file are going to fail if they run. So
if the directive used at the top of this file does not work, then there are
going to be test failures.

Undefined Variables
===================

This one will fail because the variables haven't been defined::

    >>> x + y
    5

No Such Module
==============

This one will fail because there's (probably) no such module::

    >>> import foobar
    >>> foobar.baz(42)
    0

What???
=======

This one will fail because it's just not valid python::

    >>> NOT VALID PYTHON, OKAY?
    >>> + 5
    10
