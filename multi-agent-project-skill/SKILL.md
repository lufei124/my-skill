---
name: multi-agent-project-skill
description: 当软件或产品项目可能被多个 AI Agent 并发编辑、可能在任意时刻被交接、或需要不依赖聊天记录即可持久化的任务状态、文件归属、Git 隔离、审查、集成与恢复时使用本 skill。也用于初始化一个可被 AI 协作开发的项目骨架（入口文档、长期文档、可复用 skills、协作簿记、技术栈基线）。适用于多 Agent 协作、Agent 接管、并行开发、任务交接、共享仓库、worktree 使用、文件冲突、工作中断、跨 Agent 审查或新项目初始化等场景。
---

# 多 Agent 项目协作

## 目标

让一个项目可以安全地被多个 AI Agent 并行编辑，或在任意时刻由另一个 Agent 接手。仓库是持久的事实来源；聊天上下文是临时的。

## 不可妥协的规则

1. 编辑前先读取项目状态。
2. 改动文件前先认领任务。
3. 多个 Agent 并行时，每个进行中的任务使用一个独立分支或 Git worktree。
4. 编辑前声明预期的文件范围。
5. 不得编辑被其他任务实时持有的文件，除非是在执行显式的集成或接管。
6. 改动保持最小，且仅限于已认领的任务范围内。
7. 永不擦除、重置、重新格式化或覆盖其他 Agent 未合并的成果。
8. 未真正执行过的测试，绝不得声称其已通过。
9. 除非用户或协调 Agent 明确要求，否则不得提交或推送。
10. 工作一旦暂停、易主、受阻、进入审查或完成，都要更新持久状态。

不得运行此类破坏性命令：

```bash
git reset --hard
git clean -fd
git push --force
```

## 项目骨架

一个可被多个 Agent 安全协作的项目，按以下分层组织（仓库是持久的事实来源；聊天上下文是临时的）：

```text
<project>/
├── AGENTS.md                 # 统一入口（所有 AI 平台共同入口，平台文件只链接不复制规则）
├── CLAUDE.md                 # 极简指针，指向 AGENTS.md
├── README.md
├── .gitignore                # 按技术栈生成
├── docs/                     # 长期文档层
│   ├── PROJECT_CONTEXT.md    # 问题/用户/流程/阶段/约束/不做
│   ├── ARCHITECTURE.md       # 模块/数据流/依赖边界
│   ├── DEVELOPMENT_RULES.md  # 强制/推荐/例外 + 代码-文档同步门禁 + 任务规模分级
│   ├── TESTING.md            # 测试策略与命令
│   ├── DECISIONS.md          # D-XXX 决策记录
│   └── GLOSSARY.md           # 术语表
├── skills/                   # 可复用方法层（九段式 skill）
├── .agent/                   # 多 Agent 协作簿记层（本 skill 的差异化核心）
│   ├── PROJECT_STATE.md
│   ├── TASK_BOARD.md
│   ├── FILE_LOCKS.md
│   ├── TASK_HANDOFF.md
│   ├── AGENTS_REGISTRY.md    # Agent 注册表
│   ├── decisions/            # ADR
│   ├── handoffs/             # 归档的交接记录
│   └── task-ids/             # 任务 ID 原子占位目录
└── .github/workflows/ci.yml  # 按技术栈生成
```

若骨架尚不存在，运行初始化器：

```bash
python <skill-path>/scripts/init_workspace.py <project-root>
```

初始化器从 `assets/`（单一模板真相源）读取模板，按技术栈探测结果渲染占位符并写入。技术栈探测：`package.json` -> node；`pyproject.toml` / `requirements.txt` -> python；否则 generic（生成占位骨架，由首个 Agent 补齐命令）。常用选项：`--dry-run`（预览不落盘）、`--stack {node,python,generic}`（覆盖探测）、`--force`（覆盖已有文件，慎用）、`--init-git`（非仓库时执行 `git init`）。

初始化器不得覆盖已有文件，除非被 `--force` 明确要求。模板的唯一真相源是 `assets/`，修改模板应直接改 `assets/` 下的文件，不要改脚本内嵌字符串（脚本不含任何内嵌模板）。

## 运行模式

判断当前所处模式，并遵循对应流程：

- **初始化（Initialize）**：创建缺失的状态文件并检视仓库。
- **认领（Claim）**：选定或创建一个任务，登记归属、分支、范围、依赖与验收标准。
- **执行（Execute）**：仅在已认领范围内工作，并维护一个可恢复的简短检查点。
- **检查点（Checkpoint）**：在上下文变长或变得不确定之前，记录当前进度。
- **交接（Handoff）**：让未完成或已完成的工作能被另一个 Agent 独立理解。
- **接管（Takeover）**：继续之前，先依据 Git 与测试校验另一个 Agent 的交接说明。
- **审查（Review）**：以对抗心态检查，不默认实现是正确的。
- **集成（Integrate）**：按依赖顺序合并并行工作，解决意图冲突，而不只是文本冲突。

### 初始化流程（Initialize）

初始化一个新项目或为已有项目补齐骨架时：

1. **探测技术栈**：检视目标目录是否存在 `package.json` / `pyproject.toml` / `requirements.txt`；不确定时用 `--dry-run` 先预览。
2. **运行初始化器**：`python <skill-path>/scripts/init_workspace.py <project-root>`。已有文件默认保留；若目标已有 `AGENTS.md` / `CLAUDE.md`，保留并检查是否指向骨架文档，必要时建议合并而非覆盖。
3. **检视生成物**：确认入口层（AGENTS.md/CLAUDE.md/README.md）、docs/、skills/、`.agent/`、技术栈文件（`.gitignore` + `ci.yml`）均已就位。
4. **填写项目上下文**：补齐 `docs/PROJECT_CONTEXT.md` 的最小节（解决的问题 / 目标用户 / 技术栈），并把 `AGENTS.md` 的技术栈段与命令段补全。
5. **登记 Agent 身份**：在 `.agent/AGENTS_REGISTRY.md` 登记首个 Agent；若由你主导，在 `TASK_BOARD.md` 顶部 `Coordinator:` 行声明。
6. **创建首个任务**：若技术栈为 generic 回退，首个任务默认是「补齐 `docs/TESTING.md` 与 `AGENTS.md` 的命令段」；否则首个任务由用户目标决定。按「任务 ID 原子分配」取号。
7. **Git**：若非仓库，建议 `git init`（或加 `--init-git`）；`.agent/` 须纳入版本控制。

## 开工流程

编辑之前：

1. 如存在则读取：
   - `AGENTS.md`（统一入口）
   - `docs/PROJECT_CONTEXT.md`
   - `docs/ARCHITECTURE.md`
   - `docs/DEVELOPMENT_RULES.md`
   - `.agent/PROJECT_STATE.md`
   - `.agent/TASK_BOARD.md`
   - `.agent/FILE_LOCKS.md`
   - `.agent/AGENTS_REGISTRY.md`
   - `.agent/TASK_HANDOFF.md`
   - 相关的 `.agent/decisions/`
   - 相关的 `.agent/handoffs/`
   - 与任务相关的 `docs/`（如 TESTING.md、DECISIONS.md、GLOSSARY.md）和 `skills/`
2. 运行：

```bash
git status --short
git branch --show-current
git diff --stat
git log -10 --oneline
```

3. 确立并陈述：

```text
Agent identity:
Current task:
Current task state:
Other active tasks:
Existing uncommitted changes:
Files currently owned by others:
Planned file scope:
Acceptance criteria:
```

4. 若存在无法解释的未提交改动，予以保留。不得清理或覆盖。

## Agent 注册与协调者

- 首次认领任务前，必须在 `.agent/AGENTS_REGISTRY.md` 登记唯一身份（Agent ID / 平台 / 角色 / 首次登记 / 最近活跃）。同一平台多会话用序号后缀区分，如 `claude-20260801-01`。
- 角色词汇：`coordinator`（协调者）/ `implementer`（实施者）/ `reviewer`（审查者）/ `integrator`（集成者）。
- 每次写检查点或更新状态时刷新「最近活跃」；超过 4 小时未活跃可被提请检视（见陈旧判定）。
- 协调者由用户指定，或首个完成初始化的 Agent 自荐，并在 `.agent/TASK_BOARD.md` 顶部 `Coordinator:` 行声明。
- 协调者职责：骨架初始化、撞号仲裁、STALE 最终判定、集成执行。提交/推送批准权仍在用户，不因协调者角色而转移。

## 任务认领协议

`.agent/TASK_BOARD.md` 中每个任务条目须包含：

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

合法状态：

```text
BACKLOG
CLAIMED
IN_PROGRESS
BLOCKED
READY_FOR_REVIEW
CHANGES_REQUESTED
READY_TO_INTEGRATE
DONE
ABANDONED
```

修改文件之前：

- 认领一个无人持有的任务，或显式接管一个已废弃/陈旧的任务。
- 记录唯一的 Agent 身份标识，例如 `codex-20260730-01`。
- 记录预期会改动的确切文件或目录。
- 当工作能干净拆分时，优先拆成独立任务。

### 任务 ID 原子分配

多个 Agent 并发认领时，靠文件系统原子操作避免 TASK-NNN 撞号：

1. 读取 `.agent/TASK_BOARD.md`，取已用最大编号 N。
2. 候选 ID = `TASK-(N+1)`，执行 `mkdir .agent/task-ids/TASK-(N+1)`（POSIX `mkdir` 是原子的）。
3. 若目录已存在（撞号），编号 +1 重试，直到 `mkdir` 成功。
4. 占位成功后，立即在 `TASK_BOARD.md` 写入完整任务行（含 Owner、Status、Scope），再开始动工。
5. 占位目录 `.agent/task-ids/TASK-NNN` 永不删除，作为已用编号的持久记录。

撞号时，后到者不得覆盖先到者已写入的看板行；后到者换用下一可用编号并在交接记录中说明。

## 并行工作协议

多个 Agent 同时工作时：

1. 使用独立分支或 worktree。文件锁不替代 Git 隔离。
2. 优先选择不重叠的文件和模块。
3. 编辑之前，在 `.agent/FILE_LOCKS.md` 登记预期的归属。
4. 一个锁须包含：

```text
Path or glob:
Task ID:
Owner agent:
Branch/worktree:
Reason:
Acquired at:
Last updated:
State: ACTIVE | RELEASED | STALE | TAKEOVER_PENDING
```

5. 若两个任务需要同一个文件：
   - 尽可能按文件拆分工作；
   - 将任务排序依次执行；或
   - 指派一个集成 Agent 来执行该共享文件改动。
6. 绝不靠盲目选取整版本来解决冲突。
7. 并行期间不做全仓库级别的格式化，除非这是被显式隔离出来的任务。

### worktree 操作约定

```bash
# 在主工作区为任务创建隔离 worktree（放在主仓库的兄弟目录，不嵌套）：
git worktree add ../<repo>-task-042 -b agent/<agent-id>/TASK-042-<slug>
cd ../<repo>-task-042
# ……工作……
# 完成或移交后清理（保留分支）：
git worktree remove ../<repo>-task-042
```

约定：worktree 一律放在主仓库的兄弟目录，命名 `<repo>-task-<NNN>`；分支命名 `agent/<agent-id>/TASK-<NNN>-<slug>`。worktree 不是协作状态的替代--`.agent/` 簿记仍须更新。

### `.agent/` 的 Git 策略

`.agent/` 是跨 Agent 共享的事实来源，须提交到主分支（不要加入 `.gitignore`）。

- 簿记文件设计为追加友好：`TASK_BOARD.md`、`FILE_LOCKS.md` 追加行；`handoffs/` 追加归档文件；`task-ids/` 追加占位目录。
- 使用 worktree 时：代码改动在 worktree 内进行；`.agent/` 的簿记更新基于最新主分支进行，或随代码合并一并合回主分支。避免两个分支同时编辑 `TASK_BOARD.md` 的同一区域。
- 冲突处理：追加型文件保留双方行后人工去重；`TASK_HANDOFF.md` 冲突以最新「更新时间」为准，并合并未完成的待办事项。
- 未经用户或协调 Agent 授权，不 push `.agent/` 或任何分支。

## 陈旧锁与接管协议

仅当工作明显被废弃、原 Agent 不可达、或协调 Agent/用户授权接管时，才可将一个锁视为陈旧。

### 陈旧判定（TTL）

ACTIVE 锁须随每次检查点刷新 `Last updated`；连续工作超过 60 分钟未写检查点也应刷新。`Last updated` 距今超过 4 小时的锁可被任何 Agent 提请检视，但标记 `STALE` 仍须满足以下三者之一：

- 原分支无进行中迹象（无提交、无检查点更新）；
- 原 Agent 在 `.agent/AGENTS_REGISTRY.md` 标记为不可达；
- 协调者或用户授权接管。

TTL 只是触发检视的信号，**不自动释放锁**--自动释放会破坏「永不擦除他人成果」原则。

接管之前：

1. 检视原分支/worktree、`git status`、`git diff` 以及最近的交接记录。
2. 将旧锁标记为 `STALE` 或 `TAKEOVER_PENDING`；不要删除其历史。
3. 记录：

```text
Previous owner:
New owner:
Takeover reason:
State observed at takeover:
Uncommitted changes preserved:
Verification performed:
```


4. 从已校验的状态继续，而不是重做已完成的工作。

## 执行与检查点协议

工作期间：

- 仅修改已声明的范围。
- 避免无关的重构、依赖升级、schema 变更、API 变更或全局格式化。
- 若范围必须扩大，在继续前先更新任务与锁。
- 在任何重大里程碑之后或停止之前，在 `.agent/TASK_HANDOFF.md` 保存一个可恢复的检查点。
- 将重要的架构、API、数据或业务规则决策记录到 `.agent/decisions/ADR-XXXX-title.md`。

检查点结构如下：

```text
Task ID:
Owner agent:
Current branch/worktree:
Current status:
Completed:
In progress:
Files changed:
Current code/runtime state:
Tests run and exact results:
Known failures:
Next concrete step:
Do not overwrite:
Updated at:
```

## 测试协议

运行与项目相关的检查，例如测试、lint、类型检查、构建、迁移或手动流程。

记录：

```text
Command:
Result: PASS | FAIL | NOT_RUN
Relevant output:
Reason if not run:
Manual verification:
```

规则：

- 仅在核实后，才能将既有失败标记为既有失败。
- 不得删除或弱化测试以让任务通过。
- 不得在仍有未解决必需检查的情况下将任务标记为 `DONE`。

## 交接协议

下列情况必须交接：

- 工作完成；
- 工作在完成前暂停；
- 另一个 Agent 必须接续；
- 任务受阻；
- 请求审查；
- 请求集成；
- 上下文开始变得不可靠。

更新 `.agent/TASK_HANDOFF.md` 并归档一份副本到：

```text
.agent/handoffs/YYYY-MM-DD-HHMM-task-id-agent-id.md
```

一份交接须包含：

```text
# Task handoff

## Identity
Task ID:
Task title:
Outgoing agent:
Intended next role/agent:
Branch/worktree:
Status:

## Completed
- 具体已完成的工作
- 已满足的验收标准

## Changed files
- path: 改了什么以及为什么

## Documentation updated
- 路径：更新了什么；或「无」

## Documentation not updated (and why)
- 路径：理由；或「无」

## Current position
- 工作停止的确切位置
- 当前运行/构建状态

## Decisions
- 已确认的决策
- ADR 引用
- 在没有新证据前不应重开的决策

## Verification
- 已运行的命令
- 确切的通过/失败结果
- 未运行的检查及其原因

## Remaining work
1. 下一步具体动作
2. 之后的动作

## Risks and known issues
- 已知 bug
- 可能的回归
- 冲突或依赖

## Takeover instructions
1. 先读哪些文件
2. 先运行哪些命令
3. 要检查的分支/worktree
4. 不得覆盖的工作
5. 预期的下一个交付物
```

## 接管流程

接手一方不得盲目信任交接说明。

1. 阅读交接记录与相关 ADR。
2. 检视 Git 状态与实际 diff。
3. 在可行时执行交接中所述的验证。
4. 将文档记录的状态与仓库实际状态进行对比。
5. 在编辑之前先记录差异。
6. 更新任务归属、状态、锁与当前交接记录。
7. 从第一个未核实或未完成的步骤继续。

接管回复以如下格式开头：

```text
Taken-over task:
Verified completed work:
Verified unfinished work:
State discrepancies:
Preserved changes:
Next action:
Planned scope:
```

## 审查流程

以对抗心态审查。不要默认作者或上一个 Agent 是正确的。

检查：

- 需求与验收标准；
- 边界情况与失败状态；
- 回归与意外的行为变更；
- API、schema、权限、安全、性能与数据风险；
- 缺失或薄弱的测试；
- 不必要的范围扩张；
- 代码、任务状态与交接记录之间的一致性。

问题分级：

```text
P0: 发布阻断级的安全、数据、资金或破坏性故障
P1: 核心功能失败或高概率回归
P2: 一般正确性、UX 或可维护性问题
P3: 可选改进
```

审查 Agent 通常应先报告问题。仅在被显式指派修复任务或集成角色时才修改代码。

## 集成流程

集成 Agent 必须：

1. 阅读每个任务的交接记录与验收标准。
2. 独立检视每个分支的 diff。
3. 确认任务范围内没有夹带意外改动。
4. 按依赖顺序合并。
5. 通过理解双方意图来解决冲突。
6. 先运行相关模块检查，再进行更广的回归检查。
7. 更新任务状态、释放锁、刷新项目状态，并撰写集成交接记录。

不得仅因 Git 没有产生文本冲突就判定集成完成。

## 决策记录

当变更架构、API、schema、共享行为、依赖或跨模块规则时，创建 ADR。

使用 `.agent/decisions/ADR-XXXX-title.md`：

```text
# Decision

Status: proposed | accepted | superseded
Date:
Owners:
Related tasks:

## Context

## Options considered

## Decision

## Rationale

## Consequences

## Risks

## Rollback
```

## 完成标准

只有当以下各项均成立时，才可将任务标记为 `DONE`：

```text
[ ] 验收标准已满足
[ ] 改动保持在声明范围内，或已记录范围扩张
[ ] 保留了其他 Agent 的成果
[ ] 必需检查确已运行并已记录
[ ] 任务条目为最新
[ ] 文件锁已释放
[ ] 项目状态为最新
[ ] 交接记录为最新且已归档
[ ] 重要决策有对应的 ADR
[ ] 审查/集成要求已满足
[ ] 用户或协调 Agent 已批准所请求的提交/推送
```

否则使用 `IN_PROGRESS`、`BLOCKED`、`READY_FOR_REVIEW`、`CHANGES_REQUESTED` 或 `READY_TO_INTEGRATE`。

## 响应行为

面向用户的更新保持简短。执行时，仅报告有意义的里程碑、发现的冲突、失败的检查、需要决策的事项与最终状态。除非被要求，否则不要倾倒内部簿记信息。