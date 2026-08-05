from __future__ import annotations

import re
from typing import TYPE_CHECKING, Callable, List, Optional, Protocol

if TYPE_CHECKING:
    from src.grep.engine import GrepResult


def _search_single_file_worker(
    file_path: str,
    search_text: str,
    regex_mode: bool,
    ignore_case: bool,
    Pattern: Optional[re.Pattern] = None,
) -> List[GrepResult]:
    """
    ProcessPoolExecutor で使用 するための トップレベルワーカー。
    クラスメソッド を 直接 呼べば pickled エラー が 防げます。
    """
    from src.grep.engine import GrepEngine

    engine = GrepEngine()
    return engine._scan_file(file_path, search_text, regex_mode, ignore_case, Pattern)


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
