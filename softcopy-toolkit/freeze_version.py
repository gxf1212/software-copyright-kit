#!/usr/bin/env python3
"""Record a version snapshot for a generated software-copyright package.

Writes a small JSON file with software version, source commit/hash, generation
date and the hashes of the final PDFs, so a submitted package can be traced
back to the exact source state.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit(repo: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, timeout=10
        )
        return out.stdout.strip() if out.returncode == 0 else "not-a-git-repo"
    except (OSError, subprocess.SubprocessError):
        return "git-unavailable"


def tree_hash(src: Path) -> str:
    """Hash all source files, in sorted relative-path order."""
    h = hashlib.sha256()
    for file in sorted(p for p in src.rglob("*") if p.is_file()):
        h.update(str(file.relative_to(src)).encode("utf-8"))
        h.update(sha256(file).encode("ascii"))
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    repo_root = Path(__file__).resolve().parent.parent
    parser.add_argument("--package", type=Path, default=repo_root / "software_copyright")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    pkg = args.package.resolve()
    src = pkg / "src"
    if not src.is_dir():
        print(f"ERROR: source directory not found: {src}")
        return 2

    settings = (pkg / "settings.tex").read_text(encoding="utf-8")
    version = "unknown"
    for line in settings.splitlines():
        if line.startswith(r"\newcommand{\Version}"):
            version = line.split("{")[-1].rstrip("} ").strip()
            break

    record = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "software_version": version,
        "source_commit": git_commit(pkg),
        "source_tree_sha256": tree_hash(src),
        "pdfs": {
            p.name: {"sha256": sha256(p), "size": p.stat().st_size}
            for p in sorted(pkg.glob("*.pdf"))
        },
    }

    output = args.output or (pkg / "materials" / "version-freeze.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output}")
    print(f"Version: {version}  Source tree: {record['source_tree_sha256'][:12]}  PDFs: {len(record['pdfs'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
