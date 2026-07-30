---
name: multi-agent-project-coordination
description: Use this skill when a software or product project may be edited by multiple AI agents concurrently, may be handed off at any point, or needs durable task state, file ownership, Git isolation, review, integration, and recovery that do not depend on chat history. Trigger for multi-agent collaboration, agent takeover, parallel development, task handoff, shared repositories, worktrees, file conflicts, interrupted work, or cross-agent review.
---

# Multi-Agent Project Coordination

## Goal

Make a project safe for multiple AI agents to work on concurrently or take over at any time. The repository is the durable source of truth; chat context is temporary.

## Non-negotiable rules

1. Read project state before editing.
2. Claim a task before changing files.
3. Use one branch or Git worktree per active task when agents work in parallel.
4. Declare the intended file scope before editing.
5. Do not edit files actively owned by another task unless performing an explicit integration or takeover.
6. Keep changes minimal and limited to the claimed task.
7. Never erase, reset, reformat, or overwrite another agent's unmerged work.
8. Never claim tests passed unless they were actually executed.
9. Do not commit or push unless the user or coordinating agent explicitly requests it.
10. Update durable state whenever work pauses, changes hands, becomes blocked, enters review, or finishes.

Never run destructive commands such as:

```bash
git reset --hard
git clean -fd
git push --force
```

## Required project state

Use the `.agent/` directory in the project root:

```text
.agent/
├── PROJECT_STATE.md
├── TASK_BOARD.md
├── FILE_LOCKS.md
├── TASK_HANDOFF.md
├── decisions/
└── handoffs/
```

If it does not exist, run:

```bash
python <skill-directory>/scripts/init_workspace.py <project-root>
```

The initializer must not overwrite existing files unless explicitly requested.

## Operating modes

Determine the current mode and follow the corresponding procedure:

- **Initialize**: create missing state files and inspect the repository.
- **Claim**: select or create a task, register ownership, branch, scope, dependencies, and acceptance criteria.
- **Execute**: work only inside the claimed scope and keep a short recoverable checkpoint.
- **Checkpoint**: record current progress before context becomes long or uncertain.
- **Handoff**: make incomplete or completed work independently understandable to another agent.
- **Takeover**: verify another agent's handoff against Git and tests before continuing.
- **Review**: inspect adversarially without assuming the implementation is correct.
- **Integrate**: merge parallel work in dependency order and resolve intent, not just text conflicts.

## Start-of-work procedure

Before editing:

1. Read, when present:
   - `AGENTS.md`
   - `PROJECT_CONTEXT.md`
   - `.agent/PROJECT_STATE.md`
   - `.agent/TASK_BOARD.md`
   - `.agent/FILE_LOCKS.md`
   - `.agent/TASK_HANDOFF.md`
   - relevant `.agent/decisions/`
   - relevant `.agent/handoffs/`
2. Run:

```bash
git status --short
git branch --show-current
git diff --stat
git log -10 --oneline
```

3. Establish and state:

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

4. If unexplained uncommitted changes exist, preserve them. Do not clean or overwrite them.

## Task claim protocol

Each task entry in `.agent/TASK_BOARD.md` must contain:

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

Valid statuses:

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

Before modifying files:

- Claim an unowned task or explicitly take over an abandoned/stale task.
- Record a unique agent identity, such as `codex-20260730-01`.
- Record the exact files or directories expected to change.
- Prefer separate tasks when work can be split cleanly.

## Parallel work protocol

When multiple agents work simultaneously:

1. Use separate branches or worktrees. File locks do not replace Git isolation.
2. Prefer non-overlapping files and modules.
3. Record planned ownership in `.agent/FILE_LOCKS.md` before editing.
4. A lock must include:

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

5. If two tasks require the same file:
   - split the work by file when possible;
   - sequence the tasks; or
   - assign one integration agent to perform the shared-file edit.
6. Never resolve a conflict by blindly choosing one entire version.
7. Never perform repository-wide formatting during parallel work unless it is the explicit isolated task.

## Stale lock and takeover protocol

A lock may be treated as stale only when work is clearly abandoned, the prior agent is unavailable, or the coordinating agent/user authorizes takeover.

Before takeover:

1. Inspect the prior branch/worktree, `git status`, `git diff`, and latest handoff.
2. Mark the old lock `STALE` or `TAKEOVER_PENDING`; do not delete its history.
3. Record:

```text
Previous owner:
New owner:
Takeover reason:
State observed at takeover:
Uncommitted changes preserved:
Verification performed:
```

4. Continue from the verified state rather than recreating completed work.

## Execution and checkpoint protocol

During work:

- Modify only the declared scope.
- Avoid unrelated refactors, dependency upgrades, schema changes, API changes, or global formatting.
- If scope must expand, update the task and locks before proceeding.
- Preserve a recoverable checkpoint in `.agent/TASK_HANDOFF.md` after any material milestone or before stopping.
- Record important architecture, API, data, or business-rule decisions under `.agent/decisions/ADR-XXXX-title.md`.

Use this checkpoint structure:

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

## Testing protocol

Run the checks relevant to the project, such as tests, lint, type checking, builds, migrations, or manual flows.

Record:

```text
Command:
Result: PASS | FAIL | NOT_RUN
Relevant output:
Reason if not run:
Manual verification:
```

Rules:

- A pre-existing failure must be identified as pre-existing only when verified.
- Do not delete or weaken tests to make a task pass.
- Do not mark a task `DONE` with unresolved required checks.

## Handoff protocol

Handoff is required when:

- work finishes;
- work pauses before completion;
- another agent must continue;
- the task becomes blocked;
- review is requested;
- integration is requested;
- context is becoming unreliable.

Update `.agent/TASK_HANDOFF.md` and archive a copy to:

```text
.agent/handoffs/YYYY-MM-DD-HHMM-task-id-agent-id.md
```

A handoff must contain:

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
- Concrete completed work
- Acceptance criteria already satisfied

## Changed files
- path: what changed and why

## Current position
- Exact point where work stopped
- Current runtime/build state

## Decisions
- Confirmed decisions
- ADR references
- Decisions that should not be reopened without new evidence

## Verification
- Commands run
- Exact pass/fail results
- Checks not run and why

## Remaining work
1. Concrete next action
2. Following action

## Risks and known issues
- Known bugs
- Possible regressions
- Conflicts or dependencies

## Takeover instructions
1. Files to read first
2. Commands to run first
3. Branch/worktree to inspect
4. Work that must not be overwritten
5. Expected next deliverable
```

## Takeover procedure

A receiving agent must not trust the handoff blindly.

1. Read the handoff and relevant ADRs.
2. Inspect Git state and actual diffs.
3. Run the stated verification where practical.
4. Compare documented state with repository state.
5. Record discrepancies before editing.
6. Update the task owner, status, locks, and current handoff.
7. Continue from the first unverified or unfinished step.

Start the takeover response with:

```text
Taken-over task:
Verified completed work:
Verified unfinished work:
State discrepancies:
Preserved changes:
Next action:
Planned scope:
```

## Review procedure

Review adversarially. Do not assume the author or previous agent is correct.

Check:

- requirements and acceptance criteria;
- edge cases and failure states;
- regressions and unintended behavior changes;
- API, schema, permission, security, performance, and data risks;
- missing or weak tests;
- unnecessary scope expansion;
- consistency between code, task state, and handoff.

Classify findings:

```text
P0: release-blocking security, data, money, or destructive failure
P1: core-function failure or high-probability regression
P2: normal correctness, UX, or maintainability issue
P3: optional improvement
```

A review agent should normally report findings first. It should only modify code when explicitly assigned a fix task or integration role.

## Integration procedure

An integration agent must:

1. Read each task handoff and acceptance criteria.
2. Inspect each branch diff independently.
3. Confirm task scopes do not include accidental changes.
4. Merge in dependency order.
5. Resolve conflicts by understanding both intentions.
6. Run relevant module checks and then broader regression checks.
7. Update task statuses, release locks, refresh project state, and write an integration handoff.

Do not mark integration complete merely because Git produced no textual conflicts.

## Decision records

Create an ADR when changing architecture, APIs, schemas, shared behavior, dependencies, or cross-module rules.

Use `.agent/decisions/ADR-XXXX-title.md`:

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

## Completion criteria

A task can be marked `DONE` only when all applicable items are true:

```text
[ ] Acceptance criteria are satisfied
[ ] Changes stayed within the declared scope or scope expansion was recorded
[ ] Other agents' work was preserved
[ ] Required checks were actually run and recorded
[ ] The task entry is current
[ ] File locks are released
[ ] Project state is current
[ ] Handoff is current and archived
[ ] Important decisions have ADRs
[ ] Review/integration requirements are satisfied
[ ] User or coordinating agent approved any requested commit/push
```

Otherwise use `IN_PROGRESS`, `BLOCKED`, `READY_FOR_REVIEW`, `CHANGES_REQUESTED`, or `READY_TO_INTEGRATE`.

## Response behavior

Keep user-facing updates short. When executing, report only meaningful milestones, discovered conflicts, failed checks, decisions needed, and final status. Do not dump internal bookkeeping unless requested.
