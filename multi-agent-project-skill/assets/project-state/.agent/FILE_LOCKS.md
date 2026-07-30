# File Locks

Locks are advisory coordination records. Parallel agents should still use separate Git branches or worktrees.

| Path or glob | Task ID | Owner agent | Branch/worktree | Reason | Acquired at | Last updated | State |
|---|---|---|---|---|---|---|---|

Valid states: `ACTIVE`, `RELEASED`, `STALE`, `TAKEOVER_PENDING`.

## Takeover history template

```text
Previous owner:
New owner:
Takeover reason:
State observed at takeover:
Uncommitted changes preserved:
Verification performed:
```
