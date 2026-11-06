from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional, Protocol

if TYPE_CHECKING:
    from src.grep.engine import GrepResult


def is_valid_file_path(path: str | Path | None) -> bool:
    """指定されたパスが有効かつ実在するファイルパスであるかを安全に判定する。"""
    if path is None:
        return False
    if isinstance(path, str) and not path.strip():
        return False
    try:
        return Path(path).is_file()
    except (OSError, ValueError, TypeError):
        return False


class GrepEngineProtocol(Protocol):
    """
    Grepエンジンの共通インターフェース定義。
    実体(GrepEngine)とモック(MockGrepEngine)の両方で共通して使用します。
    """

    def search(
        self,
        target_dir: str,
        search_text: str,
        regex_mode: bool = False,
        on_progress: Optional[Callable[[int, int], None]] = None,
        on_result: Optional[Callable[[GrepResult], None]] = None,
        on_complete: Optional[Callable[[int], None]] = None,
    ) -> int: ...

    def stop(self) -> None: ...
