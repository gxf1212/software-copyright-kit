# 指南2：写源程序文档

## 使用方式

本文件是写作与自查的清单。把真实软件信息附在前面，可交给AI执行，也可自己照着做：准备源程序鉴别材料。先准备真实源码的位置和要纳入的文件清单。

## 提示词正文

你负责生成软件著作权申请的源程序文档。只做代码清单的组织，不写解说文字。流程如下。

### 1. 准备代码副本

- 唯一开发源是 `software_copyright/src/`，不要直接改它。
- 运行初始化脚本生成提交副本：`python softcopy-toolkit/init_code_copy.py --force`。仓库已自带`src_prod/`，目标非空必须加`--force`；脚本只读取`src/`、写入`src_prod/`，不改动原始源码；Python多行字符串里的空行会保留，其他语言原样复制。
- 改完 `src/` 后必须重新运行初始化脚本，否则源码文档用的是旧代码。判断是否过期要先重新生成再比较，直接 `diff src src_prod` 的差异大多是空行，不能据此判断。

### 2. 编辑code_simplified.tex

- 主文档是 `source-code.tex`，不要改它；只编辑 `code_simplified.tex`。
- 只写 `\section`、`\subsection` 和 `\lstinputlisting` 三类语句，不写任何解说文字。
- `\section` 按功能模块分组，`\subsection` 用文件名；文件名里的下划线写成 `\_`（如 `my\_module.py`）。
- 路径指向 `src_prod/`，如 `\lstinputlisting{src_prod/demo_tool/io.py}`。
- 挑能体现主要功能的模块；代码总量大时不要塞无关代码。
- 总行数用count_lines.py统计后填入申请表"源程序量"。

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
- 交存节选用 `extract_front_back_pages.py` 取前30+后30页；开头的封面和目录会自动排除，前30页从正文第1页起算，不要自己删代码。

### 自动检查

- 所有 `\lstinputlisting` 指向的文件都存在。
- 文件名下划线已转义，路径正确。
- 代码清单与真实源码范围一致，无旧代码残留。
