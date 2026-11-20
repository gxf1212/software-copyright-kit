"""Command-line entry point of demo_tool."""
from __future__ import annotations
import argparse
from pathlib import Path
from . import __version__
from .core import drop_empty_rows, normalize_header, select_columns, trim_cells
from .io import read_rows, write_rows
from .report import summarize
def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(prog="demo-tool", description="Lightweight data-cleaning toolkit")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    clean = sub.add_parser("clean", help="normalize a CSV file")
    clean.add_argument("input", help="input CSV path")
    clean.add_argument("output", help="output CSV path")
    clean.add_argument("--keep-empty", action="store_true", help="keep blank rows")
    select = sub.add_parser("select", help="keep selected columns")
    select.add_argument("input", help="input CSV path")
    select.add_argument("output", help="output CSV path")
    select.add_argument("--columns", nargs="+", required=True, help="columns to keep")
    report = sub.add_parser("report", help="print a completeness report")
    report.add_argument("input", help="input CSV path")
    report.add_argument("--output", help="optional CSV report path")
    return parser
def run_clean(args: argparse.Namespace) -> None:
    """Normalize headers and cell whitespace before writing output."""
    header, rows = read_rows(args.input)
    rows = trim_cells(rows)
    if not args.keep_empty:
        rows = drop_empty_rows(rows)
    write_rows(args.output, normalize_header(header), rows)
def run_select(args: argparse.Namespace) -> None:
    """Write a subset of columns to a new file."""
    header, rows = read_rows(args.input)
    write_rows(args.output, *select_columns(header, rows, args.columns))
def run_report(args: argparse.Namespace) -> None:
    """Print or save per-column statistics."""
    header, rows = read_rows(args.input)
    summaries = summarize(header, rows)
    for item in summaries:
        print(f"{item.name}: filled={item.filled}/{item.total}, distinct={item.distinct}")
    if args.output:
        write_rows(
            Path(args.output),
            ["column", "total", "filled", "distinct", "missing"],
            [[item.name, str(item.total), str(item.filled), str(item.distinct), str(item.missing)] for item in summaries],
        )
def main(argv: list[str] | None = None) -> int:
    """Dispatch to the selected subcommand."""
    args = build_parser().parse_args(argv)
    if args.command == "clean":
        run_clean(args)
    elif args.command == "select":
        run_select(args)
    elif args.command == "report":
        run_report(args)
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
