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