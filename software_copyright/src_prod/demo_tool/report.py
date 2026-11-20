"""Summary statistics for tabular data."""
from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class ColumnSummary:
    """Basic statistics of one column."""
    name: str
    total: int
    filled: int
    distinct: int
    @property
    def missing(self) -> int:
        return self.total - self.filled
    @property
    def fill_rate(self) -> float:
        return self.filled / self.total if self.total else 0.0
def summarize(header: list[str], rows: list[list[str]]) -> list[ColumnSummary]:
    """Compute per-column completeness and cardinality."""
    result = []
    for position, name in enumerate(header):
        values = [row[position] for row in rows if position < len(row)]
        filled = [value for value in values if value.strip()]
        result.append(
            ColumnSummary(
                name=name,
                total=len(values),
                filled=len(filled),
                distinct=len(set(filled)),
            )
        )
    return result
