# 操作指南

面向在本项目里使用 `multi-agent-project-skill` 的产品经理、开发与协作 Agent。覆盖初始化、认领、交接、接管、陈旧判定与集成六件日常事。安装与升级见 [install-guide.md](install-guide.md)；完整协议见 [SKILL.md](SKILL.md)。

> 注：本文件是 skill 仓库内的操作文档副本。初始化目标项目后，目标项目里不会有本文件的副本（本 skill 不向目标项目写操作指南）；需要时直接读本 skill 仓库的此文件。

## 1. 初始化一个项目

```bash
# 预览将生成的文件（不落盘）
python <skill-path>/scripts/init_workspace.py /path/to/project --dry-run
# 实际生成骨架
python <skill-path>/scripts/init_workspace.py /path/to/project
```

技术栈自动探测：`package.json` -> node；`pyproject.toml`/`requirements.txt` -> python；否则 generic（生成占位骨架，由首个 Agent 补齐命令）。可用 `--stack {node,python,generic}` 覆盖探测，`--init-git` 在非仓库时执行 `git init`，`--force` 覆盖已有文件（慎用）。

生成后：

1. 补齐 `docs/PROJECT_CONTEXT.md` 的最小节（解决的问题 / 目标用户 / 技术栈）。
2. 把 `AGENTS.md` 的技术栈段与命令段补全（占位符已按栈预填）。
3. 在 `.agent/AGENTS_REGISTRY.md` 登记首个 Agent 身份；若由你主导，在 `.agent/TASK_BOARD.md` 顶部 `Coordinator:` 行声明。
4. 创建首个任务（见下「认领一个任务」）。generic 回退时，首个任务默认是「补齐 `docs/TESTING.md` 与 `AGENTS.md` 的命令段」。
5. `.agent/` 必须提交到版本控制（协作状态需共享）。

## 2. 认领一个任务

1. 读取 `AGENTS.md` 与 `.agent/*`，以及与任务相关的 `docs/` 和 `skills/`。
2. 检视 Git：`git status --short`、`git branch --show-current`、`git diff --stat`、`git log -10 --oneline`。
3. 首次在本项目工作：在 `.agent/AGENTS_REGISTRY.md` 登记身份（Agent ID / 平台 / 角色 / 首次登记 / 最近活跃）。
4. **原子取号**：读看板取最大编号 N，`mkdir .agent/task-ids/TASK-(N+1)`（撞号则 +1 重试）；占位成功后立即在 `TASK_BOARD.md` 写完整任务行，再动工。占位目录永不删除。
5. 创建或切换到隔离分支/worktree：`git worktree add ../<repo>-task-042 -b agent/<agent-id>/TASK-042-<slug>`。
6. 在 `.agent/FILE_LOCKS.md` 登记预期的文件归属。
7. 在声明范围内执行。

## 3. 检查点（工作中）

工作期间仅修改已声明范围；范围扩大先更新任务与锁。在重大里程碑后或停止前，在 `.agent/TASK_HANDOFF.md` 保存可恢复检查点（Task ID / 当前状态 / 已完成 / 进行中 / 改动文件 / 测试结果 / 下一步 / 不得覆盖）。重要决策记到 `.agent/decisions/ADR-XXXX-title.md`。

## 4. 暂停或退出（交接）

1. 运行可用的测试。
2. 更新 `.agent/TASK_HANDOFF.md`（含「已更新文档」「无需更新文档及理由」两节）。
3. 归档交接记录到 `.agent/handoffs/YYYY-MM-DD-HHMM-task-id-agent-id.md`。
4. 更新任务状态与 `.agent/PROJECT_STATE.md`。
5. 刷新 `AGENTS_REGISTRY.md` 的「最近活跃」。
6. 工作进行中则保留活动锁；已完成则释放。

## 5. 另一个 Agent 接管

1. 依据 Git 校验交接记录（不盲信说明）。
2. 保留未提交的工作。
3. 运行交接中所述的检查。
4. 记录文档状态与仓库实际状态的差异。
5. 转移任务与锁的归属（旧锁标 `STALE`，**不删历史**）。
6. 从第一个未完成或未核实的步骤继续。

## 6. 陈旧锁检视

`FILE_LOCKS.md` 中 ACTIVE 锁的 `Last updated` 超过 **4 小时**可被提请检视，但标记 `STALE` 仍须满足三者之一：原分支无进行中迹象 / 原 Agent 在注册表标记不可达 / 协调者或用户授权。**TTL 不自动释放锁**（保「永不擦除他人成果」原则）。ACTIVE 锁须随每次检查点刷新 `Last updated`，连续工作超 60 分钟也须刷新。

## 7. 审查与集成

- **审查**：以对抗心态检查需求与验收、边界与失败、回归、API/schema/安全/性能/数据风险、缺失测试、范围扩张、代码与状态/交接一致性。问题分级 P0/P1/P2/P3。审查 Agent 通常只报告问题，仅在被显式指派修复/集成时才改代码。
- **集成**：读每个任务的交接与验收 -> 独立检视各分支 diff -> 确认无夹带 -> 按依赖顺序合并 -> 理解双方意图解决冲突（不只看文本冲突）-> 先模块检查再广回归 -> 更新任务状态、释放锁、刷新项目状态、写集成交接。**不得仅因 Git 无文本冲突就判定集成完成。**

## 8. 多个 Agent 需要同一共享文件

不要同时编辑。择一：将任务排序依次执行；先拆分该文件；将该共享文件改动指派给一个专门的集成任务。

## 9. 完成标准

任务标记 `DONE` 前须全部成立：验收标准满足；改动在声明范围内或已记录扩张；保留他人成果；必需检查已运行并记录；任务条目最新；文件锁已释放；项目状态最新；交接记录最新且已归档；重要决策有 ADR；审查/集成要求已满足；用户或协调 Agent 已批准所请求的提交/推送。

## 不可妥协规则（速查）

1. 编辑前先读项目状态。2. 改文件前先认领任务。3. 并行任务用独立分支/worktree。4. 编辑前声明文件范围。5. 不编辑他人实时持有的文件（除非显式集成/接管）。6. 改动最小且限于认领范围。7. **永不擦除、重置、重新格式化或覆盖其他 Agent 未合并的成果**。8. 未真正运行的测试不得声称通过。9. 除非用户或协调 Agent 明确要求，不提交或推送。10. 暂停/易主/受阻/审查/完成都更新持久状态。

禁用：`git reset --hard`、`git clean -fd`、`git push --force`。
