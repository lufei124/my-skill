# 任务看板

Coordinator:（协调者 Agent ID，由用户指定或首个 Agent 自荐；留空表示暂无协调者）

> 新任务 ID 分配：读取本看板取最大编号 N，先 `mkdir .agent/task-ids/TASK-(N+1)` 原子占位（已存在则编号 +1 重试），占位成功后再写入本看板任务行。占位目录永不删除，作为已用编号记录。撞号时后到者不得覆盖先到者的看板行。

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
