from __future__ import annotations

import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)

# UI側でエラーを表示するためのコールバック（アダプターが登録する）
_ui_error_callback: Optional[Callable[[str, str], None]] = None


def register_ui_error_callback(callback: Callable[[str, str], None]) -> None:
    """GUIアダプターが、エラーをユーザーに通知するための関数を登録します。"""
    global _ui_error_callback
    _ui_error_callback = callback


def log_and_show_error(title: str, message: str, exc_info: bool = False) -> None:
    """
    エラーをログに記録し、登録されている場合はGUIで通知します。
    GUIへの直接的な依存（messageboxなど）はありません。
    """
    logger.error(f"{title}: {message}", exc_info=exc_info)

    if _ui_error_callback:
        _ui_error_callback(title, message)
    else:
        # GUIが未登録ならコンソールへフォールバック
        print(f"--- UI ERROR [{title}] ---\n{message}\n----------------------")


def format_error_summary(exc: BaseException, max_length: int = 200) -> str:
    """例外から改行・連続空白を正規化し、最大文字数内に丸めた要約文字列を返します。"""
    if max_length < 1:
        raise ValueError("max_length must be a positive integer.")

    exc_type = type(exc).__name__
    normalized = " ".join(str(exc).split())
    summary = f"{exc_type}: {normalized}" if normalized else exc_type

    if len(summary) <= max_length:
        return summary
    if max_length <= 3:
        return summary[:max_length]
    return f"{summary[: max_length - 3]}..."
