# 文件锁

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