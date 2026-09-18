from src.utils.file_utils import format_file_size, is_safe_path


class TestIsSafePath:
    """is_safe_path の単体テスト"""

    def test_normal_child_path(self, tmp_path):
        """配下の通常パスは安全と判定される"""
        assert is_safe_path(str(tmp_path), str(tmp_path / "file.txt")) is True

    def test_relative_path_inside(self, tmp_path):
        """base_dir からの相対パスは安全と判定される"""
        assert is_safe_path(str(tmp_path), "file.txt") is True

    def test_subdirectory_path(self, tmp_path):
        """サブディレクトリ内のパスは安全と判定される"""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        assert is_safe_path(str(tmp_path), str(subdir / "file.txt")) is True

    def test_parent_directory_traversal(self, tmp_path):
        """../ による親ディレクトリ参照は不安全と判定される"""
        outside = tmp_path / ".." / "outside.txt"
        assert is_safe_path(str(tmp_path), str(outside)) is False

    def test_absolute_path_outside(self, tmp_path):
        """絶対パスによる外部参照は不安全と判定される"""
        assert is_safe_path(str(tmp_path), "/absolute/path/outside") is False

    def test_null_byte(self, tmp_path):
        """NULLバイトを含むパスは不安全と判定される"""
        target = str(tmp_path) + "\x00file"
        assert is_safe_path(str(tmp_path), target) is False


class TestFormatFileSize:
    """format_file_size の単体テスト"""

    def test_zero(self):
        """0 は "0 B" を返す"""
        assert format_file_size(0) == "0 B"

    def test_negative(self):
        """負の値は "0 B" を返す"""
        assert format_file_size(-100) == "0 B"

    def test_bytes(self):
        """1023 は "1023.0 B" を返す"""
        assert format_file_size(1023) == "1023.0 B"

    def test_kilobytes(self):
        """1024 は "1.0 KB" を返す"""
        assert format_file_size(1024) == "1.0 KB"

    def test_megabytes(self):
        """1048576 は "1.0 MB" を返す"""
        assert format_file_size(1048576) == "1.0 MB"

    def test_gigabytes(self):
        """1073741824 は "1.0 GB" を返す"""
        assert format_file_size(1073741824) == "1.0 GB"
