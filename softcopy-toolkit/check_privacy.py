#!/usr/bin/env python3
"""Pre-publication check for personal data and left-over placeholders.

This is a helper, not a guarantee.  Review the reported lines manually.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PATTERNS = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
    "windows-user-path": re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+"),
    "unix-home-path": re.compile(r"/(?:home|Users)/[A-Za-z0-9_-]+/"),
    "internal-host": re.compile(r"\b(?:[a-z0-9-]+\.)+(?:local|internal|corp)\b", re.I),
    "placeholder": re.compile(r"【[^】]*】|示例单位|示例网址|TODO|FIXME"),
}

TEXT_SUFFIXES = {".md", ".tex", ".py", ".sh", ".toml", ".cfg", ".cls", ".sty"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    hits = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        # 工具脚本和写作指南里含规则示例词，跳过以免误报
        rel = path.relative_to(root)
        if rel.parts and rel.parts[0] in {"softcopy-toolkit", "guidelines", "tests"}:
            continue
        # 第三方LaTeX模板（版权声明里有作者邮箱，已在THIRD-PARTY-NOTICES声明）
        if path.name in {"easybook.cls", "easybase.sty", "eb-tcolorbox.cfg"}:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(lines, start=1):
            for name, pattern in PATTERNS.items():
                if pattern.search(line):
                    print(f"{path.relative_to(root)}:{number}: [{name}] {line.strip()[:120]}")
                    hits += 1
    print(f"\nFound {hits} potential issue(s). Review each one before publishing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
