# Agent Coordination

This repository may be edited by multiple AI agents concurrently or handed off at any time.

Before editing, use the `multi-agent-project-coordination` skill and read the durable state under `.agent/`.

Hard rules:

- Claim a task before changing files.
- Use separate Git branches or worktrees for parallel tasks.
- Record intended file scope and active locks.
- Preserve unexplained and unmerged changes.
- Update handoff state before pausing or transferring work.
- Do not commit or push unless explicitly requested.
