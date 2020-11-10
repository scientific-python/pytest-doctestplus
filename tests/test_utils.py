from pytest_doctestplus.utils import ModuleChecker


class TestModuleChecker:
    def test_simple(self):
        c = ModuleChecker()
        assert c.check('sys')
        assert not c.check('foobar')

    def test_with_version(self):
        c = ModuleChecker()
        assert c.check('pytest>1.0')
        assert not c.check('foobar>1.0')
