"""Minimal web interface of demo_tool, implemented with Streamlit."""

from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from .core import drop_empty_rows, normalize_header, trim_cells
from .io import read_rows, write_rows
from .report import summarize


def render_upload() -> Path | None:
    """Show the file uploader and save the upload to a temporary path."""
    upload = st.file_uploader("选择CSV文件", type=["csv"])
    if upload is None:
        return None
    target = Path(tempfile.gettempdir()) / upload.name
    target.write_bytes(upload.getvalue())
    return target


def render_preview(path: Path) -> None:
    """Display the first rows of the uploaded file."""
    header, rows = read_rows(path)
    st.write(f"共 {len(rows)} 行，{len(header)} 列")
    st.dataframe(rows[:20], columns=header, use_container_width=True)


def render_report(path: Path) -> None:
    """Display per-column completeness as a table."""
    header, rows = read_rows(path)
    data = [
        {"列名": item.name, "总数": item.total, "非空": item.filled, "缺失": item.missing}
        for item in summarize(header, rows)
    ]
    st.table(data)


def main() -> None:
    """Lay out the single-page interface."""
    st.set_page_config(page_title="DemoTool", layout="wide")
    st.title("DemoTool轻量数据整理工具")
    path = render_upload()
    if path is None:
        st.info("请先上传一个CSV文件")
        return
    tab_preview, tab_report = st.tabs(["数据预览", "完整性报告"])
    with tab_preview:
        render_preview(path)
    with tab_report:
        render_report(path)
    if st.button("清理并下载"):
        header, rows = read_rows(path)
        rows = drop_empty_rows(trim_cells(rows))
        output = Path(tempfile.gettempdir()) / "cleaned.csv"
        write_rows(output, normalize_header(header), rows)
        st.download_button("下载清理结果", data=output.read_bytes(), file_name="cleaned.csv")


if __name__ == "__main__":
    main()
