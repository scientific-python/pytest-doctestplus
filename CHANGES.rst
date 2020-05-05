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
