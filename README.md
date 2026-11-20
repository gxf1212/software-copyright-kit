<div align="center">

# software-copyright-kit

**一套公开、可复用的软件著作权申请材料模板包**

说明书 · 源程序文档 · 申请表 · 编译工具链 · AI分步提示词，全部打包好。克隆或下载后，把示例软件换成你自己的软件即可。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![文档语言](https://img.shields.io/badge/文档-中文-orange)]()
[![排版](https://img.shields.io/badge/排版-XeLaTeX-008080)]()
[![模板](https://img.shields.io/badge/模板-easybook-9cf)]()

</div>

软件著作权只在中国登记，所以本仓库的说明以中文为主。目标用户是课题组内外的研究生与开发者：照着模板改，就能得到一份格式合规、内容扎实的软著申请材料。

## 预览

说明书封面、正文内页与源程序文档封面。正文各章都已写示范内容，编译即可出PDF。

<p align="center">
  <img src="assets/handbook-cover.png" alt="说明书封面" width="280">
  <img src="assets/inner-page.png" alt="说明书正文内页" width="280">
  <img src="assets/sourcecode-cover.png" alt="源程序文档封面" width="280">
</p>

## 这套模板解决什么

写软著材料时，最费劲的不是写代码，而是不知道说明书该写哪几章、每章写什么、源程序文档怎么排版才合规。本仓库把这些"隐性的格式知识"沉淀成模板：

- 每章顶部都写了写作指南，标明"写什么、必写还是可选、适用哪类软件"，照着写就行。
- 命令行软件和界面软件是两种使用方式，各自独立成章，按软件类型删掉用不到的那章。
- 源程序文档已按最新版去掉代码框（纯白底交存），用户手册保留代码框，两种样式都给了。
- 申请表只保留 `application.md`（不含docx），mmd架构图源文件留作参考。

## 特性

| 能力 | 说明 |
|------|------|
| 章节齐全 | 引言、安装、命令行使用、界面使用、架构、数据结构、附录，共7章 |
| 直接编译 | easybook模板与分章tex就绪，改settings后xelatex即可出PDF |
| 合规排版 | 源程序文档无代码框，手册带代码框，三线表、页眉页码符合交存习惯 |
| 架构图用TikZ | 第5章有可直接编译的TikZ架构图例子，矢量清晰，不依赖外部图片 |
| 事实清单 | materials/facts.md记录关键数字与源码依据，避免跨章节口径不一致 |
| 工具链 | 编译、行数统计、抽页、查词、隐私检查、版本冻结脚本 |
| 写作指南 | guidelines/ 分阶段指南，自己写或交给AI都可以 |

## 快速开始

```bash
git clone https://github.com/gxf1212/software-copyright-kit.git
cd software-copyright-kit
```

### 给AI用

在仓库目录打开AI工具（Claude Code、Codex等），说明你的软件信息，让它读 `CLAUDE.md`（Codex等读 `AGENTS.md`）。流程是：审查源码 → 整理facts.md → 规划章节 → 写各章 → 准备源码 → 写申请表 → 编译 → 核对验收。

用不用AI由你决定。`guidelines/` 里的指南自己照着写同样适用。

### 手动用

1. 改 `software_copyright/settings.tex` 里的软件名和版本号。
2. 按软件类型在 `document.tex` 里注释掉用不到的章节。
3. 改写 `1-introduction.tex` 到 `7-appendix.tex`（每章顶部有注释指引）。
4. 源码放进 `software_copyright/src/`，运行初始化脚本生成去空行的 `src_prod/`，再改 `code_simplified.tex`。
5. 填 `software_copyright/materials/application.md`。
6. 编译两份PDF，检查每页行数。

```bash
# 克隆后先生成代码副本（src_prod/ 不进Git，必须本地生成）
python softcopy-toolkit/init_code_copy.py

cd software_copyright
bash ../softcopy-toolkit/compile.sh "$(pwd)/document.tex"
bash ../softcopy-toolkit/compile.sh "$(pwd)/source-code.tex"
```

`init_code_copy.py` 会生成 `src_prod/`（去空行的代码副本），源代码文档实际引用的就是它；`src/` 里的原始代码不会被改动。

## 目录结构

```
software-copyright-kit/
├── README.md / AGENTS.md / CLAUDE.md   说明与agent入口
├── software_copyright/       示例软著包（可直接编译）
│   ├── document.tex          用户手册主文件（带代码框）
│   ├── source-code.tex       源程序文档主文件（无代码框）
│   ├── settings.tex          软件名/版本/字体的唯一配置处
│   ├── 1-introduction.tex … 7-appendix.tex  七个章节模板
│   ├── images/               截图与架构图
│   ├── src/                  开发源码（唯一开发源）
│   └── materials/            application.md申请表 + facts.md事实清单 + architecture.mmd
├── softcopy-toolkit/         编译、行数统计、抽页、隐私检查、版本冻结
├── guidelines/               写作指南（总原则、各阶段、写作规范）
└── assets/                   README预览图
```

## 文档导航

- [guidelines/author-philosophy.md](guidelines/author-philosophy.md)：写作总原则，先读这个。
- [guidelines/](guidelines/)：分阶段指南（写说明书、写源程序、填申请表、核对验收）。
- [guidelines/writing-style.md](guidelines/writing-style.md)：中文写作规范（去AI味、标点空格、术语）。
- [CLAUDE.md](CLAUDE.md) / [AGENTS.md](AGENTS.md)：AI agent的全流程入口。
- [facts.md](software_copyright/materials/facts.md)：关键事实清单模板，写作前先填。
- [softcopy-toolkit/](softcopy-toolkit/)：工具链说明与脚本。

## 环境

需要XeLaTeX及中文字体。Ubuntu示例：

```bash
sudo apt install texlive-xetex texlive-lang-chinese texlive-fonts-recommended \
                 texlive-latex-extra texlive-science poppler-utils
pip install -r requirements.txt
```

Windows可用已安装的TeX Live；`easybook.cls` 系列模板文件已随仓库提供，无需额外安装。

## 交存要点（以官方最新指引为准）

- 说明书与源程序都是前、后各连续30页；不足60页全交。
- 源程序每页不少于50行，文档每页不少于30行。
- 申请表、说明书封面、源码页眉的软件全称与版本号必须一致；界面截图上的名称也要一致。
- 不虚构内容凑篇幅；总量不足就全交。
- 抽页用 `extract_front_back_pages.py`，它会自动识别开头的封面和目录页，这些页保留但不占用前30页配额。
- `check_pdf_lines.py` 统计的是排版后的印刷视觉行，适合发现稀疏页，不能替代人工核对代码完整性；示例包不足60页时最后一页行数为零头属正常，检查可加 `--allow-short-last`。

## 登记合规提醒（2026年起）

自2026-03-15起，中国版权保护中心新版申请表要求申请人手抄承诺"本软件确系独立开发，未使用AI开发编写代码、撰写文档或生成登记申请材料"，并建立失信惩戒机制。本仓库的AI工作流适合读源码、梳理功能、生成草稿和排版；**提交前请据实确认AI使用情况**，必要时向登记机构或代理核实如何申报，不要签署与实际情况不符的声明。本仓库不提供规避真实性承诺的做法。

## 许可

本仓库自有内容采用MIT许可，见 [LICENSE](LICENSE)。`easybook.cls`、`easybase.sty`、`eb-tcolorbox.cfg` 为第三方文件，采用LaTeX Project Public License，见 [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)，请勿修改。

欢迎提issue和pull request，也欢迎把本模板改成你自己的软著包。
