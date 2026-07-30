#!/usr/bin/env python3
"""初始化持久化的多 Agent 项目状态，且默认不覆盖已有文件。"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict


TEMPLATES: Dict[str, str] = {
    "PROJECT_STATE.md": """# 项目状态

最后更新：
更新者：
当前版本/分支：
当前阶段：

## 已完成

- 暂无记录。

## 进行中

- 暂无记录。

## 待审查

- 暂无记录。

## 受阻

- 暂无记录。

## 已知问题与风险

- 暂无记录。

## 近期决策

- 暂无记录。

## 下一优先级

1. 定义下一个任务。
""",
    "TASK_BOARD.md": """# 任务看板

| Task ID | 标题 | Owner agent | Status | Branch/worktree | Allowed scope | Dependencies | 更新时间 |
|---|---|---|---|---|---|---|---|
| TASK-001 | 初始化多 Agent 项目状态 | unassigned | BACKLOG | - | `.agent/` | - | - |

## 任务详情模板

```text
Task ID:
Title:
Owner agent:
Status:
Branch/worktree:
Allowed scope:
Forbidden scope:
Dependencies:
Expected output:
Acceptance criteria:
Started at:
Updated at:
```
""",
    "FILE_LOCKS.md": """# 文件锁

锁是建议性的协调记录。并行 Agent 仍应使用独立的 Git 分支或 worktree。

| Path or glob | Task ID | Owner agent | Branch/worktree | 原因 | 获取时间 | 最后更新 | State |
|---|---|---|---|---|---|---|---|

合法状态：`ACTIVE`、`RELEASED`、`STALE`、`TAKEOVER_PENDING`。

## 接管历史模板

```text
Previous owner:
New owner:
Takeover reason:
State observed at takeover:
Uncommitted changes preserved:
Verification performed:
```
""",
    "TASK_HANDOFF.md": """# 当前任务交接

## 身份

Task ID:
Task title:
Outgoing/current agent:
Intended next role/agent:
Branch/worktree:
Status:
更新时间：

## 已完成

- 暂无记录。

## 已修改文件

- 暂无记录。

## 当前位置

- 未记录进行中的工作。

## 决策

- 暂无记录。

## 验证

| 命令/检查 | 结果 | 相关输出或未运行原因 |
|---|---|---|

## 剩余工作

1. 暂无记录。

## 风险与已知问题

- 暂无记录。

## 接管说明

1. 阅读 `.agent/PROJECT_STATE.md` 与 `.agent/TASK_BOARD.md`。
2. 检视 `git status`、`git diff` 以及相关分支。
3. 核实文档中记录的测试结果。
4. 保留所有无法解释的改动。
""",
}

ADR_TEMPLATE = """# 决策

Status: proposed
Date:
Owners:
Related tasks:

## 背景

## 备选方案

## 决策

## 理由

## 影响

## 风险

## 回滚
"""

HANDOFF_TEMPLATE = """# 任务交接

## 身份

Task ID:
Task title:
Outgoing agent:
Intended next role/agent:
Branch/worktree:
Status:

## 已完成

## 已修改文件

## 当前位置

## 决策

## 验证

## 剩余工作

## 风险与已知问题

## 接管说明
"""

AGENTS_SNIPPET = """# Agent 协作

本仓库可能被多个 AI Agent 并发编辑，或在任意时刻被交接。

编辑之前，使用 `multi-agent-project-coordination` skill，并阅读 `.agent/` 下的持久状态。

硬性规则：

- 改动文件前先认领任务。
- 并行任务使用独立的 Git 分支或 worktree。
- 记录预期的文件范围与活动锁。
- 保留无法解释的和未合并的改动。
- 暂停或转移工作前更新交接状态。
- 除非被明确要求，否则不得提交或推送。
"""


def write_file(path: Path, content: str, force: bool) -> str:
    if path.exists() and not force:
        return "保留"  # kept
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "已写入"  # written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--force", action="store_true", help="覆盖已有的受管模板文件")
    parser.add_argument(
        "--add-agents-md",
        action="store_true",
        help="仅在 AGENTS.md 缺失时创建一个精简版（配合 --force 可覆盖）",
    )
    args = parser.parse_args()

    root = Path(args.project_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        parser.error(f"项目根目录不是有效目录：{root}")

    state = root / ".agent"
    (state / "decisions").mkdir(parents=True, exist_ok=True)
    (state / "handoffs").mkdir(parents=True, exist_ok=True)

    results = []
    for name, content in TEMPLATES.items():
        results.append((state / name, write_file(state / name, content, args.force)))

    results.append(
        (
            state / "decisions" / "ADR-0000-template.md",
            write_file(state / "decisions" / "ADR-0000-template.md", ADR_TEMPLATE, args.force),
        )
    )
    results.append(
        (
            state / "handoffs" / "HANDOFF-template.md",
            write_file(state / "handoffs" / "HANDOFF-template.md", HANDOFF_TEMPLATE, args.force),
        )
    )

    if args.add_agents_md:
        results.append((root / "AGENTS.md", write_file(root / "AGENTS.md", AGENTS_SNIPPET, args.force)))

    print(f"已在以下位置初始化多 Agent 状态：{state}")
    for path, action in results:
        print(f"- {action}  {path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())