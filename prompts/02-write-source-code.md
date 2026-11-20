# Prompt 2：写源程序文档

## 使用方式

把本文件内容作为 AI 的指令，让它准备源程序鉴别材料。先给 AI 真实源码的位置和要纳入的文件清单。

## 提示词正文

你负责生成软件著作权申请的源程序文档。只做代码清单的组织，不写解说文字。流程如下。

### 1. 准备代码副本

- 唯一开发源是 `software_copyright/src/`，不要直接改它。
- 复制到提交副本：`cp -a src/. src_prod/`。
- 去空行并统计：`python softcopy-toolkit/count_lines.py software_copyright/src_prod --remove-empty`。该脚本只在路径含 `software-copyright` 或 `software_copyright` 时允许改写。
- 改完 `src/` 后必须重新复制并去空行，否则文档用的是旧代码。判断过期要先重新生成再比较，直接 diff 的差异大多是空行。

### 2. 编辑 code_simplified.tex

- 主文档是 `source-code.tex`，不要改它；只编辑 `code_simplified.tex`。
- 只写 `\section`、`\subsection` 和 `\lstinputlisting` 三类语句，不写任何解说文字。
- `\section` 按功能模块分组，`\subsection` 用文件名；文件名里的下划线写成 `\_`（如 `my\_module.py`）。
- 路径指向 `src_prod/`，如 `\lstinputlisting{src_prod/demo_tool/io.py}`。
- 挑能体现主要功能的模块；代码总量大时不要塞无关代码。
- 总行数用 count_lines.py 统计后填入申请表"源程序量"。

### 3. 样式约定（已在模板里设好，通常不用改）

- `source-code.tex` 用 `\newcommand{\CodeBlockStyle}{plain}` 去掉代码框边框和底色，纯白底交存。
- 字体 `font=times*`，不生成目录，封面后直接进代码清单。
- 行号标在右上角由类文件的页眉设置负责，不要自己加。

### 4. 编译与验收

```bash
cd software_copyright
bash ../softcopy-toolkit/compile.sh "$(pwd)/source-code.tex"
python ../softcopy-toolkit/check_pdf_lines.py source-code.pdf --kind source --scope deposit
```

- 每页不少于50行；不足60页全交。
- 检查有没有稀疏页、有没有换行导致的难看断行。
- 交存节选用 `extract_front_back_pages.py` 取前30+后30页，不要自己删代码。

### 自动检查

- 所有 `\lstinputlisting` 指向的文件都存在。
- 文件名下划线已转义，路径正确。
- 代码清单与真实源码范围一致，无旧代码残留。
