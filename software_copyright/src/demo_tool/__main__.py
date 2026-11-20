"""Allow running the CLI with ``python -m demo_tool``."""

from __future__ import annotations

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
