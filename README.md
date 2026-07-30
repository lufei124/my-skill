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

## 仓库结构

```text
my-skill/
└── multi-agent-project-skill/      # 多 Agent 协作 skill
    ├── SKILL.md                    # Agent 行为守则
    ├── README.md                   # skill 专属文档
    ├── scripts/
    │   └── init_workspace.py       # 初始化 .agent/ 状态的脚本
    ├── references/
    │   ├── WORKFLOW.md             # 精简操作流程
    │   └── EXAMPLES.md             # 并行开发与接管示例
    └── assets/
        └── project-state/
            └── AGENTS.md           # 注入到目标项目的模板文件
```

## 使用方式

这里的 skill 通过引用其目录来消费。在目标项目中，可以：

1. **按路径引用** —— 让你的 Agent 指向某个 skill 的 `SKILL.md` 以遵循其协议；或
2. **注入协作能力** —— 运行初始化脚本，让目标项目自带 `.agent/` 状态和 `AGENTS.md`。

新增 skill 的约定：新建一个 `<skill-name>/` 目录，内含 `SKILL.md`（frontmatter + 行为守则），并在上方目录列表中登记，index 一行即可。