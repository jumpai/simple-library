"""Utility helpers."""

from __future__ import annotations

from typing import Iterable, List, Sequence


def normalize_isbn(value: str) -> str:
    """Normalize an ISBN by stripping separators and upper-casing."""
    return "".join(ch for ch in value if ch.isalnum()).upper()


def chunked(iterable: Sequence, size: int) -> List[Sequence]:
    """Split a sequence into chunks of the given size."""
    if size <= 0:
        raise ValueError("size must be positive")
    return [iterable[i : i + size] for i in range(0, len(iterable), size)]


def tabulate(rows: Iterable[Sequence[str]], headers: Sequence[str]) -> str:
    """Render a simple table for CLI output."""
    rows = list(rows)
    widths = [len(str(h)) for h in headers]
    for row in rows:
        for idx, value in enumerate(row):
            widths[idx] = max(widths[idx], len(str(value)))

    def fmt_line(values):
        return " | ".join(str(v).ljust(widths[i]) for i, v in enumerate(values))

    lines = [fmt_line(headers), "-+-".join("-" * w for w in widths)]
    lines.extend(fmt_line(row) for row in rows)
    return "\n".join(lines)
