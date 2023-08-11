1.0.0 (2023-08-11)
==================

- Changing GitHub organization.


0.13.0 (2023-06-07)
===================

- Compatibility with pytest 7.4 with respect to ``norecursedirs`` handling. [#201]

- Respect ``--doctest-continue-on-failure`` flag. [#197]

- Report doctests raising skip exceptions as skipped. [#196]

0.12.1 (2022-09-26)
===================

- Allow floating point comparison in Python dictionary. [#186]

0.12.0 (2022-02-25)
===================

- Run doctests in docstrings of Numpy ufuncs. [#174, #175]

0.11.2 (2021-12-09)
===================

- Fix version check for pytest 7.0.0rc1. [#171]

- Recognize text beginning with ``<!--`` as a comment for Markdown (``.md``)
  files. [#169]

0.11.1 (2021-11-16)
===================

- Fixed compatibility with pytest-dev. [#168]

0.11.0 (2021-09-20)
===================

- Added support for ``testcleanup`` and documented existing support for
  ``testsetup``. [#165]


0.10.1 (2021-07-20)
===================

- Fix the doctestplus sphinx extension to recognize the
  ``doctest-remote-data`` directive. [#162]


0.10.0 (2021-07-01)
===================

- Added ``..doctest-remote-data::`` directive to control remote data
  access for a chunk of code. [#137]

- Drop support for ``python`` 3.6. [#159]

- Fixed a bug where the command-line option ``--remote-data=any`` (associated
  with the ``pytest-remotedata`` plugin) would cause ``IGNORE_WARNINGS`` and
  ``SHOW_WARNINGS`` options to be ignored in module docstrings. [#152]

- Fix wrong behavior with ``IGNORE_WARNINGS`` and ``SHOW_WARNINGS`` that could
  make a block to pass instead of being skipped. [#148]


0.9.0 (2021-01-14)
==================

- Declare ``setuptools`` runtime dependency [#93]

- Add ``SHOW_WARNINGS`` flag to show warnings. [#136]

- Add the doctestplus sphinx extension. [#113]

- Compatibility with pytest>=6.3 [#140, #141]

0.8.0 (2020-07-31)
==================

- Compatibility with ``pytest`` 6.0.0. [#120]

0.7.0 (2020-05-20)
==================

- Added a new ini option, ``doctest_subpackage_requires``, that can be used to skip
  specific subpackages based on required packages. [#112]

0.6.1 (2020-05-04)
==================

- Disabling the usage of the ``doctest_ignore_import_errors`` option to
  ensure no behaviour changes compared to the 0.5.0 release. [#108]


0.6.0 (2020-04-30)
==================

- Drop support for ``python`` versions earlier than 3.6. [#103]

- Drop support for ``pytest`` versions earlier than 4.0. [#103]

- Fix compatibility with ``pytest`` 5.4. [#103]


0.5.0 (2019-11-15)
==================

- No longer require Numpy. [#69]

- Fixed a bug that caused ``__doctest_requires__`` to not work correctly
  with submodules. [#73]

- Fixed a limitation that meant that ``ELLIPSIS`` and ``FLOAT_CMP`` could not
  be used at the same time. [#75]

- Fixed a bug that caused ``.. doctest-requires::`` to not work correctly. [#78]

- Fixed a FutureWarning related to split() with regular expressions. [#78]

- Make it possible to specify versions in ``.. doctest-requires::``. [#78]

- Allow to use doctest-glob option instead of doctest-rst and text-file-format [#80]

- Make comment character configurable via ini variable text_file_comment_chars [#80]

- Respect ``ignore`` and ``ignore-glob`` options from pytest. [#82]

- Add ``--doctest-only`` option. [#83]

- Added an ``IGNORE_WARNINGS`` option for ``# doctest:`` [#84]

0.4.0 (2019-09-17)
==================

- Avoid ``SyntaxWarning`` regarding invalid escape sequence in Python
  3.9. [#62]

- Compatibility with ``pytest`` 5.1 to avoid ``AttributeError`` caused by
  ``FixtureRequest``. [#63]


0.3.0 (2019-03-06)
==================

- Honor the ``collect_ignore`` option used in ``conftest.py``. [#36]

- Make use of ``doctest_optionflags`` settings. [#39]

- Make it possible to set ``FLOAT_CMP`` globally in ``setup.cfg``. [#40]

- Drop support for ``pytest`` versions earlier than 3.0. [#46]

- Extend ``doctest-skip``, ``doctest-skip-all``, and ``doctest-requires``
  directives to work in TeX files. [#43, #47]


0.2.0 (2018-11-14)
==================

- Add ``doctest-plus-atol`` and ``doctest-plus-rtol`` options for setting the
  numerical tolerance. [#21]

- Update behavior of ``--doctest-modules`` option when plugin is installed. [#26]

0.1.3 (2018-04-20)
==================

- Fix packaging error: do not include tests as part of package distribution.
  [#19]

0.1.2 (2017-12-07)
==================

- Update README. Use README for long description on PyPi. [#12]


0.1.1 (2017-10-18)
==================

- Port fix from astropy core that addresses changes to numpy formatting of
  float scalars. [#8]

0.1 (2017-10-10)
================

- Alpha release.
