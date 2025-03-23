import locale
from pathlib import Path
from textwrap import dedent
from typing import Callable, Tuple

import pytest

pytest_plugins = ["pytester"]


@pytest.fixture(
    params=[
        ("A", "a", "utf-8"),
        ("☆", "★", "utf-8"),
        ("b", "B", "cp1252"),
        ("☁", "☀", "utf-8"),
    ],
    ids=[
        "Aa-utf8",
        "star-utf8",
        "bB-cp1252",
        "cloud-utf8",
    ],
)
def charset(request):
    return request.param


@pytest.fixture()
def basic_file(tmp_path: Path) -> Callable[[str, str, str], Tuple[Path, str, str]]:

    def makebasicfile(a, b, encoding: str) -> Tuple[str, str, str]:
        """alternative implementation without the use of `testdir.makepyfile`."""

        content = """
            def f():
                '''
                >>> print('{}')
                {}
                '''
                pass
            """

        original = dedent(content.format(a, b))
        expected_result = dedent(content.format(a, a))

        original_file = tmp_path.joinpath("test_basic.py")
        original_file.write_text(original, encoding=encoding)

        expected_diff = dedent(
            f"""
                 >>> print('{a}')
            -    {b}
            +    {a}
            """
        ).strip("\n")

        return str(original_file), expected_diff, expected_result

    return makebasicfile


def test_basic_file_encoding_diff(testdir, capsys, basic_file, charset):
    """
    Test the diff from console output is as expected.
    """
    a, b, encoding = charset

    file, diff, _ = basic_file(a, b, encoding)

    testdir.inline_run(
        file, "--doctest-plus-generate-diff", "--text-file-encoding", encoding
    )

    stdout, _ = capsys.readouterr()
    assert diff in stdout


def test_basic_file_encoding_overwrite(testdir, basic_file, charset):
    """
    Test that the file is overwritten with the expected content.
    """

    a, b, encoding = charset

    file, _, expected = basic_file(a, b, encoding)

    testdir.inline_run(
        file,
        "--doctest-plus-generate-diff",
        "overwrite",
        "--text-file-encoding",
        encoding,
    )

    assert expected in Path(file).read_text(encoding)


def test_legacy_diff(testdir, capsys, basic_file, charset):
    """
    Legacy test are supported to fail on Windows, when no encoding is provided.

    On Windows this is cp1252, so "utf-8" are expected to fail while writing test files.
    """
    a, b, _ = charset

    try:
        file, diff, _ = basic_file(a, b, None)
    except UnicodeEncodeError:
        encoding = locale.getpreferredencoding(False)
        reason = f"could not encode {repr(charset)} with {encoding=}"
        pytest.xfail(reason=reason)

    testdir.inline_run(
        file,
        "--doctest-plus-generate-diff",
    )

    stdout, _ = capsys.readouterr()

    assert diff in stdout


def test_legacy_overwrite(testdir, basic_file, charset):
    """
    Legacy test are supported to fail on Windows, when no encoding is provided.

    On Windows this is cp1252, so "utf-8" are expected to fail while writing test files.
    """

    a, b, _encoding = charset

    try:
        file, _, expected = basic_file(a, b, None)
    except UnicodeEncodeError:
        encoding = locale.getpreferredencoding(False)
        reason = f"could not encode {repr(charset)} with {encoding=}"
        pytest.xfail(reason=reason)

    testdir.inline_run(
        file,
        "--doctest-plus-generate-diff",
        "overwrite",
    )

    assert expected in Path(file).read_text(_encoding)
