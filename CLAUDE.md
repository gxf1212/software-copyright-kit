# 软著材料生成：AI 全流程指南

本文件是给 AI 读的操作手册。用户把本仓库克隆或下载到本地、提供软件信息后，AI 读完本文件即可独立完成整套软著材料。**先读本文件，再动手；不要跳过核对步骤。**

## 0. 本仓库是什么

一个通用的软件著作权材料模板包，不含任何特定软件的个人信息。示例软件是虚构的 `demo_tool`（轻量数据整理工具，命令行+浏览器双入口），只用来示范"每章该写什么、写成什么样"。用户使用时把它换成自己的软件。

目录结构：

```
software-copyright-kit/
├── CLAUDE.md                 本文件：AI 全流程
├── README.md                 人类快速上手说明
├── software_copyright/       一份可直接编译的示例软著包
│   ├── document.tex          用户手册主文件（带代码框）
│   ├── settings.tex          软件名/版本/字体的唯一配置处
│   ├── 1-introduction.tex    引言（必写）
│   ├── 2-installation.tex    基本信息与安装（必写）
│   ├── 3-cli-usage.tex       命令行使用方法（命令行软件写）
│   ├── 4-gui-usage.tex       图形界面使用方法（界面软件写）
│   ├── 5-architecture.tex    架构与模块（设计说明核心）
│   ├── 6-data-structure.tex  数据结构与文件说明
│   ├── 7-appendix.tex        附录与版本历史
│   ├── source-code.tex       源程序文档主文件（无代码框）
│   ├── code_simplified.tex   代码清单
│   ├── easybook.cls          第三方 LaTeX 模板（LPPL），不要改
│   ├── easybase.sty          第三方 LaTeX 模板，不要改
│   ├── eb-tcolorbox.cfg      第三方配色，不要改
│   ├── images/               截图与架构图放这里
│   ├── src/                  开发源码（唯一开发源）
│   ├── src_prod/             去空行副本，供 code_simplified.tex 引用，不进 Git
│   └── materials/
│       ├── application.md    申请表模板（只有 md，无 docx）
│       └── architecture.mmd  架构图 Mermaid 源
├── softcopy-toolkit/         编译、行数统计、抽页、查词工具
└── prompts/                  分步 prompt 与写作规范
```

## 1. 开工前：向用户收齐信息

不要凭空编造。缺下列信息就先问用户，一次问清：

1. 软件全称、简称、版本号（决定 settings.tex 三处命名）。
2. 著作权人、开发人员、完成日期、 Contact 信息（填 application.md）。
3. 用哪种说明书：用户手册（界面型）、使用说明书（命令行型）、设计说明书（算法/引擎型）。三者任选其一即可，但本模板默认把几种都列出，按需删章。
4. 真实源码位置，以及哪些文件要放进源程序文档。
5. 界面型软件：真实截图（必须全屏、软件名与申请表一致）。
6. 第三方依赖及其许可证。

**核对原则**：软著必须与真实代码一致。先抓真实源码的函数名、参数、文件路径，再写文档。源码里没有的功能不写；写了的信息尽量准确。三处名称（申请表 / 说明书封面 / 源码页眉）必须完全一致。

## 2. 改造步骤（按顺序执行）

### 步骤A：配置命名

编辑 `software_copyright/settings.tex`，把 `\Name`、`\NameCN`、`\FullName`、`\Version`、`\Header` 换成用户软件的信息。全文其余位置都引用这些宏，不要在正文里手写软件名。

按软件类型裁剪章节：在 `document.tex` 里注释掉用不到的 `\input` 行。命令行软件删 `4-gui-usage.tex`，界面软件删 `3-cli-usage.tex`，纯算法软件可再删 `2-installation.tex` 的安装细节。

### 步骤B：写说明书各章

逐章改写 `1-introduction.tex` 至 `7-appendix.tex`。每章顶部注释已写明"写什么、哪些必写、适用哪类软件"，按注释写。细节 prompt 见 `prompts/01-write-handbook.md`。

注意：
- 只写真实功能；不确定就简略，正确比丰富重要。
- 中文标点；数字/英文与中文之间不加空格；斜杠用半角 `/`。
- 行内代码用 `\lstinline|...|`，代码块用 `\begin{lstlisting}[language=...,style=blockstyle]`。
- 化学式用 `\ce{}`（mhchem 已加载），SMILES 等机器可读串用 `\lstinline`。
- 表格用三线表（`booktabs`）居中；段落顶格不缩进。
- 写"见表\ref"不要写"如表\ref"，写"见图\ref"不要写"如图\ref"。

### 步骤C：准备源程序文档

1. 把真实源码放到 `software_copyright/src/`（保留原始开发源码，不要动）。
2. 复制一份到 `src_prod/`：`cp -a src/. src_prod/`。
3. 去空行并统计：`python softcopy-toolkit/count_lines.py software_copyright/src_prod --remove-empty`。该脚本只在路径含 `software-copyright` 或 `software_copyright` 时允许改写，对原始源码目录会拒绝执行。
4. 编辑 `code_simplified.tex`：按模块分组写 `\section` / `\subsection`（文件名里的 `_` 写成 `\_`），每条代码用 `\lstinputlisting{src_prod/...}`。只写清单，不写解说文字。细节见 `prompts/02-write-source-code.md`。

### 步骤D：写申请表

按 `prompts/03-write-application.md` 填 `software_copyright/materials/application.md`。字数限制："一个字母算一个字"。主要功能 500–1300 字，开发目的/面向领域各 50 字以内，技术特点 100 字以内。申请表不提交 docx。

### 步骤E：编译

在 `software_copyright/` 目录下执行（用绝对路径传 tex，避免脚本从别的目录找到另一份同名文件）：

```bash
bash ../softcopy-toolkit/compile.sh "$(pwd)/document.tex"
bash ../softcopy-toolkit/compile.sh "$(pwd)/source-code.tex"
```

也可直接 `xelatex document.tex`（跑两遍）/ `xelatex source-code.tex`。产出 `document.pdf`（说明书）与 `source-code.pdf`（源代码）。

环境已知问题：`compile.sh` 含 `set -e`，其清理步骤的 `rm` 可能被 IDE 的安全删除包装器拦截并返回非0，导致编译中止（表现为没有成功输出、PDF 时间戳不变）。此时改用手动 `xelatex` 三遍即可。

### 步骤F：核对与验收

按 `prompts/04-check-and-polish.md` 做两件事：

1. **一致性核对**：抓真实源码签名，逐章核对 API、参数、模块路径、文件名；核对三处软件名与版本号；检查源码与说明文档描述是否矛盾。
2. **去 AI 味与排版**：删套话和防御性表述，统一术语，扫长段落，中英文间不加空格，全角标点。写作规范见 `prompts/writing-style.md`。

再做版面检查：

```bash
# 每页行数：源程序>=50行，文档>=30行
python softcopy-toolkit/check_pdf_lines.py software_copyright/source-code.pdf --kind source --scope deposit
python softcopy-toolkit/check_pdf_lines.py software_copyright/document.pdf --kind document --scope deposit
```

需要交存节选时（前后各30页）：

```bash
python softcopy-toolkit/extract_front_back_pages.py software_copyright/source-code.pdf
python softcopy-toolkit/extract_front_back_pages.py software_copyright/document.pdf
```

## 3. 代码管理（必守）

- `src/` 是唯一开发源，功能改动只动 `src/`。
- `src_prod/` 是生成副本，去空行后供 `code_simplified.tex` 引用，**不进 Git**。
- 改完 `src/` 必须重新 `cp -a src/. src_prod/` 再去空行，否则源码文档用的是旧代码。
- 判断"是否过期"要先重新复制去空行再比较；直接 `diff src src_prod` 的差异大多是空行，不能据此判断。

## 4. 排版约定速查

- 源程序文档：`\CodeBlockStyle{plain}` 去掉边框底色；`font=times*`；不生成目录。
- 用户手册：默认带边框底色代码框；`font=noto`；有目录。
- 中文标点用全角 `（）、，：。""`，标点前不加空格。
- 独立标题 `\textbf{标题：}` 写成 `\paragraph{标题}`；段落内的 `\textbf{}` 保留。
- LaTeX 源码里正文的 `_` 写成 `\_`；`lstlisting` 和 `\lstinline` 内不用转义。
- 段落顶格不缩进；不用 `\newline`，不手动断行。
- 表格三线表居中；代码块用4个空格缩进，不用制表符。
- 图放 `images/`；架构图先写 `materials/architecture.mmd` 再渲染成 PNG。

## 5. 交付清单（做完逐项确认）

- [ ] settings.tex 的软件名/版本号已改，三处命名一致
- [ ] 用不到的章节已从 document.tex 注释掉
- [ ] 说明书各章正文已按真实软件改写，占位的"示例单位/示例网址/请替换"全部清掉
- [ ] 界面截图齐全、全屏、软件名与申请表一致（界面型）
- [ ] source-code.tex 无代码框，code_simplified.tex 指向 src_prod/
- [ ] application.md 占位符全部替换，字数符合限制
- [ ] document.pdf 与 source-code.pdf 编译成功
- [ ] 每页行数达标，节选 PDF 已生成
- [ ] 去 AI 味与术语统一已做，源码/文档一致性核对已做

## 6. 边界与注意

- 本模板不含申请表 docx，只有 `application.md`。
- `easybook.cls`、`easybase.sty`、`eb-tcolorbox.cfg` 是第三方文件（LPPL），不要修改。
- 去 AI 味的完整写作规范见 `prompts/writing-style.md`；独立 skill 另行发布，本仓库只整合可执行要点。
- Git commit message 用英文，不用中文。
