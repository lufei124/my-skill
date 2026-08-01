# 示例

## 并行任务

```text
TASK-021: 支付 API
Owner: codex-20260730-01
Branch: agent/codex/TASK-021-payment-api
Allowed scope: server/payment/**, tests/payment/**
Status: IN_PROGRESS

TASK-022: 支付 UI
Owner: claude-20260730-01
Branch: agent/claude/TASK-022-payment-ui
Allowed scope: app/payment/**, test/payment/**
Depends on: TASK-021 API 契约
Status: CLAIMED
```

如果两者都需要 `shared/payment_types.ts`，则创建第三个由单一集成 Agent 拥有的任务，或将编辑排序执行。

## 中断任务的接管

```text
Previous owner: claude-20260730-01
New owner: codex-20260730-02
Takeover reason: 上一个会话在运行测试前结束
State observed: 三个已修改文件，无提交，单元测试未运行
Uncommitted changes preserved: 是
Verification performed: 已审阅 git diff；lint 通过；一个单元测试失败
```

接手方在修改代码之前先记录该失败。

## Agent 注册表登记

两个 Agent 先后登记身份：

```text
| Agent ID            | 平台/模型  | 角色          | 首次登记   | 最近活跃   | 备注              |
|---------------------|-----------|--------------|------------|------------|-------------------|
| claude-20260801-01  | Claude    | coordinator  | 2026-08-01 | 2026-08-01 | 自荐协调者        |
| codex-20260801-01   | Codex     | implementer  | 2026-08-01 | 2026-08-01 | 负责 TASK-021     |
```

`TASK_BOARD.md` 顶部：`Coordinator: claude-20260801-01`。

## 任务 ID 撞号处理

两个 Agent 同时读到看板最大编号 041，都尝试取 TASK-042：

```text
# Agent A（先到）
$ mkdir .agent/task-ids/TASK-042    # 成功
# 在 TASK_BOARD.md 写入 TASK-042 行

# Agent B（后到）
$ mkdir .agent/task-ids/TASK-042    # 失败：目录已存在
$ mkdir .agent/task-ids/TASK-043    # 成功
# 在 TASK_BOARD.md 写入 TASK-043 行，并在交接中记录「与 TASK-042 撞号，改用 043」
```

后到者不覆盖先到者的看板行；占位目录永不删除，作为已用编号记录。

## 陈旧锁判定（含 TTL）

```text
锁记录：
  Path: src/payment/controller.ts
  Task ID: TASK-021
  Owner: codex-20260730-01
  Last updated: 2026-07-30 09:00
  State: ACTIVE

检视时间：2026-07-30 14:30（距今 5.5 小时，超过 4 小时 TTL）
检视证据：
  - 原 agent/codex/TASK-021 分支最近 8 小时无提交
  - .agent/TASK_HANDOFF.md 无 TASK-021 的检查点更新
  - AGENTS_REGISTRY.md 中 codex-20260730-01 标记「不可达」
判定：满足「原分支无进行中迹象」+「原 Agent 不可达」，标记 STALE
动作：走接管协议，旧锁标 STALE 不删历史，由接管者记录 Takeover reason
```

TTL 只是触发检视的信号；不自动释放锁。
