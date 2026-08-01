# Capability Fidelity Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct the evidence authority model, formalize requirement research, separate research findings from stage snapshots, validate prototype metadata completeness, and track review input versions without changing the stable 3.0.0 workflow.

**Architecture:** Keep `references/context-loading.md` as the single shared contract, but split authority into product decisions, current-state evidence, and external constraints. Introduce `00-research-findings.md` as the new-requirement research artifact while preserving `00-project-context.md` for legacy compatibility; keep `context-snapshot.md` as a derived stage packet. Extend the existing standard-library prototype parser with a COMPLETE/INCOMPLETE/INVALID classification and reuse current review report files for version tracking.

**Tech Stack:** Markdown Skill contracts, Python 3 standard library, Bash validation.

## Global Constraints

- Do not change the three product confirmation points, stage-state schema, workflow states, prototype waiver, PRD format, D/R/AC contracts, Feishu delivery policy, or version `3.0.0`.
- Do not add dependencies, databases, RAG services, crawlers, caches, approval systems, workflow engines, or permanent role directories.
- Do not create a Git commit.
- Preserve progressive loading: current evidence first, history and HTML on demand, high-risk sources proactively deep-read.

---

### Task 1: Authority Model and Research Contract

**Files:**
- Modify: `references/context-loading.md`
- Modify: `SKILL.md`
- Modify: `AGENTS.md`

**Interfaces:**
- Produces: three independent authority models, a fixed conflict report, six research-source classes, L1/L2/L3 research depth, and a stable quick execution index.
- Consumes: existing progressive loading, high-risk deep-read, and root conflict escalation rules.

- [ ] **Step 1:** Replace the single business-source hierarchy with product-decision, current-state, and external-constraint evidence models.
- [ ] **Step 2:** Define conflict output that always separates current state, target state, and required change.
- [ ] **Step 3:** Define user interview, project knowledge, current implementation, history, data/feedback, and external research sources with L1/L2/L3 depth.
- [ ] **Step 4:** Add a stable heading-based execution index and make root/stage references point to named sections.

### Task 2: Research Artifact and Handoff Timing

**Files:**
- Modify: `references/templates.md`
- Modify: `references/workflow.md`
- Modify: `skills/game-requirement-discovery/SKILL.md`
- Modify: `skills/game-prototype/SKILL.md`
- Modify: related `agents/openai.yaml`

**Interfaces:**
- Produces: `00-research-findings.md` for new requirements, legacy `00-project-context.md` compatibility, discovery output ending before requirement confirmation, and coordinator-owned PRD/review snapshot generation.
- Consumes: existing requirement summary and prototype confirmation/waiver gates.

- [ ] **Step 1:** Replace the new-demand project-context template with the specified research-findings structure and document legacy compatibility.
- [ ] **Step 2:** Expand discovery to the six evidence classes and return current state, target state, conflicts, unknowns, risks, recommendations, and a summary draft.
- [ ] **Step 3:** Remove discovery’s post-prototype snapshot responsibility; assign PRD/review snapshot generation and freezing only to the coordinator.
- [ ] **Step 4:** Update prototype input/output to consume research findings and return prototype evidence for snapshot construction.

### Task 3: Prototype Metadata Completeness (TDD)

**Files:**
- Modify: `scripts/check-stage-gate.py`
- Modify: `references/stage-gates.md`
- Modify: `skills/game-prototype/SKILL.md`
- Modify: `skills/game-prd-writing/SKILL.md`
- Modify: `skills/game-prd-review/SKILL.md`

**Interfaces:**
- Produces: `classify_prototype_meta(meta: dict[str, Any]) -> PrototypeMetaCheck`, COMPLETE exit `0`, INCOMPLETE exit `2`, and INVALID exit `3`.
- Reuses: `PrototypeMetaParser` and `read_prototype_meta`.

- [ ] **Step 1: Write failing self-tests**

Add complete, missing-field, wrong-type, malformed JSON, missing metadata, invalid `D-###`, legacy-minimal fallback, and no-source-leak cases.

- [ ] **Step 2: Run RED**

Run: `python3 scripts/check-stage-gate.py --self-test`

Expected: fail because completeness classification is not implemented.

- [ ] **Step 3: Implement minimal classifier and CLI**

Validate required fields and types with the standard library. Emit compact metadata for COMPLETE; emit `{"status":"INCOMPLETE","missingFields":[],"invalidFields":[],"nextAction":"read_relevant_html"}` with exit `2`; preserve INVALID exit `3`.

- [ ] **Step 4: Run GREEN**

Run: `python3 scripts/check-stage-gate.py --self-test`

Expected: all gate, complexity, and metadata cases pass.

- [ ] **Step 5:** Make the PRD gate reject an incomplete new confirmed prototype while documenting that historical metadata follows the HTML compatibility path rather than being treated as complete.

### Task 4: Review Version Consistency and Documentation

**Files:**
- Modify: `references/templates.md`
- Modify: `references/context-loading.md`
- Modify: `skills/game-prd-review/SKILL.md`
- Modify: affected `agents/openai.yaml`
- Modify: `README.md`
- Modify: `operation-guide.md`
- Modify: `CHANGELOG.md`
- Modify: `scripts/validate.sh`

**Interfaces:**
- Produces: role output fields `reviewRole`, `snapshotVersion`, `prdVersion`, `prototypeVersion`, `reviewedAt`; coordinator mismatch handling; user and maintainer documentation.

- [ ] **Step 1:** Add role version fields to review templates and require coordinator equality checks before `passed`.
- [ ] **Step 2:** Define stale-role rerun of only affected sections without adding state fields.
- [ ] **Step 3:** Synchronize user docs, prompts, maintainer rules, and `[Unreleased]`.
- [ ] **Step 4:** Add lightweight validation guards for the research artifact, authority headings, metadata classification, and review version fields.

### Task 5: Verification and Git Audit

**Files:**
- Verify all modified and added files; do not commit.

**Interfaces:**
- Produces: fresh self-test, metadata CLI, validation, documentation, scan, and Git evidence.

- [ ] **Step 1:** Run the required metadata COMPLETE/INCOMPLETE/INVALID and source-leak cases.
- [ ] **Step 2:** Run `py_compile`, `doc-impact-check.sh`, `validate.sh`, both PRD lint fixtures, shell syntax, and `git diff --check`.
- [ ] **Step 3:** Run both required documentation scans and the junk-file scan.
- [ ] **Step 4:** Confirm the schema, gates, PRD format, D/R/AC, delivery policy, install architecture, and version remain unchanged except for the explicitly requested prototype completeness gate documentation.
