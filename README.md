# my-skill

一组可复用的 Claude Code Skill 集合。每个子目录都是一个独立、可移植的 Skill，可以直接放入项目、按路径引用其 `SKILL.md`，或整包安装为插件。

## Skill 汇总

| Skill | 一句话说明 |
| --- | --- |
| [`multi-agent-project-skill`](multi-agent-project-skill) | 多 Agent 并行协作与交接协议，用仓库内 `.agent/` 目录持久化任务状态 |
| [`research-workflow`](research-workflow) | 领域无关的深度调研工作流，多 Agent 虚拟团队产出结构化调研报告 |
| [`mobile-game-product-forge`](mobile-game-product-forge) | 移动游戏产品需求工坊：端到端编排调研、原型、PRD、评审、校验与交付 |

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

### `mobile-game-product-forge`

移动游戏产品需求工坊：把游戏想法、已确认原型或现有 PRD 转化为产品、设计、客户端、服务端、测试、数据和运营可执行的需求。主编排器按当前阶段只补齐缺失环节（调研 -> 原型适用性判断 -> PRD -> 动态评审 -> 校验 -> 可选飞书交付），绝不把推断伪装成已确认需求；下设 8 个子 Skill 覆盖调研、原型、PRD 撰写/评审、埋点设计、知识维护提案与发布，通过 JSON 状态（`00-stage-state.json`）与机器门禁贯穿全流程。因含子 Skill 与 `../../references/...` 相对引用，需整包安装而非单文件引用。

安装（Claude Code 插件，推荐）：

```bash
claude plugin marketplace add git@gitee.com:xianlan---shanghai-g/mobile-game-product-forge.git
claude plugin install mobile-game-product-forge@fairyland-forge
```

无插件环境可改用本地脚本软链：`bash mobile-game-product-forge/scripts/install.sh --agent claude`（也支持 `codex` / `cursor`）。安装后在目标项目调用 `$setup-mobile-game-product-forge` 初始化，再用 `$mobile-game-product-forge` 发起正式需求。

详见 [`mobile-game-product-forge/README.md`](mobile-game-product-forge/README.md) 与 [`mobile-game-product-forge/SKILL.md`](mobile-game-product-forge/SKILL.md)。

## 使用方式

各 skill 的消费方式略有不同，按其自身文档选择：

1. **按路径引用** —— 让你的 Agent 指向某个 skill 的 `SKILL.md` 以遵循其协议（如 `research-workflow`）；
2. **初始化目标项目** —— 运行脚本向目标项目注入状态目录与协作规则（如 `multi-agent-project-skill` 的 `.agent/`）。
3. **整包安装** -- 作为 Claude Code 插件或经 `scripts/install.sh` 软链到 skills 目录（如 `mobile-game-product-forge`，含子 Skill 与相对引用，需整包安装）。

新增 skill 的约定：新建一个 `<skill-name>/` 目录，内含 `SKILL.md`（frontmatter + 行为守则），并在上方汇总表中登记一行。
