from __future__ import annotations

import pytest

from src.utils.error_handler import format_error_summary


def test_format_error_summary_normal_exception() -> None:
    """通常例外が '<ClassName>: <message>' 形式で返ること。"""
    exc = ValueError("sample message")
    assert format_error_summary(exc) == "ValueError: sample message"


def test_format_error_summary_normalizes_whitespace() -> None:
    """改行・タブ・連続空白が単一スペースに正規化されること。"""
    exc = ValueError("line1\n  line2\t\tline3  ")
    assert format_error_summary(exc) == "ValueError: line1 line2 line3"


def test_format_error_summary_empty_message() -> None:
    """メッセージが空または空白のみの例外では例外クラス名のみが返ること。"""
    assert format_error_summary(RuntimeError()) == "RuntimeError"
    assert format_error_summary(ValueError("")) == "ValueError"
    assert format_error_summary(ValueError("  \n\t ")) == "ValueError"


def test_format_error_summary_truncation_boundary_and_ellipsis() -> None:
    """max_length 境界値および超過時の '...' 丸めが正しく動作すること。"""
    exc = ValueError("1234567890")
    full_summary = "ValueError: 1234567890"
    exact_len = len(full_summary)

    # ちょうど max_length と一致する場合は省略されない
    assert format_error_summary(exc, max_length=exact_len) == full_summary

    # 1文字でも超過する場合は末尾に '...' を付けて max_length に収める
    truncated = format_error_summary(exc, max_length=exact_len - 1)
    assert len(truncated) == exact_len - 1
    assert truncated.endswith("...")
    assert truncated == f"{full_summary[: exact_len - 4]}..."


def test_format_error_summary_default_max_length_200() -> None:
    """デフォルトの max_length=200 を超えるメッセージが 200 文字に丸められること。"""
    exc = RuntimeError("a" * 250)
    summary = format_error_summary(exc)
    assert len(summary) == 200
    assert summary.endswith("...")


@pytest.mark.parametrize("max_length", [1, 2, 3])
def test_format_error_summary_small_positive_max_length(max_length: int) -> None:
    """1 <= max_length <= 3 の場合は '...' を付けず安全に切り詰められること。"""
    exc = ValueError("sample message")
    summary = format_error_summary(exc, max_length=max_length)
    assert len(summary) <= max_length
    assert summary == "ValueError: sample message"[:max_length]


@pytest.mark.parametrize("invalid_max_length", [0, -1, -5])
def test_format_error_summary_invalid_max_length_raises_value_error(invalid_max_length: int) -> None:
    """max_length <= 0 の場合に ValueError が送出されること。"""
    with pytest.raises(ValueError):
        format_error_summary(ValueError("test"), max_length=invalid_max_length)
