#!/usr/bin/env python3
"""Audit a software-copyright package for name/version consistency and leftovers.

Exit code 0 means no blocking issue; 1 means at least one issue was found.
The application form and facts file are templates by design, so their
``【...】`` slots are hints until --strict is given (use it after filling them).
A warning is not a legal finding: review each item manually.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def macro_value(settings: str, name: str) -> str:
    m = re.search(r"\\newcommand\{\\" + re.escape(name) + r"\}\{([^}]*)\}", settings)
    return m.group(1).strip() if m else ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    repo_root = Path(__file__).resolve().parent.parent
    parser.add_argument("--package", type=Path, default=repo_root / "software_copyright")
    parser.add_argument(
        "--strict", action="store_true",
        help="Count template placeholders in application.md/facts.md as issues "
             "(use after those files are filled in).",
    )
    args = parser.parse_args()
    pkg = args.package.resolve()
    settings = (pkg / "settings.tex").read_text(encoding="utf-8")

    name = macro_value(settings, "Name")
    name_cn = macro_value(settings, "NameCN")
    version = macro_value(settings, "Version")
    print(f"settings: Name={name!r} NameCN={name_cn!r} Version={version!r}\n")

    issues = 0
    hints = 0

    # 1.占位符残留：application.md/facts.md是待填模板，【】只作提示
    placeholder = re.compile(r"(?:【[^】]*】|示例单位|示例网址|XXX|TODO|FIXME|请替换)")
    for path in sorted(pkg.rglob("*.tex")) + sorted(pkg.rglob("*.md")):
        is_template = path.name in {"application.md", "facts.md"}
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not placeholder.search(line) or line.lstrip().startswith("%"):
                continue
            if is_template and "【" in line and not args.strict:
                hints += 1
                continue
            print(f"[PLACEHOLDER] {path.name}:{number}: {line.strip()[:100]}")
            issues += 1

    # 2.application.md的软件名/版本是否与settings一致
    app = pkg / "materials" / "application.md"
    app_text = app.read_text(encoding="utf-8") if app.exists() else ""
    if app.exists():
        for label, value in (("Version", version), ("NameCN", name_cn)):
            if not value or value in app_text:
                continue
            if "【" in app_text and not args.strict:
                hints += 1
                continue
            print(f"[MISMATCH] application.md does not mention {label}={value!r}")
            issues += 1

    # 3.facts.md是否填写
    facts = pkg / "materials" / "facts.md"
    if facts.exists():
        text = facts.read_text(encoding="utf-8")
        if "【" in text:
            if args.strict:
                print("[TODO] facts.md still has unfilled placeholders")
                issues += 1
            else:
                hints += 1
    else:
        print("[MISSING] materials/facts.md not found")
        issues += 1

    # 4. 代码清单引用的文件是否存在于src_prod
    code_list = pkg / "code_simplified.tex"
    if code_list.exists():
        for ref in re.findall(r"\\lstinputlisting\{([^}]+)\}", code_list.read_text(encoding="utf-8")):
            target = (pkg / ref).resolve()
            if not target.exists():
                print(f"[MISSING CODE] {ref} (run init_code_copy.py first)")
                issues += 1

    # 5.文档里是否残留旧启动命令（模块名web.py不算，只查streamlit run）
    stale = re.compile(r"streamlit\s+run[^\n]*\bweb\.py\b", re.IGNORECASE)
    for path in sorted(pkg.glob("*.tex")):
        text = path.read_text(encoding="utf-8")
        if stale.search(text):
            print(f"[STALE CMD] {path.name}: old streamlit entry (web.py)")
            issues += 1

    if hints:
        print(f"\n{hints} template slot(s) left for the user to fill; "
              "use --strict to count them as issues.")
    print(f"{issues} potential issue(s). Review manually; warnings are not legal findings.")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
