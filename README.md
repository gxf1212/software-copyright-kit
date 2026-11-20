# 软件著作权材料模板包

一套可复用的软著申请材料模板：说明书、源程序文档、申请表、编译工具链和给 AI 的分步 prompt 都打包好了。克隆或下载后，把虚构的示例软件 `demo_tool` 换成你自己的软件即可。

软著只在中国登记，所以本仓库的说明以中文为主。

## 这套模板解决什么

- 不知道说明书该写哪些章、每章写什么 → 每章 tex 顶部都有写作指南注释。
- 命令行软件还是界面软件不知道怎么取舍 → 两种使用方式各写一章，按需删。
- 源程序文档格式总出错 → 已在最新版样式里去掉代码框，纯白底交存。
- 申请表字数、命名一致性容易踩坑 → 模板里标了限制和核对点。
- 想让 AI 全程代写 → 把本仓库交给 AI，它会读 `CLAUDE.md` 自动跑完整流程。

## 目录

```
software-copyright-kit/
├── CLAUDE.md                 AI 全流程指南（给 AI 读）
├── software_copyright/       示例软著包（可编译）
├── softcopy-toolkit/         编译、行数统计、抽页、查词工具
└── prompts/                  分步 prompt 与写作规范
```

## 快速开始

```bash
git clone <本仓库地址>
cd software-copyright-kit
```

### 给 AI 用（推荐）

在仓库目录打开 AI 工具，说明你的软件信息，让它读 `CLAUDE.md`。流程是：收信息 → 改 settings → 写各章 → 准备源码 → 写申请表 → 编译 → 核对验收。

### 手动用

1. 改 `software_copyright/settings.tex` 里的软件名和版本号。
2. 按软件类型在 `document.tex` 里注释掉用不到的章节。
3. 改写 `1-introduction.tex` 到 `7-appendix.tex`（每章顶部有注释指引）。
4. 源码放进 `software_copyright/src/`，复制到 `src_prod/` 后去空行，改 `code_simplified.tex`。
5. 填 `software_copyright/materials/application.md`。
6. 编译两份 PDF，检查每页行数。

```bash
cd software_copyright
bash ../softcopy-toolkit/compile.sh "$(pwd)/document.tex"
bash ../softcopy-toolkit/compile.sh "$(pwd)/source-code.tex"
```

## 环境

需要 XeLaTeX 及中文字体。Ubuntu 示例：

```bash
sudo apt install texlive-xetex texlive-lang-chinese texlive-fonts-recommended \
                 texlive-latex-extra texlive-science poppler-utils
pip install -r requirements.txt
```

Windows 可用已安装的 TeX Live；`easybook.cls` 系列模板文件已随仓库提供，无需额外安装。

## 交存要点（以官方最新指引为准）

- 说明书与源程序都是前、后各连续30页；不足60页全交。
- 源程序每页不少于50行，文档每页不少于30行。
- 申请表、说明书封面、源码页眉的软件全称与版本号必须一致；界面截图上的名称也要一致。
- 不虚构内容凑篇幅；总量不足就全交。

## 许可

本仓库自有内容采用 MIT 许可，见 `LICENSE`。`easybook.cls`、`easybase.sty`、`eb-tcolorbox.cfg` 为第三方文件，采用 LaTeX Project Public License，见 `THIRD-PARTY-NOTICES.md`，请勿修改。
