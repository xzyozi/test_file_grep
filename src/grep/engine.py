import concurrent.futures
from dataclasses import dataclass, field
import os
import re
import threading
from typing import Any, Callable, Dict, List, Optional

from src.grep.office_parser import OfficeParser


@dataclass
class GrepResult:
    """Grep検索の単一ヒット結果を保持するデータクラス"""

    file_path: str
    line_content: str
    line_number: int = 0  # 従来の行番号
    location_display: str = ""  # GUI表示用の位置情報 (例: "Sheet1!A5")
    metadata: Dict[str, Any] = field(default_factory=dict)  # 拡張用メタデータ


class GrepEngine:
    """
    外部モジュールに依存せず、Python標準ライブラリのみで構成されたGrepエンジンクラス。
    マルチスレッドによる並列スキャンと、効率的な文字コード推測をサポートします。
    """

    # 走査から完全に除外するバイナリ拡張子
    # ※ Officeファイル(.docx, .xlsx)は OfficeParser で別途処理するため、ここには含めない
    BINARY_EXTENSIONS = {
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".bin",
        ".dat",
        ".pyc",
        ".pyo",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".ico",
        ".pdf",
        ".zip",
        ".tar",
        ".gz",
        ".rar",
        ".7z",
        ".class",
        ".obj",
        ".o",
    }

    # 試行する文字コード（テキストファイル用）
    ENCODINGS = ["utf-8", "cp932", "shift_jis", "euc_jp", "iso-2022-jp", "utf-16"]

    def __init__(self, max_threads: int = 4):
        self.max_threads = max_threads
        self._stop_event = threading.Event()

    def stop(self) -> None:
        """検索を中断します。スレッドセーフにイベントを発行します。"""
        self._stop_event.set()

    def search(
        self,
        target_dir: str,
        search_text: str,
        regex_mode: bool = False,
        ignore_case: bool = False,
        whole_word: bool = False,
        exclude_dirs: Optional[List[str]] = None,
        on_progress: Optional[Callable[[int, int], None]] = None,
        on_result: Optional[Callable[[GrepResult], None]] = None,
        on_complete: Optional[Callable[[int], None]] = None,
    ) -> int:
        """
        指定されたディレクトリ内を再帰的に検索します。

        Args:
            target_dir: 検索対象ディレクトリ
            search_text: 検索文字列（または正規表現パターン）
            regex_mode: 正規表現として扱うかどうか
            ignore_case: 大文字小文字を区別しない
            whole_word: 単語単位で検索する
            exclude_dirs: 除外するディレクトリ名のリスト (例: ['.git', 'node_modules'])
            on_progress: (完了ファイル数, 総ファイル数) を通知するコールバック
            on_result: ヒットした GrepResult を通知するコールバック
            on_complete: 合計ヒット数を通知するコールバック

        Returns:
            int: 合計ヒット数
        """
        # 前回の停止状態をクリアし、常に新しく開始できるようにする
        self._stop_event.clear()

        hit_count = 0
        all_files = self._collect_files(target_dir, exclude_dirs)
        total_files = len(all_files)

        # 正規表現パターンの事前コンパイル
        pattern = None
        re_flags = re.IGNORECASE if ignore_case else 0
        actual_search_text = search_text

        if whole_word and not regex_mode:
            # 単語単位(非正規表現)の場合は、正規表現の \b を使うために内部的に正規表現化する
            actual_search_text = r"\b" + re.escape(search_text) + r"\b"
            regex_mode = True

        if regex_mode:
            try:
                # 単語単位かつ正規表現の場合は、ユーザーのパターンを \b で囲む
                final_pattern = (
                    r"\b" + actual_search_text + r"\b"
                    if (whole_word and not actual_search_text.startswith(r"\b"))
                    else actual_search_text
                )
                pattern = re.compile(final_pattern, re_flags)
            except re.error as e:
                raise ValueError(f"Invalid regular expression: {e}")

        # ignore_case かつ正規表現でない場合、search_text の小文字化をループ外で一度だけ事前計算する。
        # これにより、各行の走査ループ内で search_text.lower() を再計算する必要がなくなり、
        # 不要なオーバーヘッドを削減できる。
        lower_search_text = search_text.lower() if (ignore_case and not regex_mode) else None

        # ThreadPoolExecutorによる並列読み込み
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {
                executor.submit(
                    self._scan_file, f, actual_search_text, regex_mode, ignore_case, pattern, lower_search_text
                ): f
                for f in all_files
            }

            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                if self._stop_event.is_set():
                    # 中断時は残りのタスク完了を待たずにループを抜ける
                    break

                try:
                    results = future.result()
                    for res in results:
                        hit_count += 1
                        if on_result:
                            on_result(res)
                except Exception:
                    pass

                if on_progress:
                    on_progress(i + 1, total_files)

        if on_complete:
            on_complete(hit_count)

        return hit_count

    def _collect_files(self, target_dir: str, exclude_dirs: Optional[List[str]] = None) -> List[str]:
        """検索対象となるファイルのリストを収集します。"""
        file_list = []
        excludes = set(exclude_dirs) if exclude_dirs else set()

        for root, dirs, files in os.walk(target_dir):
            if self._stop_event.is_set():
                break

            # 除外ディレクトリのフィルタリング (in-place modification)
            if excludes:
                dirs[:] = [d for d in dirs if d not in excludes]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in self.BINARY_EXTENSIONS:
                    file_list.append(os.path.join(root, file))
        return file_list

    def _scan_file(
        self,
        file_path: str,
        search_text: str,
        regex_mode: bool,
        ignore_case: bool,
        pattern: Optional[re.Pattern] = None,
        lower_search_text: Optional[str] = None,
    ) -> List[GrepResult]:
        """単一のファイルをスキャンしてヒットした行を返します。"""
        # 中断チェック
        if self._stop_event.is_set():
            return []

        results = []
        ext = os.path.splitext(file_path)[1].lower()

        # Officeファイルの処理
        if ext in (".docx", ".docm", ".xlsx", ".xlsm"):
            office_data = OfficeParser.extract_content(file_path)
            if office_data:
                for item in office_data:
                    line = item.get("text", "")
                    location = item.get("location", "Unknown")
                    meta = item.get("metadata", {})

                    if self._check_hit(line, search_text, regex_mode, ignore_case, pattern, lower_search_text):
                        results.append(
                            GrepResult(
                                file_path=file_path,
                                line_content=line,
                                location_display=location,
                                metadata={"office_type": ext, **meta},
                            )
                        )
                return results

        # 通常のテキストファイルの処理 (メモリ効率に優れたストリーム読み込み)
        try:
            # 1. バイナリ判定 (Null Byte Check)
            with open(file_path, "rb") as f:
                header = f.read(1024)
                if b"\x00" in header:
                    return []  # バイナリと判定してスキップ

            # 2. エンコーディング試行とストリーム検索
            for enc in self.ENCODINGS:
                try:
                    with open(file_path, "r", encoding=enc, errors="strict") as f:
                        for i, line in enumerate(f, 1):
                            if self._check_hit(line, search_text, regex_mode, ignore_case, pattern, lower_search_text):
                                results.append(
                                    GrepResult(file_path=file_path, line_content=line.rstrip(), line_number=i)
                                )
                    return results  # 成功したら終了
                except (UnicodeDecodeError, LookupError):
                    continue
        except (PermissionError, OSError):
            pass

        return []

    def _check_hit(
        self,
        line: str,
        search_text: str,
        regex_mode: bool,
        ignore_case: bool,
        pattern: Optional[re.Pattern] = None,
        lower_search_text: Optional[str] = None,
    ) -> bool:
        """指定された行が検索テキストにマッチするか判定します。"""
        if regex_mode and pattern:
            return bool(pattern.search(line))

        if ignore_case:
            # ループ外で事前計算済みの小文字化文字列を使用し、search_text.lower() の再計算を回避する
            return lower_search_text in line.lower()

        return search_text in line
