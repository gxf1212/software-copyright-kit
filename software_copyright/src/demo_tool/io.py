"""Input and output helpers for delimiter-separated text files."""

from __future__ import annotations

import csv
from pathlib import Path

ENCODING_CANDIDATES = ("utf-8-sig", "utf-8", "gb18030")


def detect_encoding(path: str | Path) -> str:
    """Return the first encoding that decodes the whole file."""
    target = Path(path)
    for encoding in ENCODING_CANDIDATES:
        try:
            target.read_text(encoding=encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    raise ValueError(f"cannot decode {target} with any candidate encoding")


def read_rows(path: str | Path) -> tuple[list[str], list[list[str]]]:
    """Read a CSV file and return its header and data rows."""
    target = Path(path)
    with target.open(encoding=detect_encoding(target), newline="") as handle:
        reader = csv.reader(handle)
        rows = [row for row in reader if row]
    if not rows:
        return [], []
    return rows[0], rows[1:]


def write_rows(path: str | Path, header: list[str], rows: list[list[str]]) -> int:
    """Write header and rows to a CSV file, returning the number of data rows."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)
    return len(rows)
