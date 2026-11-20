#!/usr/bin/env python3
"""Check visible text-row counts in software-copyright PDF materials.

The checker uses Poppler's ``pdftotext -layout`` output.  It measures printed
non-empty text rows, not semantic source statements.  This makes it useful for
finding sparse pages after typesetting, while the final submission still needs
a visual review for figures, long-line wrapping, and exceptional deposit rules.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


PAGE_MARKER = re.compile(r"第\s*\d+\s*页")
PURE_PAGE_NUMBER = re.compile(r"^(?:第\s*)?\d+(?:\s*页)?$")


@dataclass(frozen=True)
class PageResult:
    physical_page: int
    printed_page: int | None
    line_count: int
    minimum: int
    exempt: bool
    passed: bool


def extract_pages(pdf_path: Path) -> list[str]:
    """Extract pages with layout preserved using pdftotext."""
    if shutil.which("pdftotext") is None:
        raise RuntimeError("pdftotext was not found; install poppler-utils")
    process = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    pages = process.stdout.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


def printed_page_number(page_text: str) -> int | None:
    """Return a Chinese printed-page marker found near the page top."""
    top_lines = [line for line in page_text.splitlines() if line.strip()][:1]
    for line in top_lines:
        match = PAGE_MARKER.search(line)
        if match:
            digits = re.search(r"\d+", match.group())
            return int(digits.group()) if digits else None
    return None


def count_visible_rows(page_text: str) -> int:
    """Count non-empty printed rows, excluding page headers and page numbers."""
    count = 0
    non_empty_index = 0
    for raw_line in page_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        non_empty_index += 1
        if non_empty_index == 1 and PAGE_MARKER.search(line):
            continue
        if PURE_PAGE_NUMBER.fullmatch(line):
            continue
        count += 1
    return count


def parse_page_spec(spec: str) -> set[int]:
    """Parse one-based physical page ranges such as ``1,3-5``."""
    pages: set[int] = set()
    if not spec:
        return pages
    for part in spec.split(","):
        item = part.strip()
        if not item:
            continue
        if "-" in item:
            start_text, end_text = item.split("-", 1)
            start, end = int(start_text), int(end_text)
            if start < 1 or end < start:
                raise ValueError(f"invalid page range: {item}")
            pages.update(range(start, end + 1))
        else:
            page = int(item)
            if page < 1:
                raise ValueError(f"invalid page number: {item}")
            pages.add(page)
    return pages


def content_page_indices(pages: Sequence[str], marker_mode: str) -> list[int]:
    """Choose content-page indices, optionally using printed-page markers."""
    marked = [index for index, text in enumerate(pages) if printed_page_number(text) is not None]
    if marker_mode == "required":
        if not marked:
            raise ValueError("no '第 N 页' markers found in the PDF")
        return marked
    if marker_mode == "auto" and marked:
        return marked
    return list(range(len(pages)))


def deposit_scope(indices: Sequence[int]) -> list[int]:
    """Apply the ordinary first/last 30-page deposit rule."""
    if len(indices) <= 60:
        return list(indices)
    return list(indices[:30]) + list(indices[-30:])


def check_pages(
    pages: Sequence[str],
    minimum: int,
    scope: str,
    marker_mode: str,
    exempt_pages: Iterable[int] = (),
    allow_short_last: bool = False,
) -> list[PageResult]:
    """Evaluate selected PDF pages and return structured results."""
    indices = content_page_indices(pages, marker_mode)
    if scope == "deposit":
        indices = deposit_scope(indices)
    exempt = set(exempt_pages)
    if allow_short_last and indices:
        exempt.add(indices[-1] + 1)

    results = []
    for index in indices:
        physical_page = index + 1
        line_count = count_visible_rows(pages[index])
        is_exempt = physical_page in exempt
        results.append(
            PageResult(
                physical_page=physical_page,
                printed_page=printed_page_number(pages[index]),
                line_count=line_count,
                minimum=minimum,
                exempt=is_exempt,
                passed=is_exempt or line_count >= minimum,
            )
        )
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check per-page visible line counts in software-copyright PDFs."
    )
    parser.add_argument("pdf", type=Path, help="PDF file to inspect")
    parser.add_argument(
        "--kind", choices=("source", "document"), default="source",
        help="source defaults to 50 rows; document defaults to 30",
    )
    parser.add_argument("--min-lines", type=int, help="override the default threshold")
    parser.add_argument(
        "--scope", choices=("all", "deposit"), default="all",
        help="all content pages, or ordinary first/last 30-page deposit scope",
    )
    parser.add_argument(
        "--page-markers", choices=("auto", "required", "off"), default="auto",
        help="use '第 N 页' headers to exclude cover/front matter",
    )
    parser.add_argument(
        "--exempt-pages", default="",
        help="comma-separated one-based physical pages/ranges, e.g. 1,8-10",
    )
    parser.add_argument(
        "--allow-short-last", action="store_true",
        help="exempt the last checked content page (use only when applicable)",
    )
    parser.add_argument("--json", dest="json_path", type=Path, help="write a JSON report")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.pdf.is_file():
        print(f"ERROR: PDF not found: {args.pdf}", file=sys.stderr)
        return 2
    minimum = args.min_lines if args.min_lines is not None else (50 if args.kind == "source" else 30)
    if minimum < 1:
        print("ERROR: --min-lines must be positive", file=sys.stderr)
        return 2

    try:
        pages = extract_pages(args.pdf)
        results = check_pages(
            pages,
            minimum=minimum,
            scope=args.scope,
            marker_mode=args.page_markers,
            exempt_pages=parse_page_spec(args.exempt_pages),
            allow_short_last=args.allow_short_last,
        )
    except (OSError, subprocess.CalledProcessError, RuntimeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    failures = [result for result in results if not result.passed]
    print(f"PDF: {args.pdf}")
    print(
        f"Kind: {args.kind} | scope: {args.scope} | minimum: {minimum} | "
        f"checked: {len(results)} | failed: {len(failures)}"
    )
    print("physical  printed  rows  status")
    for result in results:
        printed = "-" if result.printed_page is None else str(result.printed_page)
        status = "EXEMPT" if result.exempt else ("PASS" if result.passed else "FAIL")
        print(f"{result.physical_page:>8}  {printed:>7}  {result.line_count:>4}  {status}")

    if args.json_path:
        report = {
            "pdf": str(args.pdf),
            "kind": args.kind,
            "scope": args.scope,
            "minimum": minimum,
            "checked": len(results),
            "failed": len(failures),
            "pages": [asdict(result) for result in results],
        }
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
