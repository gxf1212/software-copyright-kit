"""Core cleaning and transformation routines."""

from __future__ import annotations

import re
from typing import Iterable


def normalize_header(names: Iterable[str]) -> list[str]:
    """Convert column names to stable snake_case identifiers."""
    result = []
    for name in names:
        key = re.sub(r"[^0-9a-zA-Z]+", "_", name.strip().lower()).strip("_")
        result.append(key or "column")
    seen: dict[str, int] = {}
    unique = []
    for key in result:
        count = seen.get(key, 0)
        unique.append(key if count == 0 else f"{key}_{count}")
        seen[key] = count + 1
    return unique


def drop_empty_rows(rows: list[list[str]]) -> list[list[str]]:
    """Remove rows whose cells are all blank."""
    return [row for row in rows if any(cell.strip() for cell in row)]


def trim_cells(rows: list[list[str]]) -> list[list[str]]:
    """Strip leading and trailing whitespace from every cell."""
    return [[cell.strip() for cell in row] for row in rows]


def select_columns(header: list[str], rows: list[list[str]], names: list[str]) -> tuple[list[str], list[list[str]]]:
    """Keep the requested columns in the order given by names."""
    index = {name: position for position, name in enumerate(header)}
    missing = [name for name in names if name not in index]
    if missing:
        raise KeyError(f"unknown columns: {', '.join(missing)}")
    positions = [index[name] for name in names]
    return names, [[row[position] for position in positions] for row in rows]
