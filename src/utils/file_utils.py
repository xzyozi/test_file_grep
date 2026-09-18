from pathlib import Path


def is_safe_path(base_dir: str, target_path: str) -> bool:
    """
    target_path が base_dir の内部または配下に安全に収まっているかを判定する。

    ../ や絶対パスによるディレクトリ外参照、NULLバイト（\x00）が含まれる場合は False を返す。
    """
    # NULLバイトが含まれる場合は不正と判定する
    if "\x00" in target_path:
        return False

    base_path = Path(base_dir).resolve()
    target_path_obj = Path(target_path)
    if target_path_obj.is_absolute():
        target_resolved = target_path_obj.resolve()
    else:
        target_resolved = (base_path / target_path_obj).resolve()

    return target_resolved.is_relative_to(base_path)


def format_file_size(size_bytes: int) -> str:
    """
    バイト数を "B", "KB", "MB", "GB" の単位でフォーマットする。

    例:
        0 -> "0 B"
        1024 -> "1.0 KB"
        1048576 -> "1.0 MB"
    負の値の場合は "0 B" を返す。
    """
    if size_bytes < 0:
        return "0 B"

    if size_bytes == 0:
        return "0 B"

    units = [(1024**3, "GB"), (1024**2, "MB"), (1024**1, "KB"), (1, "B")]
    for unit_value, unit_name in units:
        if size_bytes >= unit_value:
            return f"{size_bytes / unit_value:.1f} {unit_name}"

    return f"{size_bytes:.1f} B"
