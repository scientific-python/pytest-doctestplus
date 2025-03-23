from textwrap import dedent

import pytest

pytest_plugins = ["pytester"]


@pytest.mark.parametrize("encoding", ["utf-8", "cp1252"])
def test_file_encoding(testdir, capsys, encoding):
    p = testdir.makepyfile(
        """
        def f():
            '''
            >>> print(2)
            4
            >>> print(3)
            5
            '''
            pass
        """
    )
    with open(p) as f:
        original = f.read()

    testdir.inline_run(
        p, "--doctest-plus-generate-diff", "--text-file-encoding", encoding
    )
    diff = dedent(
        """
         >>> print(2)
    -    4
    +    2
         >>> print(3)
    -    5
    +    3
    """
    )
    captured = capsys.readouterr()
    assert diff in captured.out

    testdir.inline_run(
        p, "--doctest-plus-generate-diff=overwrite", "--text-file-encoding", encoding
    )
    captured = capsys.readouterr()
    assert "Applied fix to the following files" in captured.out

    with open(p) as f:
        result = f.read()

    assert result == original.replace("4", "2").replace("5", "3")


@pytest.mark.parametrize("encoding", ["utf-8"])
def test_file_encoding_utf8(testdir, capsys, encoding):
    p = testdir.makepyfile(
        """
        def f():
            '''
            >>> print(☆)
            ★
            >>> print(☁)
            ☀
            '''
            pass
        """,
        encoding=encoding,
    )
    with open(p, encoding=encoding) as f:
        original = f.read()

    testdir.inline_run(
        p, "--doctest-plus-generate-diff=diff", "--text-file-encoding", encoding
    )
    diff = dedent(
        """
         >>> print(☆)
    -    ★
    +    ☆
         >>> print(☁)
    -    ☀
    +    ☁
    """
    )
    captured = capsys.readouterr()
    assert diff in captured.out

    testdir.inline_run(
        p, "--doctest-plus-generate-diff=overwrite", "--text-file-encoding", encoding
    )
    captured = capsys.readouterr()
    assert "Applied fix to the following files" in captured.out

    with open(p, encoding=encoding) as f:
        result = f.read()

    assert result == original.replace("★", "☆").replace("☀", "☁")
