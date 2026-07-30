# 工作流参考

## 新项目

```bash
python scripts/init_workspace.py /path/to/project --add-agents-md
```

随后在 `.agent/TASK_BOARD.md` 中创建首个任务，选定分支/worktree，并记录文件范围。

## Agent 开始一个任务

1. 读取 `AGENTS.md` 与 `.agent/*`。
2. 检视 Git 状态与 diff。
3. 认领一个任务。
4. 创建或切换到隔离的分支/worktree。
5. 添加文件锁。
6. 在范围内执行。

## Agent 暂停或退出

1. 运行可用的测试。
2. 更新 `.agent/TASK_HANDOFF.md`。
3. 将交接记录归档到 `.agent/handoffs/`。
4. 更新任务与项目状态。
5. 若工作仍在进行则保留活动锁；若工作已完成则释放。

## 另一个 Agent 接管

1. 依据 Git 校验交接记录。
2. 保留未提交的工作。
3. 运行交接中所述的检查。
4. 记录差异。
5. 转移任务与锁的归属。
6. 从第一个未完成或未核实的步骤继续。

## 多个 Agent 需要同一个共享文件

不要让它们同时编辑。从以下方式中择一：

- 将任务排序依次执行；
- 先拆分该文件；
- 将该共享文件的改动指派给一个专门的集成任务。