#!/usr/bin/env python3
"""软著文档本地 Web 查看服务

把 software_copyright/ 下的 document.pdf 与 source-code.pdf 以 HTTP 方式暴露，
支持 Range 请求，浏览器可直接内嵌渲染 PDF。

用法:
    python serve_docs.py                     # 默认 127.0.0.1:8000
    python serve_docs.py --port 9000
    python serve_docs.py --bind 0.0.0.0      # 供内网其他机器访问

配合 SSH 端口转发从另一台机器访问（不建议直接暴露到内网）:
    ssh -L 8000:127.0.0.1:8000 gxf1212@<host>
"""
import argparse
import mimetypes
import os
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Tuple

# 脚本所在目录（softcopy-toolkit/）的上一级，即 software_copyright/
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIME_PDF = "application/pdf"
# RFC 7233: Range: bytes=START-END；END 省略表示到文件末尾
RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")


def _parse_range(raw: Optional[str], total: int) -> Optional[Tuple[int, int]]:
    """解析 Range 请求头，返回 [start, end]（闭区间，含 end），非法或越界返回 None。

    Args:
        raw: Range 请求头原文，如 "bytes=1000-1999"。
        total: 文件总字节数。

    Returns:
        合法的 (start, end) 区间，或 None（表示忽略 Range，返回完整文件）。
    """
    if not raw:
        return None
    match = RANGE_RE.match(raw.strip())
    if not match:
        return None
    start_s, end_s = match.groups()
    try:
        start = int(start_s) if start_s else 0
        end = int(end_s) if end_s else total - 1
    except ValueError:
        return None
    if start < 0 or start >= total:
        return None
    end = min(end, total - 1)
    if start > end:
        return None
    return start, end


class RangeHandler(BaseHTTPRequestHandler):
    """支持 Range 请求的只读文件服务，静态文件根目录为 ROOT。"""

    def log_message(self, format: str, *args) -> None:  # noqa: N802 - 遵循基类命名
        print(f"[{self.address_string()}] {format % args}", flush=True)

    def do_HEAD(self) -> None:  # noqa: N802 - 遵循基类命名
        self._respond(include_body=False)

    def do_GET(self) -> None:  # noqa: N802 - 遵循基类命名
        self._respond(include_body=True)

    def _respond(self, include_body: bool) -> None:
        # 把 URL 路径安全地映射到 ROOT 之下，防止路径穿越
        rel = os.path.normpath(self.path.split("?", 1)[0].lstrip("/"))
        target = os.path.join(ROOT, rel) if rel else ROOT
        if not target.startswith(ROOT):
            self.send_error(403, "Forbidden")
            return
        if os.path.isdir(target):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            body = self._index_body().encode("utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if not os.path.isfile(target):
            self.send_error(404, "File not found")
            return

        size = os.path.getsize(target)
        ctype = mimetypes.guess_type(target)[0] or "application/octet-stream"
        if target.lower().endswith(".pdf") or "pdf" in ctype:
            ctype = MIME_PDF

        rng = _parse_range(self.headers.get("Range"), size)
        partial = rng is not None
        start, end = rng if rng else (0, size - 1)

        self.send_response(206 if partial else 200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        if partial:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            length = end - start + 1
        else:
            length = size
        self.send_header("Content-Length", str(length))
        self.end_headers()

        if not include_body:
            return

        with open(target, "rb") as fh:
            if partial:
                fh.seek(start)
                remaining = length
            else:
                remaining = size
            while remaining > 0:
                chunk = fh.read(min(65536, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def _index_title(self) -> str:
        """索引页标题，取自服务根目录名（toolkit 跨多个软著项目共用）。"""
        return f"{os.path.basename(ROOT.rstrip(os.sep)) or '软著'} 软件文档"

    def _index_body(self) -> str:
        """构建根目录文档索引页，列出本目录下所有 PDF。"""
        items = sorted(
            f for f in os.listdir(ROOT)
            if f.lower().endswith(".pdf")
        )
        links = "".join(
            f'<li><a href="{name}">{name}</a> '
            f'({os.path.getsize(os.path.join(ROOT, name)) / 1024:.0f} KB)</li>\n'
            for name in items
        )
        title = self._index_title()
        return (
            "<!doctype html><html lang=\"zh\"><head><meta charset=\"utf-8\">"
            f"<title>{title}</title>"
            "<style>body{font-family:Arial,Helvetica,sans-serif;max-width:52em;"
            "margin:4em auto;padding:0 1em}li{margin:0.6em 0;font-size:1.05em}"
            "a{color:#1558b0}h1{font-size:1.5em}</style></head><body>"
            f"<h1>{title}</h1><p>点击以下文档在浏览器中查看：</p>"
            f"<ul>{links}</ul></body></html>"
        )


def main() -> None:
    """解析命令行参数并启动 HTTP 服务。"""
    parser = argparse.ArgumentParser(description="软著文档本地 Web 查看服务")
    parser.add_argument("--bind", default="127.0.0.1",
                        help="监听地址，默认 127.0.0.1（仅本机）")
    parser.add_argument("--port", type=int, default=8000, help="监听端口，默认 8000")
    args = parser.parse_args()

    server = HTTPServer((args.bind, args.port), RangeHandler)
    print(f"文档目录: {ROOT}")
    print(f"打开 http://{args.bind}:{args.port}/ 查看文档索引")
    print("按 Ctrl+C 停止服务")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
