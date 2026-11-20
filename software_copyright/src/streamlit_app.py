"""Streamlit entry point.

Run with ``streamlit run src/streamlit_app.py`` from the software_copyright
directory.  This wrapper keeps the package-relative imports in demo_tool.web
working, which would fail if Streamlit loaded web.py directly as a script.
"""

from __future__ import annotations

from demo_tool.web import main

if __name__ == "__main__":
    main()
