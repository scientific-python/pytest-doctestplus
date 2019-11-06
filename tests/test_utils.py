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

    def test_check_distribution(self):
        c = ModuleChecker()
        # in python3.4+ packages attribute will not be populated
        # because it calls 'pip freeze' which is slow
        if not c.packages:
            c.packages = c.get_packages()
            # after this we will be able to test _check_distribution even in
            # python3.4+ environment
        assert c._check_distribution('pytest>1.0')
        assert not c._check_distribution('pytest<1.0')
        assert not c._check_distribution('foobar>1.0')
