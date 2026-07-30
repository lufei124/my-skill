# Workflow Reference

## New project

```bash
python scripts/init_workspace.py /path/to/project --add-agents-md
```

Then create the first task in `.agent/TASK_BOARD.md`, choose a branch/worktree, and record file scope.

## Agent starts a task

1. Read `AGENTS.md` and `.agent/*`.
2. Inspect Git status and diffs.
3. Claim a task.
4. Create or switch to an isolated branch/worktree.
5. Add file locks.
6. Execute within scope.

## Agent pauses or exits

1. Run available tests.
2. Update `.agent/TASK_HANDOFF.md`.
3. Archive the handoff under `.agent/handoffs/`.
4. Update task and project status.
5. Keep active locks if work remains; release them if work is complete.

## Another agent takes over

1. Verify handoff against Git.
2. Preserve uncommitted work.
3. Run stated checks.
4. Record discrepancies.
5. Transfer task and lock ownership.
6. Continue from the first unfinished or unverified step.

## Multiple agents need one shared file

Do not let both edit it concurrently. Choose one:

- sequence the tasks;
- split the file first;
- assign the shared-file change to a dedicated integration task.
