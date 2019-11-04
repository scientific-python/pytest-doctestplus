import pytest


@pytest.fixture
def docstring_file(testdir):
    """Fixture that returns generator of text file with class and specified docstring."""

    # note that we have to use raw strings in 2 places:
    # - in file string because we don't want \n to evaluate
    # - in inner docstring because doctest has problems with \n for the same reasons as above
    def make_file(doctest_string):
        return testdir.makepyfile(r"""
            class MyClass(object):
                r'''
                %s
                '''
                pass
        """ % doctest_string)

    return make_file
