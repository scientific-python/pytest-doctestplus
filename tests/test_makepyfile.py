import os
from encodings.aliases import aliases
from pathlib import Path
from textwrap import dedent
from typing import Tuple

import pytest

pytest_plugins = ["pytester"]


def not_debug():
    """run tests only when not in CI and debug is enabled."""
    return os.getenv("CI", False) or not os.getenv("PYTEST_DEBUG_MAKEPYFILE", False)


def enc(enc):
    try:
        _ = "abc".encode(enc)
    except LookupError:
        return False

    return True


all_encodings = set(filter(enc, aliases.values()))


@pytest.fixture(params=all_encodings)
def encoding(request):
    return request.param


@pytest.fixture(
    params=[
        ("3", "4"),
        ("A", "B"),
        ("!", "?"),
        ("☆", "☁"),
        ("✅", "💥"),
        ("é", "ü"),
        ("Я", "ж"),  # Cyrillic characters
        ("Ф", "Щ"),  # More Cyrillic
        ("中", "国"),  # Chinese characters (zhong guo - China)
        ("道", "德"),  # Chinese characters (dao de - way virtue)
    ],
    ids=[
        "numbers",
        "letters",
        "punctuation",
        "stars",
        "check-explosion",
        "accented_letters",
        "cyrillic_basic",
        "cyrillic_complex",
        "chinese_country",
        "chinese_concept",
    ],
)
def any_charset(request):
    return request.param


@pytest.fixture
def makepyfile_encoded(testdir, encoding, any_charset):
    a, b = any_charset

    original_file = testdir.makepyfile(
        f"""
        def f():
            '''
            >>> print('{a}')
            {b}
            '''
            pass
        """,
        encoding=encoding,
    )

    expected_diff = dedent(
        f"""
             >>> print('{a}')
        -    {b}
        +    {a}
        """
    ).strip("\n")

    yield original_file, expected_diff, encoding


def makebasicfile(tmp_path: Path, a, b, encoding: str) -> Tuple[Path, str]:
    """alternative implementation without the use of `testdir.makepyfile`."""

    original_file = Path(tmp_path).joinpath("test_basic.py")
    code = dedent(
        f"""
        def f():
            '''
            >>> print('{a}')
            {b}
            '''
            pass
        """
    )

    original_file.write_text(code, encoding=encoding)

    expected_diff = dedent(
        f"""
             >>> print('{a}')
        -    {b}
        +    {a}
        """
    ).strip("\n")

    return original_file, expected_diff


@pytest.fixture
def basic_encoded(tmp_path, encoding, any_charset):

    a, b = any_charset

    file, diff = makebasicfile(tmp_path, a, b, encoding)

    yield file, diff, encoding


@pytest.mark.skipif(not_debug(), reason="running in CI or debugging is not enabled.")
def test_makepyfile(makepyfile_encoded):
    """
    Test is expected to fail because of UnicodeDecodeError.

    Just to compare visually with `test_basicfile` to see the difference
    """

    file, diff, enc = makepyfile_encoded

    text = Path(file).read_text(enc)

    print(text, diff)


@pytest.mark.skipif(not_debug(), reason="running in CI or debugging is not enabled.")
def test_basicfile(basic_encoded):
    """
    Test is expected to fail because of UnicodeDecodeError.

    Just to compare visually with `test_makepyfile` to see the difference
    """
    file, diff, enc = basic_encoded

    text = Path(file).read_text(enc)

    print(text, diff)


def test_compare_make_basic_file(testdir, encoding, any_charset):
    """
    Compare testdir.makepyfile with pathlib.Path.writetext to create python files.

    Expected behavior is when `testdir.makepyfile` created a file with given encoding,
    `makebasicfile` also should be able to encode the charset.

    If a UnicodeEncodeError is raised, it means `testdir.makepyfile` screwed up the
    encoding.
    """

    a, b = any_charset

    # create a python file with testdir.makepyfile in the old fashioned way

    make_file = testdir.makepyfile(
        f"""
        def f():
            '''
            >>> print('{a}')
            {b}
            '''
            pass
        """,
        encoding=encoding,
    )

    assert Path(
        make_file
    ).is_file(), f"`testdir.makepyfile` failed encode {repr((a,b))} with {encoding=}"

    make_diff = dedent(
        f"""
             >>> print('{a}')
        -    {b}
        +    {a}
        """
    ).strip("\n")

    # try to check if makepyfile screwed up and create python file in a different way

    try:
        basic_file, basic_diff = makebasicfile(str(testdir), a, b, encoding)
    except UnicodeEncodeError:
        pytest.fail(
            f"testdir.makepyfile encoding {repr((a,b))} with {encoding=}, but it sould have failed."
        )

    assert Path(
        basic_file
    ).is_file(), f"`makebasicfile` failed encode {repr((a,b))} with {encoding=}"
    assert (
        make_diff == basic_diff
    ), "sanity check - diffs always should be the same, if not my test implementation is wrong."
