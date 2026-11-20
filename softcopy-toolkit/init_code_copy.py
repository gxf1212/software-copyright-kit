#!/usr/bin/env python3
"""Create the source-code copy used by code_simplified.tex.

The original development source is copied into a generated directory with
empty lines removed, so the source-code PDF stays compact.  The original is
never modified.  For Python files, blank lines inside triple-quoted strings
are preserved because deleting them changes the meaning of the code.

Usage (from the repository root):
    python softcopy-toolkit/init_code_copy.py
    python softcopy-toolkit/init_code_copy.py --src path/to/src --dst path/to/src_prod
"""

from __future__ import annotations

import argparse
import io
import os
import shutil
import sys
import tokenize
from pathlib import Path

SOURCE_EXTENSIONS = {
    ".py", ".js", ".java", ".c", ".cpp", ".h", ".sh", ".bash",
    ".yml", ".yaml", ".tex", ".json", ".toml", ".rs", ".go",
}
IGNORE_DIRS = {".git", "__pycache__", "node_modules", ".idea", ".vscode", "venv", "env", ".venv"}


def multiline_string_lines(text: str) -> set[int]:
    """Return one-based line numbers touched by Python multi-line strings."""
    touched: set[int] = set()
    try:
        tokens = tokenize.generate_tokens(io.StringIO(text).readline)
        for token in tokens:
            if token.type == tokenize.STRING and token.end[0] > token.start[0]:
                touched.update(range(token.start[0], token.end[0] + 1))
    except (tokenize.TokenError, IndentationError):
        pass
    return touched


def strip_empty_lines(text: str, extension: str) -> str:
    """Remove blank lines, keeping blank lines inside Python multi-line strings."""
    lines = text.splitlines()
    keep = multiline_string_lines(text) if extension == ".py" else set()
    result = [line for index, line in enumerate(lines, start=1) if line.strip() or index in keep]
    return "\n".join(result) + "\n" if result else ""


def is_inside(child: Path, parent: Path) -> bool:
    """Return True when child is inside parent."""
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    repo_root = Path(__file__).resolve().parent.parent
    parser.add_argument("--src", type=Path, default=repo_root / "software_copyright" / "src")
    parser.add_argument("--dst", type=Path, default=repo_root / "software_copyright" / "src_prod")
    parser.add_argument("--keep-dst", action="store_true", help="Merge into an existing destination instead of replacing it")
    args = parser.parse_args()

    src, dst = args.src.resolve(), args.dst.resolve()
    if not src.is_dir():
        print(f"ERROR: source directory not found: {src}", file=sys.stderr)
        return 2
    if src == dst or is_inside(dst, src) or is_inside(src, dst):
        print("ERROR: destination must be a separate directory outside the source tree", file=sys.stderr)
        return 2

    if dst.exists() and not args.keep_dst:
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)

    file_count = 0
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for name in files:
            source_file = Path(root) / name
            if source_file.suffix.lower() not in SOURCE_EXTENSIONS:
                continue
            rel = source_file.relative_to(src)
            target_file = dst / rel
            target_file.parent.mkdir(parents=True, exist_ok=True)
            try:
                text = source_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                print(f"WARNING: skipped non-UTF-8 file: {rel}", file=sys.stderr)
                continue
            target_file.write_text(strip_empty_lines(text, source_file.suffix.lower()), encoding="utf-8")
            file_count += 1

    print(f"Source: {src}")
    print(f"Copy:   {dst}")
    print(f"Copied {file_count} files with empty lines removed.")
    print("The original source was not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
