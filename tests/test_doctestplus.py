pytest_plugins = ['pytester']


def test_ignored_whitespace(testdir):
    testdir.makeini(
        """
        [pytest]
        doctest_optionflags = ELLIPSIS NORMALIZE_WHITESPACE
        doctestplus = enabled
    """
    )
    p = testdir.makepyfile(
        """
        class MyClass(object):
            '''
            >>> a = "foo    "
            >>> print(a)
            foo
            '''
            pass
    """
    )
    reprec = testdir.inline_run(p, "--doctest-plus")
    reprec.assertoutcome(passed=1)


def test_non_ignored_whitespace(testdir):
    testdir.makeini(
        """
        [pytest]
        doctest_optionflags = ELLIPSIS
        doctestplus = enabled
    """
    )
    p = testdir.makepyfile(
        """
        class MyClass(object):
            '''
            >>> a = "foo    "
            >>> print(a)
            foo
            '''
            pass
    """
    )
    reprec = testdir.inline_run(p, "--doctest-plus")
    reprec.assertoutcome(failed=1, passed=0)


def test_float_cmp(testdir):
    testdir.makeini(
        """
        [pytest]
        doctest_optionflags = ELLIPSIS
        doctestplus = enabled
    """
    )
    p = testdir.makepyfile(
        """
        def f():
            '''
            >>> x = 1/3.
            >>> x
            0.333333
            '''
            pass

        def g():
            '''
            >>> x = 1/3.
            >>> x    # doctest: +FLOAT_CMP
            0.333333
            '''
            pass
    """
    )
    reprec = testdir.inline_run(p, "--doctest-plus")
    reprec.assertoutcome(failed=1, passed=1)


def test_float_cmp_global(testdir):
    testdir.makeini(
        """
        [pytest]
        doctest_optionflags = FLOAT_CMP
        doctestplus = enabled
    """
    )
    p = testdir.makepyfile(
        """
        def f():
            '''
            >>> x = 1/3.
            >>> x
            0.333333
            '''
            pass
    """
    )
    reprec = testdir.inline_run(p, "--doctest-plus")
    reprec.assertoutcome(passed=1)


def test_allow_bytes_unicode(testdir):
    testdir.makeini(
        """
        [pytest]
        doctestplus = enabled
    """
    )
    # These are dummy tests just to check tht doctest-plus can parse the
    # ALLOW_BYTES and ALLOW_UNICODE options. It doesn't actually implement
    # these options.
    p = testdir.makepyfile(
        """
        def f():
            '''
            >>> 1 # doctest: +ALLOW_BYTES
            1
            >>> 1 # doctest: +ALLOW_UNICODE
            1
            '''
            pass
    """
    )
    reprec = testdir.inline_run(p, "--doctest-plus")
    reprec.assertoutcome(passed=1)


def test_doctest_skip(testdir):
    testdir.makeini(
        """
        [pytest]
        doctestplus = enabled
    """
    )
    p = testdir.makepyfile(
        """
        from pytest_doctestplus import doctest_skip

        @doctest_skip("need to skip...")
        def f():
            '''
            >>> 1/0
            '''
            return 2

        # Check the function still works:
        assert f() == 2
    """
    )
    reprec = testdir.inline_run(p, "--doctest-plus")
    reprec.assertoutcome(passed=0, failed=0)


def test_doctest_skip_class(testdir):
    testdir.makeini(
        """
        [pytest]
        doctestplus = enabled
    """
    )
    p = testdir.makepyfile(
        """
        from pytest_doctestplus import doctest_skip

        @doctest_skip("need to skip...")
        class Thing(object):
            '''
            >>> 1/0
            '''
            def meth(self):
                '''
                >>> 1/0
                '''
                pass

        class SubThing1(Thing):
            '''
            >>> 1+1
            2
            '''
            def meth(self):
                '''
                >>> 1+2
                3
                '''
                pass

        class SubThing2(Thing):
            '''
            >>> 1+1
            2
            '''
            @doctest_skip("skip only this...")
            def meth(self):
                '''
                >>> 1/0
                '''
                pass
    """
    )
    reprec = testdir.inline_run(p, "--doctest-plus")
    reprec.assertoutcome(passed=3, failed=0)


def test_doctest_skipif(testdir):
    testdir.makeini(
        """
        [pytest]
        doctestplus = enabled
    """
    )
    p = testdir.makepyfile(
        """
        from pytest_doctestplus import doctest_skipif

        @doctest_skipif(True, "will skip")
        def f():
            '''
            >>> 1/0
            '''
            return 3

        @doctest_skipif(False, "won't skip")
        def g():
            '''
            >>> 1+1
            2
            '''
            return 4

        assert f() == 3
        assert g() == 4

    """
    )
    reprec = testdir.inline_run(p, "--doctest-plus")
    reprec.assertoutcome(passed=1, failed=0)


def test_doctest_skipif_callable(testdir):
    testdir.makeini(
        """
        [pytest]
        doctestplus = enabled
    """
    )
    p = testdir.makepyfile(
        """
        from pytest_doctestplus import doctest_skipif

        @doctest_skipif(lambda: True, "will skip")
        def f():
            '''
            >>> 1/0
            '''
            return 3

        @doctest_skipif(lambda: False, "won't skip")
        def g():
            '''
            >>> 1+1
            2
            '''
            return 4

        assert f() == 3
        assert g() == 4

    """
    )
    reprec = testdir.inline_run(p, "--doctest-plus")
    reprec.assertoutcome(passed=1, failed=0)


def test_doctest_skipif_callable_delayed_check(testdir):
    testdir.makeini(
        """
        [pytest]
        doctestplus = enabled
    """
    )
    p = testdir.makepyfile(
        """
        from pytest_doctestplus import doctest_skipif

        @doctest_skipif(lambda: not installed, "skip if _nonexistent_ not installed")
        def f():
            '''
            >>> 1/0
            '''
            return 3

        installed = False

        assert f() == 3
    """
    )
    reprec = testdir.inline_run(p, "--doctest-plus")
    reprec.assertoutcome(passed=0, failed=0)
