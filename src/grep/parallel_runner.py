import concurrent.futures
from dataclasses import dataclass, field
from typing import Any, List

from src.grep.interface import _search_single_file_worker


@dataclass
class ParallelResult:
    """並列処理の結果を保持する構造体"""

    results: List[Any] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def _worker_wrapper(args):
    file_path, pattern, flag1, flag2 = args
    return _search_single_file_worker(file_path, pattern, flag1, flag2)


def run_parallel(
    file_paths: list[str],
    pattern: str,
    max_workers: int = None,
) -> List[Any]:
    """
    複数ファイルを 並列でパース・検索 します。

    Args:
        file_paths: 処理 するファイルのリスト
        pattern: 検索文字列 (正規除非はパターン として扱う)
        max_workers: 並列数 (未指定時は CPU コア数 を 使用)

    Returns:
        List[Any]: 全ての ファイルからの 結果 の 合成
    """

    # max_workers は None の時、Executor が 自動で 適切な 値 を 設定 します。
    executor = concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)
    results = []

    try:
        args_list = [(f, pattern, True, False) for f in file_paths]
        for result in executor.map(_worker_wrapper, args_list):
            if isinstance(result, list):
                results.extend(result)
    finally:
        executor.shutdown()

    return results
