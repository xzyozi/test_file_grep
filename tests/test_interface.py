from __future__ import annotations

from pathlib import Path

import pytest

from src.grep.interface import is_valid_file_path


class TestIsValidFilePath:
    """is_valid_file_path の単体テストスイート。"""

    def test_valid_file_path_str(self, tmp_path: Path) -> None:
        """実在するファイルパス (str) の場合、True を返すこと。"""
        test_file = tmp_path / "valid.txt"
        test_file.write_text("hello", encoding="utf-8")
        assert is_valid_file_path(str(test_file)) is True

    def test_valid_file_path_path_object(self, tmp_path: Path) -> None:
        """実在するファイルパス (Path オブジェクト) の場合、True を返すこと。"""
        test_file = tmp_path / "valid.txt"
        test_file.write_text("hello", encoding="utf-8")
        assert is_valid_file_path(test_file) is True

    def test_none_returns_false(self) -> None:
        """None が渡された場合、False を返すこと。"""
        assert is_valid_file_path(None) is False

    @pytest.mark.parametrize("empty_input", ["", "   ", "\t\n  "])
    def test_empty_or_whitespace_returns_false(self, empty_input: str) -> None:
        """空文字列や空白文字のみのパスの場合、False を返すこと。"""
        assert is_valid_file_path(empty_input) is False

    def test_non_existent_file_returns_false(self, tmp_path: Path) -> None:
        """実在しないファイルパスの場合、False を返すこと。"""
        missing_file = tmp_path / "non_existent.txt"
        assert is_valid_file_path(missing_file) is False
        assert is_valid_file_path(str(missing_file)) is False

    def test_directory_path_returns_false(self, tmp_path: Path) -> None:
        """ディレクトリパスの場合（ファイルではないため）、False を返すこと。"""
        assert is_valid_file_path(tmp_path) is False
        assert is_valid_file_path(str(tmp_path)) is False

    @pytest.mark.parametrize(
        "invalid_path",
        [
            "invalid\0path.txt",
            "C:\\invalid<>path|name?.txt",
            "   \0   ",
        ],
    )
    def test_invalid_path_syntax_returns_false(self, invalid_path: str) -> None:
        """パス構文として不正な文字列でも例外を送出せず False を返すこと。"""
        assert is_valid_file_path(invalid_path) is False
