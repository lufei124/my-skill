# my-skill

一组可复用的 Claude Code Skill 集合。每个子目录都是一个独立、可移植的 Skill，可以直接放入项目或按路径引用其 `SKILL.md`。

## Skill 汇总

| Skill | 一句话说明 |
| --- | --- |
| [`multi-agent-project-skill`](multi-agent-project-skill) | 多 Agent 并行协作与交接协议，用仓库内 `.agent/` 目录持久化任务状态 |
| [`research-workflow`](research-workflow) | 领域无关的深度调研工作流，多 Agent 虚拟团队产出结构化调研报告 |
| [`subsystem-research-workflow`](subsystem-research-workflow) | 游戏/MUD 子系统深度调研（`research-workflow` 的游戏专用前身） |

### `multi-agent-project-skill`

让软件/产品项目能安全地被多个 AI Agent 并行编辑，或在任意时刻交接给另一个 Agent 继续。核心思想是仓库本身（而非聊天记录）才是持久的事实来源：在项目中引入 `.agent/` 目录，存放任务看板、文件锁、交接状态与决策记录（ADR），任何 Agent 只需读取仓库即可恢复完整上下文。涵盖任务认领、文件锁、分支/worktree 隔离、检查点交接、对抗式接管校验与集成审查等协议。

初始化目标项目：

```bash
python multi-agent-project-skill/scripts/init_workspace.py /path/to/your-project --add-agents-md
```

详见 [`multi-agent-project-skill/README.md`](multi-agent-project-skill/README.md) 与 [`multi-agent-project-skill/SKILL.md`](multi-agent-project-skill/SKILL.md)。

### `research-workflow`

对项目中的某个子系统、模块或流程进行深度源码调研与设计批判，领域无关。先通过 Grilling 强制对齐范围/目标/团队/产出，再组织多 Agent 虚拟调研团队，并行产出原始素材、视角化 stories、设计可选方案、红队对抗与最终汇总，保存到 `.scratch/research/NN-topic-name/`。内置 `game-mud` 与 `software-system` 领域预设，也可无预设纯通用运行；默认不自动 commit。

创建调研骨架：

```bash
python research-workflow/scripts/create_research_skeleton.py auth-module --preset software-system
```

详见 [`research-workflow/README.md`](research-workflow/README.md) 与 [`research-workflow/SKILL.md`](research-workflow/SKILL.md)。

### `subsystem-research-workflow`

`research-workflow` 的游戏/MUD 专用前身，保留可用。针对任务、战斗、经济、门派等子系统做深度调研：Grilling 对齐 + 编号主题目录 + 多 Agent Workflow（一手考古 / 机制抽象 / 现代评审 / 红队对抗 / 评审委员会汇总），产出源码清单、三层 User Stories、引擎设计灵感与最终汇总。其游戏领域精华已迁入 [`research-workflow/references/domain-presets/game-mud.md`](research-workflow/references/domain-presets/game-mud.md)。详见 [`subsystem-research-workflow/SKILL.md`](subsystem-research-workflow/SKILL.md)。

## 使用方式

这里的 skill 通过引用其目录来消费。在目标项目中，可以：

1. **按路径引用** —— 让你的 Agent 指向某个 skill 的 `SKILL.md` 以遵循其协议；或
2. **注入协作能力** —— 运行初始化脚本，让目标项目自带 `.agent/` 状态和 `AGENTS.md`。

新增 skill 的约定：新建一个 `<skill-name>/` 目录，内含 `SKILL.md`（frontmatter + 行为守则），并在上方汇总表中登记一行。
