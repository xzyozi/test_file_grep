from pathlib import Path


def is_safe_path(base_dir: str, target_path: str) -> bool:
    """
    Determine whether target_path is safely contained within base_dir or one of its subdirectories.

    Returns False if the path contains a NULL byte (\x00), uses ../ traversal, or is an absolute path
    pointing outside base_dir.
    """
    # Reject paths containing a NULL byte
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
    Format a byte count into a human-readable string using "B", "KB", "MB", or "GB" units.

    Examples:
        0 -> "0 B"
        1023 -> "1023 B"
        1024 -> "1.0 KB"
        1048576 -> "1.0 MB"
    Negative values return "0 B".
    """
    if size_bytes < 0:
        return "0 B"

    if size_bytes == 0:
        return "0 B"

    units = [(1024**3, "GB"), (1024**2, "MB"), (1024**1, "KB")]
    for unit_value, unit_name in units:
        if size_bytes >= unit_value:
            return f"{size_bytes / unit_value:.1f} {unit_name}"

    return f"{size_bytes} B"
