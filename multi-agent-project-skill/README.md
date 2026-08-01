# Multi-Agent Project Skill

一个可移植的 Claude Code skill，面向那些可能被多个 AI Agent 并行编辑、或在任意时刻被交接的项目。它既初始化一个可被 AI 协作开发的项目骨架，也定义多 Agent 并行编辑、交接、审查与集成的协作协议。

## 内容

- `SKILL.md`：Agent 行为与协作协议守则。
- `scripts/init_workspace.py`：从 `assets/` 读取模板，为目标项目生成完整骨架（入口层 + docs + skills + `.agent/` + 技术栈基线）。默认不覆盖已有文件。
- `assets/`：**模板的唯一真相源**。修改模板直接改这里的文件，不要改脚本（脚本不含任何内嵌模板）。
  - `assets/skeleton/`：技术栈无关骨架，镜像目标项目路径。
  - `assets/stacks/{node,python,generic}/`：技术栈相关的 `.gitignore` 与 CI 模板。
- `references/WORKFLOW.md`：精简版操作流程。
- `references/EXAMPLES.md`：并行开发、接管、注册、撞号与陈旧锁判定示例。

## 初始化一个项目

```bash
# 预览将生成的文件（不落盘）
python /path/to/skill/scripts/init_workspace.py /path/to/project --dry-run
# 实际生成
python /path/to/skill/scripts/init_workspace.py /path/to/project
```

技术栈自动探测：`package.json` -> node；`pyproject.toml`/`requirements.txt` -> python；否则 generic（生成占位骨架，由首个 Agent 补齐命令）。

### 常用选项

- `--dry-run`：只打印计划，不写入。
- `--stack {node,python,generic}`：手动指定技术栈，覆盖探测。
- `--force`：覆盖已有文件（慎用）。
- `--init-git`：非 Git 仓库时执行 `git init`。

## 生成的骨架

```text
<project>/
├── AGENTS.md / CLAUDE.md / README.md      # 入口层（AGENTS.md 统一入口，平台文件只链接不复制规则）
├── .gitignore                              # 按技术栈生成
├── docs/                                   # 长期文档（PROJECT_CONTEXT / ARCHITECTURE / DEVELOPMENT_RULES / TESTING / DECISIONS / GLOSSARY）
├── skills/                                 # 5 个九段式 skill（requirement-review / feature-development / bug-fix / test-and-verify / task-handoff）
├── .agent/                                 # 多 Agent 协作簿记
│   ├── PROJECT_STATE.md / TASK_BOARD.md / FILE_LOCKS.md / TASK_HANDOFF.md / AGENTS_REGISTRY.md
│   ├── decisions/  handoffs/  task-ids/
└── .github/workflows/ci.yml                # 按技术栈生成
```

`.agent/` 必须提交到仓库（协作状态需共享）；三份 `.gitignore` 均不忽略它。

已有文件默认保留。仅在你确实打算替换内容时，才使用 `--force`。

## 设计原理

- **仓库是持久的事实来源；聊天上下文是临时的**。所有协作状态落到磁盘文件，不依赖对话记录。
- **模板单一真相源**：`assets/` 是唯一模板来源，脚本零内嵌字符串，消除双份漂移。
- **AGENTS.md 统一入口**：平台适配文件（CLAUDE.md 等）只链接不复制规则，避免多处维护漂移。
- **Git 隔离优先**：并行任务用独立分支/worktree，文件锁只是建议性协调记录。
- **保守主义**：默认不覆盖、不提交、不推送；禁用破坏性 Git 命令。
