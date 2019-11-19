import doctest

import pytest

from pytest_doctestplus.output_checker import FLOAT_CMP, OutputChecker


class TestFloats:
    @pytest.mark.parametrize(
        "want, expected, expected_norm",
        [
            ("A 65.0\nB 66.0", True, True),
            ("A 65.0\nB   66.0  ", False, True),
            ("A 65.0\nB 66.01", False, False),
        ],
    )
    def test_normalize_floats(self, want, expected, expected_norm):
        c = OutputChecker()
        got = "A 65.0\nB 66.0"
        assert c.normalize_floats(want, got, flags=FLOAT_CMP) is expected
        flags = FLOAT_CMP | doctest.NORMALIZE_WHITESPACE
        assert c.normalize_floats(want, got, flags=flags) is expected_norm

    def test_normalize_with_blank_line(self):
        c = OutputChecker()
        got = "\nA 65.0\nB 66.0"
        want = "<BLANKLINE>\nA 65.0\nB 66.0"
        assert c.normalize_floats(want, got, flags=FLOAT_CMP)
        assert not c.normalize_floats(
            want, got, flags=FLOAT_CMP | doctest.DONT_ACCEPT_BLANKLINE
        )

    @pytest.mark.parametrize(
        "want, expected",
        [
            ("A 65.0\nB 66.0\n...G 70.0", False),
            ("A 65.0\nB 66.0\n...", True),
            ("A 65.0\nB 66.0\n...\nE 69.0", True),
        ],
    )
    def test_normalize_with_ellipsis(self, want, expected):
        c = OutputChecker()
        got = []
        for char in ["A", "B", "C", "D", "E"]:
            got.append("%s %s" % (char, float(ord(char))))
        got = "\n".join(got)

        result = c.normalize_floats(want, got, flags=doctest.ELLIPSIS | FLOAT_CMP)
        assert result is expected

    def test_normalize_with_ellipsis_with_blankline(self):
        c = OutputChecker()
        got = []
        for char in ["A", "B", "C", "D", "E"]:
            got.append("%s %s" % (char, float(ord(char))))
        got = "\n" + "\n".join(got)
        want = "<BLANKLINE>\nA 65.0\nB 66.0\n..."
        assert c.normalize_floats(want, got, flags=doctest.ELLIPSIS | FLOAT_CMP)

    @pytest.mark.parametrize(
        "array, chunks, expected",
        [
            (["1", "2", "3", "4"], [["2"], []], False),
            (["1", "2", "3", "4"], [[], ["2"], []], True),
            (["1", "2", "3", "4"], [["1", "2"], []], True),
            (["1", "2", "3", "4"], [["1", "2"], ["4"]], True),
            (["1", "2", "3", "4", "5"], [["1", "2"], ["4", "5"]], True),
            (["1", "2", "3", "4", "5", "6"], [["1", "2"], ["4"], ["6"]], True),
            ([str(i) for i in range(20)], [[], ["1", "2"], ["4"], ["6"], []], True),
            ([str(i) for i in range(20)], [[], ["1", "2"], ["7"], ["6"], []], False),
        ],
    )
    def test_partial_match(self, array, chunks, expected):
        c = OutputChecker()
        assert c.partial_match(array, chunks) is expected
