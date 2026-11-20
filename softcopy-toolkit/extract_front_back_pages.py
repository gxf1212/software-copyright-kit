#!/usr/bin/env python3
"""Extract the first N and last M pages of source text from a PDF.

The leading cover has no printed page marker, so it is detected and excluded
by default: it is not source text and must not consume the 30-page quota.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader, PdfWriter

import re

# easybook numbers body pages in Arabic and TOC pages in roman numerals.
# Only Arabic markers count as the start of the deposited text.
PAGE_MARKER = re.compile(r"第\s*\d+\s*页")


def detect_cover_pages(reader: PdfReader) -> int:
    """Return the count of leading front-matter pages before the body.

    easybook PDFs print Arabic page numbers in the body and roman ones in the
    table of contents. The cover and the whole TOC are front matter: they are
    excluded from the deposit by default and do not consume the page quota.
    ``--keep-cover`` retains them without counting them toward the quota.
    """
    count = 0
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:
            break
        if PAGE_MARKER.search(text):
            break
        count += 1
        if count >= 10:  # safety cap: never treat more than 10 leading pages as cover
            break
    return count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract the first N and last M source pages; the cover is excluded by default."
    )
    parser.add_argument("input_pdf", type=Path, help="Input PDF")
    parser.add_argument("output_pdf", type=Path, nargs="?", help="Output PDF")
    parser.add_argument(
        "--front-pages", type=int, default=30,
        help="Consecutive pages kept after the cover (default 30).",
    )
    parser.add_argument("--back-pages", type=int, default=30, help="Pages kept from the end (default 30)")
    parser.add_argument(
        "--cover-pages", type=int, default=None,
        help="Manually set the number of leading cover pages to skip (default: auto-detect).",
    )
    parser.add_argument(
        "--keep-cover", "--auto-cover", dest="keep_cover", action="store_true",
        help="Keep the cover in the output without counting it toward --front-pages "
             "(preview only; the official deposit excludes it).",
    )
    parser.add_argument(
        "--no-auto-cover", action="store_true",
        help="Disable cover detection and count from physical page 1 "
             "(use when the PDF already has no cover).",
    )
    args = parser.parse_args()

    input_pdf = args.input_pdf
    if not input_pdf.exists():
        raise SystemExit(f"Input PDF not found: {input_pdf}")

    output_pdf = args.output_pdf
    if output_pdf is None:
        output_pdf = input_pdf.with_name(
            f"{input_pdf.stem}_front{args.front_pages}_back{args.back_pages}{input_pdf.suffix}"
        )

    reader = PdfReader(str(input_pdf))
    total_pages = len(reader.pages)
    if args.no_auto_cover:
        cover_pages = 0
    elif args.cover_pages is not None:
        cover_pages = min(max(args.cover_pages, 0), total_pages)
    else:
        cover_pages = detect_cover_pages(reader)
    cover_pages = min(cover_pages, total_pages)
    available = total_pages - cover_pages
    front_start = cover_pages + 1
    front_end = cover_pages + min(max(args.front_pages, 0), available)
    back_start = max(total_pages - max(args.back_pages, 0) + 1, front_end + 1)

    pages = list(range(front_start, front_end + 1))
    pages.extend(range(back_start, total_pages + 1))
    if args.keep_cover:
        pages = list(range(1, cover_pages + 1)) + pages

    if not pages:
        raise SystemExit("No pages selected")

    writer = PdfWriter()
    for page in pages:
        writer.add_page(reader.pages[page - 1])

    with output_pdf.open("wb") as handle:
        writer.write(handle)

    output_pages = len(writer.pages)
    cover_state = "kept" if args.keep_cover else "excluded"
    print(f"Input PDF: {input_pdf}")
    print(f"Total pages: {total_pages}")
    print(f"Cover pages: {cover_pages} ({cover_state}; not counted toward front-pages)")
    print(f"Extracted pages: {output_pages}")
    print(f"Output PDF: {output_pdf}")


if __name__ == "__main__":
    main()
