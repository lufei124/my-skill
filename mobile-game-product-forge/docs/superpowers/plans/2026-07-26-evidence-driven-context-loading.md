# Evidence-Driven Context Loading Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace defensive full-context rereads with evidence-driven progressive loading while preserving the existing workflow, quality gates, and maximum review capability.

**Architecture:** Add `references/context-loading.md` as the only shared loading contract. The root orchestrator and four affected stage Skills keep only their stage-specific default inputs, exclusions, and escalation triggers. Reuse `check-stage-gate.py`’s existing `PrototypeMetaParser` through a metadata-only CLI, and keep `context-snapshot.md` as an untrusted summary plus evidence index rather than a new state or authority.

**Tech Stack:** Markdown Skill contracts, Python 3 standard library, Bash validation.

## Global Constraints

- Do not change the three confirmation points, stage-state schema, workflow states, prototype waiver, D/R/AC contracts, PRD format, Feishu delivery policy, or version `3.0.0`.
- Do not add third-party dependencies, persistent role-slice directories, databases, caches, services, or a workflow engine.
- Context budgets are soft; evidence gaps, conflicts, uncertainty, high-risk domains, and user trace requests must expand source reading automatically.
- Do not create a Git commit.

---

### Task 1: Shared Context Contract and Snapshot Template

**Files:**
- Create: `references/context-loading.md`
- Modify: `references/templates.md`
- Modify: `references/workflow.md`

**Interfaces:**
- Produces: a three-layer loading contract, `context-snapshot.md` evidence-index template, source-fingerprint reuse rules, current-version selection, high-risk deep-read triggers, shared-core role inputs, validation timing, and regression scenarios.
- Consumes: existing authority order, JSON state ownership, prototype/PRD/review stage boundaries.

- [ ] **Step 1:** Write `context-loading.md` with authority hierarchy, progressive levels, capability safeguards, soft budgets, escalation triggers, metadata fallback, incremental snapshot updates, role slicing, conflict aggregation, and L1/L2/L3 regression scenarios.
- [ ] **Step 2:** Add `context-snapshot.md` to the work-directory template and add the required source-version/evidence-index structure without changing `00-stage-state.json`.
- [ ] **Step 3:** Replace workflow’s fixed-threshold context guidance with snapshot generation/freeze points, current-version rules, and references to the shared contract.
- [ ] **Step 4:** Run `grep` checks for forbidden full-read defaults and required progressive-loading terms.

### Task 2: Root and Stage Skill Loading Boundaries

**Files:**
- Modify: `SKILL.md`
- Modify: `skills/game-requirement-discovery/SKILL.md`
- Modify: `skills/game-prototype/SKILL.md`
- Modify: `skills/game-prd-writing/SKILL.md`
- Modify: `skills/game-prd-review/SKILL.md`
- Modify: corresponding `agents/openai.yaml`

**Interfaces:**
- Consumes: `references/context-loading.md`.
- Produces: stage-specific default inputs, non-default sources, automatic expansion triggers, metadata-first prototype consumption, and shared-core plus professional-increment review packets.

- [ ] **Step 1:** Add the root default order (`00-stage-state.json` → current recorded file → `context-snapshot.md` → necessary contract) and prohibit default README/guide/all-references/all-history loading.
- [ ] **Step 2:** Give discovery and prototype stage-specific current-source defaults and evidence expansion rules.
- [ ] **Step 3:** Change PRD writing from full-HTML default to metadata-first, targeted DOM/HTML fallback, and high-risk deep read.
- [ ] **Step 4:** Change review fan-out to frozen shared core plus professional increments, temporary slices only when needed, and coordinator conflict aggregation without rereading every role’s original context.
- [ ] **Step 5:** Align affected OpenAI prompts with the loading behavior without changing invocation policy.

### Task 3: Metadata-Only Mechanical Extraction

**Files:**
- Modify: `scripts/check-stage-gate.py`
- Modify: `scripts/validate.sh`

**Interfaces:**
- Produces: `python check-stage-gate.py --extract-prototype-meta <index.html>` returning only compact JSON metadata; invalid/missing metadata returns exit code `3`.
- Reuses: `read_prototype_meta(path: Path) -> dict[str, Any]` and `PrototypeMetaParser`.

- [ ] **Step 1: Write failing self-tests**

Add cases proving valid metadata extraction, missing metadata failure, invalid JSON failure, and serialized output excludes HTML/CSS/JavaScript source.

- [ ] **Step 2: Run RED**

Run: `python3 scripts/check-stage-gate.py --self-test`

Expected: failure because the metadata-only extraction interface does not exist.

- [ ] **Step 3: Implement minimal CLI**

Add a mutually exclusive `--extract-prototype-meta PATH` argument that invokes the existing parser and emits compact JSON only; catch file/parser/JSON failures and return `INVALID_STATE` exit code `3`.

- [ ] **Step 4: Run GREEN**

Run: `python3 scripts/check-stage-gate.py --self-test`

Expected: all gate, policy, and metadata extraction cases pass.

- [ ] **Step 5:** Add validation guards requiring the shared context contract to be linked from the root and four stage Skills.

### Task 4: User and Maintainer Documentation

**Files:**
- Modify: `README.md`
- Modify: `operation-guide.md`
- Modify: `AGENTS.md`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Produces: user-facing automatic context behavior, maintainer architecture mapping, reference index, and `[Unreleased]` record.

- [ ] **Step 1:** Explain in README that the system automatically builds/reuses evidence-index snapshots and reads original sources when evidence is insufficient.
- [ ] **Step 2:** Explain in the operation guide how users add sources or request history/deep verification without exposing internal budgets or role-slice algorithms.
- [ ] **Step 3:** Register `context-loading.md` and its single-source responsibility in AGENTS/README; add context-safety maintenance rules.
- [ ] **Step 4:** Add an `[Unreleased]` entry without changing version fields.

### Task 5: Verification and Git Audit

**Files:**
- Verify all modified files; do not commit.

**Interfaces:**
- Consumes: repository validation matrix and task acceptance commands.
- Produces: fresh test evidence, forbidden-pattern scans, junk-file scan, and actual Git status.

- [ ] **Step 1:** Run metadata CLI valid/missing/invalid tests and verify output contains no HTML source.
- [ ] **Step 2:** Run `py_compile`, stage-gate self-test, document-impact check, `validate.sh`, and both PRD lint fixtures with expected exit codes.
- [ ] **Step 3:** Run required grep scans, `git diff --check`, junk-file scan, `git status --short`, and `git diff --stat`.
- [ ] **Step 4:** Confirm version remains `3.0.0`, schema and install architecture are unchanged, and no commit was created.
