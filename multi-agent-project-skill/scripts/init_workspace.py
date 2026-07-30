#!/usr/bin/env python3
"""Initialize durable multi-agent project state without overwriting existing files."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict


TEMPLATES: Dict[str, str] = {
    "PROJECT_STATE.md": """# Project State

Last updated:
Updated by:
Current version/branch:
Current phase:

## Completed

- None recorded.

## In progress

- None recorded.

## Ready for review

- None recorded.

## Blocked

- None recorded.

## Known issues and risks

- None recorded.

## Recent decisions

- None recorded.

## Next priorities

1. Define the next task.
""",
    "TASK_BOARD.md": """# Task Board

| Task ID | Title | Owner agent | Status | Branch/worktree | Allowed scope | Dependencies | Updated at |
|---|---|---|---|---|---|---|---|
| TASK-001 | Initialize multi-agent project state | unassigned | BACKLOG | - | `.agent/` | - | - |

## Task details template

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
""",
    "FILE_LOCKS.md": """# File Locks

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
""",
    "TASK_HANDOFF.md": """# Current Task Handoff

## Identity

Task ID:
Task title:
Outgoing/current agent:
Intended next role/agent:
Branch/worktree:
Status:
Updated at:

## Completed

- None recorded.

## Changed files

- None recorded.

## Current position

- No active work recorded.

## Decisions

- None recorded.

## Verification

| Command/check | Result | Relevant output or reason not run |
|---|---|---|

## Remaining work

1. None recorded.

## Risks and known issues

- None recorded.

## Takeover instructions

1. Read `.agent/PROJECT_STATE.md` and `.agent/TASK_BOARD.md`.
2. Inspect `git status`, `git diff`, and the relevant branch.
3. Verify documented test results.
4. Preserve all unexplained changes.
""",
}

ADR_TEMPLATE = """# Decision

Status: proposed
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
"""

HANDOFF_TEMPLATE = """# Task handoff

## Identity

Task ID:
Task title:
Outgoing agent:
Intended next role/agent:
Branch/worktree:
Status:

## Completed

## Changed files

## Current position

## Decisions

## Verification

## Remaining work

## Risks and known issues

## Takeover instructions
"""

AGENTS_SNIPPET = """# Agent Coordination

This repository may be edited by multiple AI agents concurrently or handed off at any time.

Before editing, use the `multi-agent-project-coordination` skill and read the durable state under `.agent/`.

Hard rules:

- Claim a task before changing files.
- Use separate Git branches or worktrees for parallel tasks.
- Record intended file scope and active locks.
- Preserve unexplained and unmerged changes.
- Update handoff state before pausing or transferring work.
- Do not commit or push unless explicitly requested.
"""


def write_file(path: Path, content: str, force: bool) -> str:
    if path.exists() and not force:
        return "kept"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "written"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--force", action="store_true", help="overwrite managed template files")
    parser.add_argument(
        "--add-agents-md",
        action="store_true",
        help="create a minimal AGENTS.md only when it is missing (or overwrite with --force)",
    )
    args = parser.parse_args()

    root = Path(args.project_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        parser.error(f"project root is not a directory: {root}")

    state = root / ".agent"
    (state / "decisions").mkdir(parents=True, exist_ok=True)
    (state / "handoffs").mkdir(parents=True, exist_ok=True)

    results = []
    for name, content in TEMPLATES.items():
        results.append((state / name, write_file(state / name, content, args.force)))

    results.append(
        (
            state / "decisions" / "ADR-0000-template.md",
            write_file(state / "decisions" / "ADR-0000-template.md", ADR_TEMPLATE, args.force),
        )
    )
    results.append(
        (
            state / "handoffs" / "HANDOFF-template.md",
            write_file(state / "handoffs" / "HANDOFF-template.md", HANDOFF_TEMPLATE, args.force),
        )
    )

    if args.add_agents_md:
        results.append((root / "AGENTS.md", write_file(root / "AGENTS.md", AGENTS_SNIPPET, args.force)))

    print(f"Initialized multi-agent state at: {state}")
    for path, action in results:
        print(f"- {action:7} {path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
