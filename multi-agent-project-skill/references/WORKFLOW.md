# 工作流参考

## 新项目（初始化）

```bash
# 预览将生成的文件（不落盘）
python <skill-path>/scripts/init_workspace.py /path/to/project --dry-run
# 实际生成骨架
python <skill-path>/scripts/init_workspace.py /path/to/project
# 可选：非 Git 仓库时一并 git init
python <skill-path>/scripts/init_workspace.py /path/to/project --init-git
```

初始化器自动探测技术栈（`package.json` -> node；`pyproject.toml`/`requirements.txt` -> python；否则 generic），生成入口层 + docs/ + skills/ + `.agent/` + 技术栈文件（`.gitignore` + `ci.yml`）。已有文件默认保留。

生成后：补齐 `docs/PROJECT_CONTEXT.md` 最小节与 `AGENTS.md` 技术栈段；在 `.agent/AGENTS_REGISTRY.md` 登记 Agent 身份；在 `.agent/TASK_BOARD.md` 创建首个任务（generic 回退时首个任务默认补齐 `docs/TESTING.md` 命令段）。

## Agent 开始一个任务

1. 读取 `AGENTS.md` 与 `.agent/*`，以及与任务相关的 `docs/` 和 `skills/`。
2. 检视 Git 状态与 diff。
3. 在 `.agent/AGENTS_REGISTRY.md` 登记身份（首次）。
4. 原子取号：`mkdir .agent/task-ids/TASK-NNN`（NNN = 看板最大编号 +1，撞号则 +1 重试）。
5. 在 `TASK_BOARD.md` 写入任务行；创建或切换到隔离的分支/worktree。
6. 在 `FILE_LOCKS.md` 登记预期的文件归属。
7. 在声明范围内执行。

## worktree 生命周期

```bash
# 创建（兄弟目录，不嵌套）：
git worktree add ../<repo>-task-042 -b agent/<agent-id>/TASK-042-<slug>
cd ../<repo>-task-042
# ……工作，期间在 .agent/ 更新簿记……
# 完成或移交后清理（保留分支）：
git worktree remove ../<repo>-task-042
```

`.agent/` 须提交到主分支；worktree 中的簿记更新基于最新主分支进行，或随代码合并一并合回。

## Agent 暂停或退出

1. 运行可用的测试。
2. 更新 `.agent/TASK_HANDOFF.md`（含「已更新文档」「无需更新文档及理由」两节）。
3. 将交接记录归档到 `.agent/handoffs/`。
4. 更新任务与 `PROJECT_STATE.md`。
5. 刷新 `AGENTS_REGISTRY.md` 的「最近活跃」。
6. 若工作仍在进行则保留活动锁；若工作已完成则释放。

## 另一个 Agent 接管

1. 依据 Git 校验交接记录。
2. 保留未提交的工作。
3. 运行交接中所述的检查。
4. 记录差异。
5. 转移任务与锁的归属（旧锁标 `STALE`，不删历史）。
6. 从第一个未完成或未核实的步骤继续。

## 陈旧锁检视

`FILE_LOCKS.md` 中 ACTIVE 锁的 `Last updated` 超过 4 小时可被提请检视，但标记 `STALE` 仍须满足：原分支无进行中迹象 / 原 Agent 不可达 / 协调者或用户授权，三者之一。TTL 不自动释放锁。

## 多个 Agent 需要同一个共享文件

不要让它们同时编辑。从以下方式中择一：

- 将任务排序依次执行；
- 先拆分该文件；
- 将该共享文件的改动指派给一个专门的集成任务。
