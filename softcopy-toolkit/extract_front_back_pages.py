#!/usr/bin/env python3
"""Extract the first N and last M pages from a PDF without duplicating overlap."""

from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader, PdfWriter

import re

PAGE_MARKER = re.compile(r"第\s*\d+\s*页")


def detect_cover_pages(reader: PdfReader) -> int:
    """Return the count of leading pages without a '第 N 页' marker.

    Used only with ``--auto-cover`` to build a preview copy.  Deposited PDFs
    produced by easybook carry a printed page marker on every content page;
    leading pages without it are cover/front matter.  The official deposit
    should NOT include the cover, so this is opt-in.
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
        description="Extract front/back pages from a PDF while keeping cover/TOC at the beginning."
    )
    parser.add_argument("input_pdf", type=Path, help="Input PDF")
    parser.add_argument("output_pdf", type=Path, nargs="?", help="Output PDF")
    parser.add_argument("--front-pages", type=int, default=30, help="Pages kept from the start")
    parser.add_argument("--back-pages", type=int, default=30, help="Pages kept from the end")
    parser.add_argument(
        "--cover-pages",
        type=int,
        default=0,
        help="Leading cover/title pages kept but not counted toward --front-pages (default 0).",
    )
    parser.add_argument(
        "--auto-cover",
        action="store_true",
        help="Auto-detect leading cover/TOC pages and keep them. This produces a "
             "preview copy with cover + 60 content pages; the official deposit "
             "should use exactly the front/back page counts without the cover.",
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
    if args.cover_pages:
        cover_pages = min(max(args.cover_pages, 0), total_pages)
    elif args.auto_cover:
        cover_pages = detect_cover_pages(reader)
    else:
        cover_pages = 0
    cover_pages = min(cover_pages, total_pages)
    available = total_pages - cover_pages
    front_end = cover_pages + min(max(args.front_pages, 0), available)
    back_start = max(total_pages - max(args.back_pages, 0) + 1, front_end + 1)

    pages = list(range(1, front_end + 1))
    pages.extend(range(back_start, total_pages + 1))

    if not pages:
        raise SystemExit("No pages selected")

    writer = PdfWriter()
    for page in pages:
        writer.add_page(reader.pages[page - 1])

    with output_pdf.open("wb") as handle:
        writer.write(handle)

    output_pages = len(writer.pages)
    print(f"Input PDF: {input_pdf}")
    print(f"Total pages: {total_pages}")
    print(f"Cover pages kept: {cover_pages} (not counted toward front-pages)")
    print(f"Extracted pages: {output_pages}")
    print(f"Output PDF: {output_pdf}")


if __name__ == "__main__":
    main()
