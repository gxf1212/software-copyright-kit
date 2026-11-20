# Prompt 库

给 AI 用的分步提示词。按顺序使用，也可以让 AI 读仓库根目录的 `CLAUDE.md` 一次跑完全程。

| 文件 | 用途 |
|------|------|
| `01-write-handbook.md` | 写说明书各章（引言、安装、使用、架构、数据、附录） |
| `02-write-source-code.md` | 准备源码副本、写源程序文档、编译验收 |
| `03-write-application.md` | 填申请表（字数限制、命名一致性） |
| `04-check-and-polish.md` | 与真实源码一致性核对、去 AI 味、版面验收 |
| `writing-style.md` | 中文写作规范（去 AI 味、标点空格、术语；软著、论文、推文通用） |

用法：把对应文件的内容整段作为 AI 指令，并在前面附上你的真实软件信息（软件名、版本、功能、源码路径、截图）。AI 会据此改写 `software_copyright/` 里的模板文件。

另见 `softcopy-toolkit/prompts.md`：工具链自带的完整提示词与约定（文档结构、LaTeX 规范、登记合规要点），是这些分步 prompt 的原始出处，保持原样未改。
