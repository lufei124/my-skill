# my-skill

一组可复用的 Claude Code Skill 集合。每个子目录都是独立、可移植的 Skill，可以直接放入项目或按路径引用。

## 已收录的 Skill

### [`multi-agent-project-skill`](multi-agent-project-skill)

**`multi-agent-project-coordination`** —— 让软件/产品项目能够安全地被多个 AI Agent 并行编辑，或在任一时刻被交接、由另一个 Agent 接手继续。

仓库本身（而非聊天记录）才是持久的事实来源（source of truth）。该 skill 会在项目中引入一个 `.agent/` 目录，存放任务看板、文件锁、交接状态与决策记录，任何 Agent 只需读取仓库就能恢复完整上下文。

**协调的内容包括：**

- 任务认领与归属管理（避免两个 Agent 悄然编辑同一个任务）
- 针对同一仓库并行开发的文件锁机制
- Git 隔离 —— 每个进行中的任务使用独立分支或 worktree
- 检查点与结构化交接，让工作能在上下文丢失或更换 Agent 后继续
- 对抗式接管校验（接手方不会盲目信任交接说明）
- 审查与集成流程，解决的是「意图冲突」而非仅仅是文本冲突
- 针对跨模块决策的架构决策记录（ADR）

**快速开始 —— 初始化一个项目：**

```bash
python multi-agent-project-skill/scripts/init_workspace.py /path/to/your-project --add-agents-md
```

该命令会创建以下结构，且默认不会覆盖已有文件：

```text
.agent/
├── PROJECT_STATE.md
├── TASK_BOARD.md
├── FILE_LOCKS.md
├── TASK_HANDOFF.md
├── decisions/
└── handoffs/
```

详细的协议规则见 [`multi-agent-project-skill/README.md`](multi-agent-project-skill/README.md)，完整的 Agent 行为守则见 [`multi-agent-project-skill/SKILL.md`](multi-agent-project-skill/SKILL.md)。

### [`research-workflow`](research-workflow)

**`research-workflow`** —— 领域无关的深度调研工作流。对项目中的某个子系统、模块或流程进行源码调研与设计批判。

先强制 Grilling 对齐范围/目标/团队/产出，再组织多 Agent 虚拟调研团队，并行产出原始素材、视角化 stories、设计可选方案、红队对抗与最终汇总，保存到 `.scratch/research/NN-topic-name/` 下。内置 `game-mud` 与 `software-system` 领域预设，也可无预设纯通用运行。默认不自动 commit。

**快速开始 —— 创建一个调研骨架：**

```bash
python research-workflow/scripts/create_research_skeleton.py auth-module --preset software-system
```

该命令会在 `.scratch/research/` 下创建带序号主题目录与 6 层子目录（`00-brief/` … `05-synthesis/`），并按预设把领域增量注入 `brief.md`。可用的 `--preset`：`game-mud`、`software-system`、`none`（默认）。

本 skill 是 [`subsystem-research-workflow`](subsystem-research-workflow) 的通用化版本，其游戏/MUD 精华迁入了 [`research-workflow/references/domain-presets/game-mud.md`](research-workflow/references/domain-presets/game-mud.md)。详见 [`research-workflow/README.md`](research-workflow/README.md) 与 [`research-workflow/SKILL.md`](research-workflow/SKILL.md)。

### [`subsystem-research-workflow`](subsystem-research-workflow)

**`subsystem-research-workflow`** —— 游戏/MUD 项目子系统深度调研（`research-workflow` 的游戏专用前身，保留可用）。通过 Grilling 对齐 + 编号主题目录 + 三阶段多 Agent Workflow（一手考古 / 机制抽象 / 现代评审 / 红队对抗 / 评审委员会汇总），产出源码清单、三层 User Stories、引擎设计灵感与最终汇总。详见 [`subsystem-research-workflow/SKILL.md`](subsystem-research-workflow/SKILL.md)。

## 仓库结构

```text
my-skill/
├── multi-agent-project-skill/      # 多 Agent 协作 skill
│   ├── SKILL.md                    # Agent 行为守则
│   ├── README.md                   # skill 专属文档
│   ├── scripts/
│   │   └── init_workspace.py       # 初始化 .agent/ 状态的脚本
│   ├── references/
│   │   ├── WORKFLOW.md             # 精简操作流程
│   │   └── EXAMPLES.md             # 并行开发与接管示例
│   └── assets/
│       └── project-state/
│           └── AGENTS.md           # 注入到目标项目的模板文件
├── research-workflow/              # 通用深度调研 skill
│   ├── SKILL.md                    # 通用行为守则
│   ├── README.md
│   ├── references/
│   │   ├── grilling-questions.md   # 通用 grilling 问题
│   │   ├── team-roles.md           # 通用角色原型
│   │   ├── output-structure.md     # 通用产出层级
│   │   ├── workflow-template.md    # Workflow 脚本模板
│   │   └── domain-presets/         # 领域预设（game-mud / software-system）
│   ├── scripts/
│   │   ├── create_research_skeleton.py   # 创建调研骨架（支持 --preset）
│   │   ├── grade_research_init.py        # 初始化评分
│   │   └── aggregate_benchmark.py        # benchmark 汇总
│   └── evals/evals.json
└── subsystem-research-workflow/    # 游戏/MUD 子系统调研 skill（research-workflow 的前身）
    ├── SKILL.md
    ├── references/
    ├── scripts/
    └── evals/evals.json
```

## 使用方式

这里的 skill 通过引用其目录来消费。在目标项目中，可以：

1. **按路径引用** —— 让你的 Agent 指向某个 skill 的 `SKILL.md` 以遵循其协议；或
2. **注入协作能力** —— 运行初始化脚本，让目标项目自带 `.agent/` 状态和 `AGENTS.md`。

新增 skill 的约定：新建一个 `<skill-name>/` 目录，内含 `SKILL.md`（frontmatter + 行为守则），并在上方目录列表中登记，index 一行即可。