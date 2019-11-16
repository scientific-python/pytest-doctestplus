import doctest

from pytest_doctestplus.output_checker import FLOAT_CMP, OutputChecker


class TestFloats:
    def test_normalize_floats(self):
        c = OutputChecker()
        got = "A 65.0\nB 66.0"

        want = "A 65.0\nB 66.0"
        assert c.normalize_floats(want, got, flags=FLOAT_CMP)

        want = "A 65.0\nB   66.0  "
        assert c.normalize_floats(
            want, got, flags=FLOAT_CMP | doctest.NORMALIZE_WHITESPACE
        )

        want = "A 65.0\nB 66.01"
        assert not c.normalize_floats(want, got, flags=FLOAT_CMP)

    def test_normalize_with_blank_line(self):
        c = OutputChecker()
        got = "\nA 65.0\nB 66.0"
        want = "<BLANKLINE>\nA 65.0\nB 66.0"
        assert c.normalize_floats(want, got, flags=FLOAT_CMP)
        assert not c.normalize_floats(
            want, got, flags=FLOAT_CMP | doctest.DONT_ACCEPT_BLANKLINE
        )

    def test_normalize_with_ellipsis(self):
        c = OutputChecker()
        got = []
        for char in ["A", "B", "C", "D", "E"]:
            got.append("%s %s" % (char, float(ord(char))))
        got = "\n".join(got)

        want = "A 65.0\nB 66.0\n...G 70.0"
        assert not c.normalize_floats(want, got, flags=doctest.ELLIPSIS | FLOAT_CMP)

        want = "A 65.0\nB 66.0\n..."
        assert c.normalize_floats(want, got, flags=doctest.ELLIPSIS | FLOAT_CMP)

        want = "A 65.0\nB 66.0\n...\nE 69.0"
        assert c.normalize_floats(want, got, flags=doctest.ELLIPSIS | FLOAT_CMP)

        got = "\n" + got
        want = "<BLANKLINE>\nA 65.0\nB 66.0\n..."
        assert c.normalize_floats(want, got, flags=doctest.ELLIPSIS | FLOAT_CMP)

    def test_partial_match(self):
        c = OutputChecker()

        assert not c.partial_match(["1", "2", "3", "4"], [["2"], []],)
        assert c.partial_match(["1", "2", "3", "4"], [[], ["2"], []],)
        assert c.partial_match(["1", "2", "3", "4"], [["1", "2"], []],)
        assert c.partial_match(["1", "2", "3", "4"], [["1", "2"], ["4"]],)
        assert c.partial_match(["1", "2", "3", "4", "5"], [["1", "2"], ["4", "5"]],)
        assert c.partial_match(
            ["1", "2", "3", "4", "5", "6"], [["1", "2"], ["4"], ["6"]],
        )
        assert c.partial_match(
            [str(i) for i in range(20)], [[], ["1", "2"], ["4"], ["6"], []],
        )
        assert not c.partial_match(
            [str(i) for i in range(20)], [[], ["1", "2"], ["7"], ["6"], []],
        )
