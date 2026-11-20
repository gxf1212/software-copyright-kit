# Softcopy Toolkit

软著材料的编译、行数核对与抽页工具，跨多个软著包共用。脚本来自实际软著项目，按原样打包。

## 脚本一览

| 脚本 | 用途 | 依赖 |
|------|------|------|
| `compile.sh` | XeLaTeX编译说明书或源程序文档 | `xelatex`（必需）、`pdfinfo`/`fc-list`（可选） |
| `check_pdf_lines.py` | 统计PDF每页可见行数，对照软著下限 | `pdftotext`（poppler-utils） |
| `init_code_copy.py` | 从 `src/` 生成去空行的 `src_prod/` 副本 | 仅标准库 |
| `count_lines.py` | 统计源码行数；`--remove-empty` 去空行（仅限 `src_prod/`） | 仅标准库 |
| `extract_front_back_pages.py` | 提取前N + 后M页生成节选PDF，自动排除封面与目录 | `pypdf` |
| `audit_material.py` | 核对命名一致性、占位符、facts.md、代码引用 | 仅标准库 |
| `check_privacy.py` | 发布前检查个人信息、邮箱、路径、占位符 | 仅标准库 |
| `freeze_version.py` | 记录源码commit/哈希、版本、日期与PDF哈希 | 仅标准库 |
| `search_pdf_text.py` | 在PDF文本层检索关键词 | `pymupdf` |
| `convert_quotes.py` | Markdown英文双引号转中文引号 | 仅标准库 |
| `serve_docs.py` | 本地Web查看生成的两份PDF | 仅标准库 |

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

# 覆盖仓库自带的代码副本（在仓库根目录运行；src/ 不会被改动）
python softcopy-toolkit/init_code_copy.py --force

# 统计行数；--remove-empty只允许在src_prod/ 这类生成副本上运行
python ../softcopy-toolkit/count_lines.py src_prod

# 每页行数：源程序下限50，文档下限30
python ../softcopy-toolkit/check_pdf_lines.py source-code.pdf --kind source --scope deposit
python ../softcopy-toolkit/check_pdf_lines.py document.pdf --kind document --scope deposit

# 抽取前30+后30页节选（封面与目录自动排除）
python ../softcopy-toolkit/extract_front_back_pages.py source-code.pdf

# 发布前审计与版本冻结
python ../softcopy-toolkit/audit_material.py
python ../softcopy-toolkit/check_privacy.py .
python ../softcopy-toolkit/freeze_version.py
```

`compile.sh` 按文件名区分材料类型：`source-code.tex` 用50行规则，其余文档用30行规则。其它子命令：`clean`、`--open`、`help`。编译失败返回非零，不会把旧PDF误报成功。

`audit_material.py` 返回0表示没有阻塞问题，返回1表示检出问题；`application.md`/`facts.md`里的【】是待填模板占位，只作提示，填完后加`--strict`一并检查。

`check_pdf_lines.py` 用 `pdftotext -layout` 统计PDF文本层非空行，排除页眉和纯页码。退出码：0全部通过，1有页面低于阈值，2参数或依赖错误。截图页等可用 `--exempt-pages` 豁免，末页零头可用 `--allow-short-last`。它统计的是印刷视觉行，长代码折行会算成多行，不能替代人工核对。

`count_lines.py` 的 `--remove-empty` 会就地改写文件，只允许在名为 `src_prod` 的生成副本上运行，指向原始开发源码 `src/` 会被拒绝。`init_code_copy.py` 用 `tokenize` 保留Python多行字符串里的空行，避免改变代码含义。

`extract_front_back_pages.py` 默认按页码标记识别开头的封面和目录并排除，前30页从正文第1页起算；`--cover-pages N` 手动指定前置页数，`--no-auto-cover` 关闭识别，`--keep-cover` 保留封面但不占配额（仅用于预览）。

## 本地查看

```bash
python3 ../softcopy-toolkit/serve_docs.py      # http://localhost:8000/
```
