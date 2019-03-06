0.3.0 (2019-03-06)
==================

- Honor the ``collect_ignore`` option used in ``conftest.py``. [#36]

- Make use of ``doctest_optionflags`` settings. [#39]

- Make it possible to set ``FLOAT_CMP`` globally in ``setup.cfg``. [#40]

- Drop support for ``pytest`` versions earlier than 3.0. [#46]

- Extend ``doctest-skip``, ``doctest-skip-all``, and ``doctest-requires``
  directives to work in TeX files. [#43]


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
