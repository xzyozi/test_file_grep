from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional, Protocol

if TYPE_CHECKING:
    from src.grep.engine import GrepResult


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
        case_insensitive: bool = False,
        on_progress: Optional[Callable[[int, int], None]] = None,
        on_result: Optional[Callable[[GrepResult], None]] = None,
        on_complete: Optional[Callable[[int], None]] = None,
    ) -> int: ...

    def stop(self) -> None: ...
