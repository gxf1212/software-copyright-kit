# Softcopy Toolkit

软著材料的编译、行数核对与抽页工具，跨多个软著包共用。脚本来自实际软著项目，按原样打包。

## 脚本一览

| 脚本 | 用途 | 依赖 |
|------|------|------|
| `compile.sh` | XeLaTeX 编译说明书或源程序文档 | `xelatex`（必需）、`pdfinfo`/`fc-list`（可选） |
| `check_pdf_lines.py` | 统计 PDF 每页可见行数，对照软著下限 | `pdftotext`（poppler-utils） |
| `count_lines.py` | 统计源码行数；`--remove-empty` 去空行 | 仅标准库 |
| `extract_front_back_pages.py` | 提取前 N + 后 M 页生成节选 PDF | `pypdf` |
| `search_pdf_text.py` | 在 PDF 文本层检索关键词 | `pymupdf` |
| `convert_quotes.py` | Markdown 英文双引号转中文引号 | 仅标准库 |
| `serve_docs.py` | 本地 Web 查看生成的两份 PDF | 仅标准库 |

## 安装依赖

```bash
sudo apt install texlive-xetex texlive-lang-chinese texlive-fonts-recommended \
                 texlive-latex-extra texlive-science poppler-utils
pip install -r requirements.txt
```

## 常用命令

在 `software_copyright/` 目录下执行：

```bash
# 编译（传绝对路径，避免脚本从别的目录找到同名文件）
bash ../softcopy-toolkit/compile.sh "$(pwd)/document.tex"
bash ../softcopy-toolkit/compile.sh "$(pwd)/source-code.tex"

# 统计/去空行（只在路径含 software-copyright 或 software_copyright 时允许改写）
python ../softcopy-toolkit/count_lines.py src_prod --remove-empty

# 每页行数：源程序下限50，文档下限30
python ../softcopy-toolkit/check_pdf_lines.py source-code.pdf --kind source --scope deposit
python ../softcopy-toolkit/check_pdf_lines.py document.pdf --kind document --scope deposit

# 抽取前30+后30页节选
python ../softcopy-toolkit/extract_front_back_pages.py source-code.pdf
```

`compile.sh` 按文件名区分材料类型：`source-code.tex` 用50行规则，其余文档用30行规则。其它子命令：`clean`、`--open`、`help`。

`check_pdf_lines.py` 用 `pdftotext -layout` 统计 PDF 文本层非空行，排除页眉和纯页码。退出码：0 全部通过，1 有页面低于阈值，2 参数或依赖错误。截图页等可用 `--exempt-pages` 豁免。

`count_lines.py` 的 `--remove-empty` 会就地改写文件，只允许在提交副本 `src_prod/` 上运行，不能指向原始开发源码 `src/`。

## 本地查看

```bash
python3 ../softcopy-toolkit/serve_docs.py      # http://localhost:8000/
```
