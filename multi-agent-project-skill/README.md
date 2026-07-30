# Multi-Agent Project Coordination Skill

A portable skill for projects that may be edited by several AI agents concurrently or handed off at any moment.

## Contents

- `SKILL.md`: agent behavior and coordination protocol
- `scripts/init_workspace.py`: initializes `.agent/` state without overwriting existing files
- `references/WORKFLOW.md`: compact operating workflow
- `references/EXAMPLES.md`: parallel and takeover examples

## Initialize a project

```bash
python /path/to/skill/scripts/init_workspace.py /path/to/project --add-agents-md
```

This creates:

```text
.agent/
├── PROJECT_STATE.md
├── TASK_BOARD.md
├── FILE_LOCKS.md
├── TASK_HANDOFF.md
├── decisions/
└── handoffs/
```

Existing files are preserved by default. Use `--force` only when replacement is intentional.
