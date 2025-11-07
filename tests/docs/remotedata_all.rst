:orphan:

.. doctest-remote-data-all::

.. _label_to_check_that_no_content_works_probably_unnecessary2:

Some Bad Test Cases
*******************

All of the example code blocks in this file are going to fail if they run. So
if the directive used at the top of this file does not work, then there are
going to be test failures.

Undefined Variables
===================

This one will fail because the variables haven't been defined::

    >>> 2 + 3
    5
