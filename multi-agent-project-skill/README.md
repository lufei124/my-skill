# Multi-Agent Project Coordination Skill

一个可移植的 skill，面向那些可能被多个 AI Agent 并行编辑、或在任意时刻被交接的项目。

## 内容

- `SKILL.md`：Agent 行为与协作协议守则
- `scripts/init_workspace.py`：初始化 `.agent/` 状态，且默认不会覆盖已有文件
- `references/WORKFLOW.md`：精简版操作流程
- `references/EXAMPLES.md`：并行开发与接管示例

## 初始化一个项目

```bash
python /path/to/skill/scripts/init_workspace.py /path/to/project --add-agents-md
```

该命令会创建：

```text
.agent/
├── PROJECT_STATE.md
├── TASK_BOARD.md
├── FILE_LOCKS.md
├── TASK_HANDOFF.md
├── decisions/
└── handoffs/
```

已有文件默认会被保留。仅在你确实打算替换内容时，才使用 `--force`。