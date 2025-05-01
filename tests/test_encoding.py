import locale
import os
from pathlib import Path
from textwrap import dedent
from typing import Callable, Optional

import pytest

pytest_plugins = ["pytester"]
IS_CI = os.getenv("CI", "false") == "true"


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
def basic_file(tmp_path: Path) -> Callable[[str, str, str], tuple[str, str, str]]:

    def makebasicfile(a, b, encoding: str) -> tuple[str, str, str]:
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


@pytest.fixture()
def ini_file(testdir) -> Callable[..., Path]:

    def makeini(
        encoding: Optional[str] = None,
    ) -> Path:
        """Create a pytest.ini file with the specified encoding."""

        ini = ["[pytest]"]

        if encoding is not None:
            ini.append(f"doctest_encoding = {encoding}")

        ini.append("")

        p = testdir.makefile(".ini", pytest="\n".join(ini))

        return Path(p)

    return makeini


def test_basic_file_encoding_diff(testdir, capsys, basic_file, charset, ini_file):
    """
    Test the diff from console output is as expected.
    """
    a, b, encoding = charset

    # create python file to test
    file, diff, _ = basic_file(a, b, encoding)

    # create pytest.ini file
    ini = ini_file(encoding=encoding)
    assert ini.is_file(), "setup pytest.ini not created/found"

    testdir.inline_run(
        file,
        "--doctest-plus-generate-diff",
        "-c",
        str(ini),
    )

    stdout, _ = capsys.readouterr()
    assert diff in stdout


def test_basic_file_encoding_overwrite(testdir, basic_file, charset, ini_file):
    """
    Test that the file is overwritten with the expected content.
    """

    a, b, encoding = charset

    # create python file to test
    file, _, expected = basic_file(a, b, encoding)

    # create pytest.ini file
    ini = ini_file(encoding=encoding)
    assert ini.is_file(), "setup pytest.ini not created/found"

    testdir.inline_run(
        file,
        "--doctest-plus-generate-diff",
        "overwrite",
        "-c",
        str(ini),
    )

    assert expected in Path(file).read_text(encoding)


@pytest.mark.skipif(IS_CI, reason="skip on CI")
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


@pytest.mark.skipif(IS_CI, reason="skip on CI")
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
