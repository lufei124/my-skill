# Examples

## Parallel tasks

```text
TASK-021: Payment API
Owner: codex-20260730-01
Branch: agent/codex/TASK-021-payment-api
Allowed scope: server/payment/**, tests/payment/**
Status: IN_PROGRESS

TASK-022: Payment UI
Owner: claude-20260730-01
Branch: agent/claude/TASK-022-payment-ui
Allowed scope: app/payment/**, test/payment/**
Depends on: TASK-021 API contract
Status: CLAIMED
```

If both need `shared/payment_types.ts`, create a third task owned by one integration agent or sequence the edits.

## Interrupted task takeover

```text
Previous owner: claude-20260730-01
New owner: codex-20260730-02
Takeover reason: previous session ended before tests
State observed: three modified files, no commit, unit tests not run
Uncommitted changes preserved: yes
Verification performed: git diff reviewed; lint passed; one unit test failed
```

The receiving agent records the failure before modifying code.
