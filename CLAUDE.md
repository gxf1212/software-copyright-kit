# 软著材料生成：AI全流程指南

本文件是给AI读的操作手册。用户把本仓库克隆或下载到本地、提供软件信息后，AI读完本文件即可独立完成整套软著材料。**先读本文件，再动手；不要跳过核对步骤。**

**合规边界（先看这一条）**：自2026-03-15起，中国版权保护中心新版申请表要求申请人手抄承诺“本软件确系独立开发，未使用AI开发编写代码、撰写文档或生成登记申请材料”。本仓库的AI工作流适合读源码、梳理功能、生成草稿和排版，但**最终提交前必须由申请人据实确认**：若确实用了AI辅助，按登记机构或代理的要求核实如何申报，不得签署与实际情况不符的声明。本仓库不提供任何规避真实性承诺的方法。

## 0. 本仓库是什么

一个通用的软件著作权材料模板包，不含任何特定软件的个人信息。示例软件是虚构的 `demo_tool`（轻量数据整理工具，命令行+浏览器双入口），只用来示范“每章该写什么、写成什么样”。用户使用时把它换成自己的软件。

目录结构：

```
software-copyright-kit/
├── CLAUDE.md                 本文件：AI全流程
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
│   ├── easybook.cls          第三方LaTeX模板（LPPL），不要改
│   ├── easybase.sty          第三方LaTeX模板，不要改
│   ├── eb-tcolorbox.cfg      第三方配色，不要改
│   ├── images/               截图与架构图放这里
│   ├── src/                  开发源码（唯一开发源）
│   ├── src_prod/             去空行副本，供code_simplified.tex引用（仓库自带，改代码后重新生成）
│   └── materials/
│       ├── application.md    申请表模板（只有md，无docx）
│       └── architecture.mmd  架构图Mermaid源
├── softcopy-toolkit/         编译、行数统计、抽页、查词工具
└── guidelines/                  分步prompt与写作规范
```

## 1. 开工前：向用户收齐信息

不要凭空编造。缺下列信息就先问用户，一次问清：

1. 软件全称、简称、版本号（决定settings.tex三处命名）。
2. 著作权人、开发人员、完成日期、 Contact信息（填application.md）。
3. 用哪种说明书：用户手册（界面型）、使用说明书（命令行型）、设计说明书（算法/引擎型）。三者任选其一即可，但本模板默认把几种都列出，按需删章。
4. 真实源码位置，以及哪些文件要放进源程序文档。
5. 界面型软件：真实截图。完整界面图能看清软件名称，局部操作图用于说明关键步骤，两者结合；重点是真实、清晰、功能可识别，软件名与申请表一致。不强制每张都全屏。
6. 第三方依赖及其许可证。

**核对原则**：软著必须与真实代码一致。先抓真实源码的函数名、参数、文件路径，再写文档。源码里没有的功能不写；写了的信息要准确。三处名称（申请表 / 说明书封面 / 源码页眉）必须完全一致。

## 2. 改造步骤（按顺序执行）

### 步骤0：先审查源码，再规划章节（不要跳过）

拿到软件信息后，先做审计再动笔。说明书越写越长、反复返工，通常都是因为一开始没规划好功能覆盖。

1. **列出真实功能清单**：逐个模块看源码，列出功能、入口（CLI/API/GUI）、重要参数、输入输出、模块关系。
2. **填关键事实清单**：把重要数字、定义、来源文件和适用范围写进 `software_copyright/materials/facts.md`（模板已备好）。每条附真实文件路径或函数名。数字相近但范围不同的，必须写清统计范围，例如“实验材料总数”“组合库内已测数”“未测候选数”是三件不同的事。
3. **核对功能动词**：检查“支持”“自动”“实时”“预测”“验证”“训练”这些词是否真的由源码实现；区分真实计算、历史结果展示、缓存、日志回放和仅供演示的功能。有模型的软件还要分开训练表现、交叉验证、独立测试和最终预测。
4. **再决定写哪些章**：根据功能类型和事实清单裁剪章节，不要直接套模板把所有章都写一遍。命令行软件保留CLI章、删GUI章；界面软件反之；算法引擎重点写实现机制。复杂科研软件必须生成facts.md，普通工具软件至少口头完成这份核对。

写作时所有章节只引用facts.md里的数据，不另起炉灶。写总原则见 `guidelines/author-philosophy.md`。

### 步骤A：配置命名

编辑 `software_copyright/settings.tex`，把 `\Name`、`\NameCN`、`\FullName`、`\Version`、`\Header` 换成用户软件的信息。全文其余位置都引用这些宏，不要在正文里手写软件名。

按软件类型裁剪章节：在 `document.tex` 里注释掉用不到的 `\input` 行。命令行软件删 `4-gui-usage.tex`，界面软件删 `3-cli-usage.tex`，纯算法软件可再删 `2-installation.tex` 的安装细节。

### 步骤B：写说明书各章

逐章改写 `1-introduction.tex` 至 `7-appendix.tex`。每章顶部注释已写明“写什么、哪些必写、适用哪类软件”，按注释写。细节prompt见 `guidelines/01-handbook-guide.md`。

注意：
- 只写真实功能；不确定就简略，正确比丰富重要。
- 中文标点；数字/英文与中文之间不加空格；斜杠用半角 `/`。
- 行内代码用 `\lstinline|...|`，代码块用 `\begin{lstlisting}[language=...,style=blockstyle]`。
- 化学式用 `\ce{}`（mhchem已加载），SMILES等机器可读串用 `\lstinline`。
- 表格用三线表（`booktabs`）居中；段落顶格不缩进。
- 写“见表\ref”不要写“如表\ref”，写“见图\ref”不要写“如图\ref”。

### 步骤C：准备源程序文档

1. 把真实源码放到 `software_copyright/src/`（保留原始开发源码，不要动）。
2. 运行初始化脚本生成去空行副本：`python softcopy-toolkit/init_code_copy.py --force`。仓库已自带`src_prod/`，目标非空需要`--force`；脚本只读取`src/`、写入`src_prod/`，不改动原始源码；Python多行字符串里的空行会保留。
3. 统计行数：`python softcopy-toolkit/count_lines.py software_copyright/src_prod`。如需对副本再去空行，可加 `--remove-empty`，该选项只允许在名为 `src_prod` 的生成副本上执行，对 `src/` 会拒绝。
4. 编辑 `code_simplified.tex`：按模块分组写 `\section` / `\subsection`（文件名里的 `_` 写成 `\_`），每条代码用 `\lstinputlisting{src_prod/...}`。只写清单，不写解说文字。细节见 `guidelines/02-source-code-guide.md`。

### 步骤D：写申请表

按 `guidelines/03-application-guide.md` 填 `software_copyright/materials/application.md`。字数限制：“一个字母算一个字”。主要功能500–1300字，开发目的/面向领域各50字以内，技术特点100字以内。申请表不提交docx。

### 步骤E：编译

在 `software_copyright/` 目录下执行（用绝对路径传tex，避免脚本从别的目录找到另一份同名文件）：

```bash
bash ../softcopy-toolkit/compile.sh "$(pwd)/document.tex"
bash ../softcopy-toolkit/compile.sh "$(pwd)/source-code.tex"
```

也可直接 `xelatex document.tex`（跑两遍）/ `xelatex source-code.tex`。产出 `document.pdf`（说明书）与 `source-code.pdf`（源代码）。

`compile.sh` 已处理Windows下临时目录删除被拦截的问题，编译失败会返回非零且不把旧PDF误报成功。若仍异常，可直接手动 `xelatex` 两遍。

### 步骤F：核对与验收

按 `guidelines/04-review-guide.md` 做三件事：

1. **事实核对**：逐章核对API、参数、模块路径、文件名；核对三处软件名与版本号；对照facts.md核对关键数字与定义；检查“支持/自动/实时/预测/验证/训练”等动词是否真由源码实现；区分真实计算与日志回放、历史结果展示。
2. **命令可运行**：每条写进文档的命令都实际跑一遍，确认参数和默认值正确、入口不依赖特殊环境。找到函数不等于功能可用。
3. **去AI味与排版**：删套话和防御性表述、删与实际操作无关的基础知识讲解，统一术语，扫长段落，中英文间不加空格，全角标点。写作规范见 `guidelines/writing-style.md`；总原则见 `guidelines/author-philosophy.md`。

自动检查可跑 `bash tests/smoke.sh`（若有），覆盖CLI命令、源码副本生成和两份文档编译。

再做版面检查：

```bash
# 每页行数：源程序>=50行，文档>=30行
python softcopy-toolkit/check_pdf_lines.py software_copyright/source-code.pdf --kind source --scope deposit
python softcopy-toolkit/check_pdf_lines.py software_copyright/document.pdf --kind document --scope deposit
```

需要交存节选时（前后各30页，封面与目录自动排除）：

```bash
python softcopy-toolkit/extract_front_back_pages.py software_copyright/source-code.pdf
python softcopy-toolkit/extract_front_back_pages.py software_copyright/document.pdf
```

生成的节选PDF和交存报告要人工核对：页码连续、源文件顺序正确、封面是否已排除、代码是否完整。自动检查仅作辅助。

最后冻结版本（记录源码commit/哈希、版本、日期和PDF哈希，便于追溯）：

```bash
python softcopy-toolkit/freeze_version.py
```

公开发布前跑一次隐私检查，逐条人工确认报告里的行，不要把研究数据、真实姓名、内部路径或第三方代码带进公开仓库：

```bash
python softcopy-toolkit/check_privacy.py .
```

## 3. 代码管理（必守）

- `src/` 是唯一开发源，功能改动只动 `src/`。
- `src_prod/` 是生成副本，去空行后供 `code_simplified.tex` 引用。仓库自带一份，改完 `src/` 后重新运行初始化脚本更新。
- 改完`src/`必须重新运行`python softcopy-toolkit/init_code_copy.py --force`，否则源码文档用的是旧代码。
- 判断“是否过期”要先重新复制去空行再比较；直接 `diff src src_prod` 的差异大多是空行，不能据此判断。

## 4. 排版约定速查

- 源程序文档：`\CodeBlockStyle{plain}` 去掉边框底色；`font=times*`；不生成目录。
- 用户手册：默认带边框底色代码框；`font=noto`；有目录。
- 中文标点用全角 `（）、，：。“”`，标点前不加空格。
- 独立标题 `\textbf{标题：}` 写成 `\paragraph{标题}`；段落内的 `\textbf{}` 保留。
- LaTeX源码里正文的 `_` 写成 `\_`；`lstlisting` 和 `\lstinline` 内不用转义。
- 段落顶格不缩进；不用 `\newline`，不手动断行。
- 表格三线表居中；代码块用4个空格缩进，不用制表符。
- 架构图、流程图、状态图这类示意图优先用TikZ直接在tex里画（第5章有可编译例子，settings.tex已加载tikz及positioning/arrows.meta/calc/fit库），矢量清晰、不依赖外部文件；界面截图等真实图像才放 `images/` 用 `\includegraphics` 插入。
- 若坚持用Mermaid画架构图，先写 `materials/architecture.mmd` 再渲染成PNG放入 `images/`。

## 5. 交付清单（做完逐项确认）

- [ ] settings.tex的软件名/版本号已改，三处命名一致
- [ ] 用不到的章节已从document.tex注释掉
- [ ] 说明书各章正文已按真实软件改写，占位的“示例单位/示例网址/请替换”全部清掉
- [ ] 界面截图真实清晰、能识别软件名与关键功能，软件名与申请表一致（界面型）
- [ ] source-code.tex无代码框，code_simplified.tex指向src_prod/
- [ ] application.md占位符全部替换，字数符合限制
- [ ] document.pdf与source-code.pdf编译成功
- [ ] 每页行数达标，节选PDF已生成且人工核对过页码与代码完整性
- [ ] facts.md的关键数字、定义、动词核对完成，跨章节一致
- [ ] 每条写进文档的命令都实际跑通过
- [ ] 去AI味与术语统一已做，源码/文档一致性核对已做
- [ ] 版本冻结已生成；公开前隐私检查已跑并逐条确认

## 6. 边界与注意

- 本模板不含申请表docx，只有 `application.md`。
- `easybook.cls`、`easybase.sty`、`eb-tcolorbox.cfg` 是第三方文件（LPPL），不要修改。
- 去AI味的完整写作规范见 `guidelines/writing-style.md`；独立skill另行发布，本仓库只整合可执行要点。
- Git commit message用英文，不用中文。
