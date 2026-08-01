# Workflow Convergence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 收敛正式需求的阶段状态、原型豁免、复杂度路由和飞书交付策略，使 PRD 终稿不再依赖飞书发布且机器门禁真实覆盖文档承诺。

**Architecture:** 新需求统一生成 `00-stage-state.json`，由 `references/stage-state.schema.json` 集中声明结构、枚举和复杂度策略；`scripts/check-stage-gate.py` 只使用 Python 标准库解析 JSON、校验状态与文件证据。根编排器持有状态，子 Skill 只读执行门禁；PRD 完成与项目交付分别由 `prd`/`validation` 和 `delivery` 表达。

**Tech Stack:** Markdown Skill 规范、JSON Schema 风格契约、Python 3 标准库、Bash 校验脚本、PowerShell/Git Bash 兼容调用示例。

## Global Constraints

- 不增加第三方 YAML 或 JSON Schema 依赖。
- 新需求只生成 `schemaVersion: "1.1"` 的 `00-stage-state.json`。
- 不强制迁移历史 YAML；旧 YAML 仅提示旧格式。
- 用户确认点只保留需求理解、原型确认/豁免、重大评审争议。
- 飞书发布是项目交付策略，不改变 `prd.status=final`。
- 不升级版本、不创建 Git commit、不修改游戏业务代码。

---

### Task 1: JSON 状态契约与门禁实现

**Files:**
- Create: `references/stage-state.schema.json`
- Modify: `scripts/check-stage-gate.py`
- Modify: `scripts/validate.sh`

**Interfaces:**
- Consumes: `00-stage-state.json` 与工作目录内阶段产物。
- Produces: `PASS` / `NOT_REQUIRED` / `BLOCKED` / `INVALID_STATE`，退出码分别为 `0` / `0` / `2` / `3`。

- [ ] **Step 1: 将附件列出的 required/waived、openP0、版本一致性、delivery 和 L1/L2/L3 用例写入 `self_test()`**
- [ ] **Step 2: 运行 `python3 scripts/check-stage-gate.py --self-test`，确认旧实现失败**
- [ ] **Step 3: 新增 JSON Schema 风格契约并删除自制 YAML 解析器**
- [ ] **Step 4: 实现结构、枚举、路径、文件、版本和各目标阶段的校验**
- [ ] **Step 5: 更新 `validate.sh` 的状态文件与隐式调用断言**
- [ ] **Step 6: 运行 self-test、`py_compile` 和 `validate.sh`**

### Task 2: 工作流与模板统一

**Files:**
- Modify: `references/stage-gates.md`
- Modify: `references/templates.md`
- Modify: `references/workflow.md`
- Modify: `references/prd-spec.md`

**Interfaces:**
- Consumes: `stage-state.schema.json` 的枚举与复杂度策略。
- Produces: 三确认点、原型豁免、L1/L2/L3、PRD 完成和交付分离的共享规则。

- [ ] **Step 1: 用 JSON 1.1 模板替换 YAML 1.0 模板并指向单一 Schema**
- [ ] **Step 2: 把 PRD 门禁改为 required/waived 二选一**
- [ ] **Step 3: 把 L1/L2/L3 从章节裁剪扩展为访谈、原型、评审、知识提案和交付策略**
- [ ] **Step 4: 把知识提案与飞书交付改为 PRD 终稿后的独立分支**
- [ ] **Step 5: 补历史 YAML 迁移说明与标准阻塞输出**

### Task 3: 编排器与子 Skill 行为收敛

**Files:**
- Modify: `SKILL.md`
- Modify: `skills/setup-mobile-game-product-forge/SKILL.md`
- Modify: `skills/game-prototype/SKILL.md`
- Modify: `skills/game-prd-writing/SKILL.md`
- Modify: `skills/game-prd-review/SKILL.md`
- Modify: `skills/game-prd-publish/SKILL.md`
- Modify: `agents/openai.yaml`
- Modify: `skills/game-prd-writing/agents/openai.yaml`
- Modify: `skills/game-prd-publish/agents/openai.yaml`

**Interfaces:**
- Consumes: 新阶段状态与共享规则。
- Produces: 正式请求优先路由根编排器；PRD 写作和发布只能显式调用或由根编排器委派。

- [ ] **Step 1: 根编排器改为 JSON 状态和三个产品确认点**
- [ ] **Step 2: 增加原型适用性判断和产品负责人豁免确认**
- [ ] **Step 3: 按复杂度选择访谈、评审、知识提案和交付重量**
- [ ] **Step 4: setup 记录飞书是否为强制项目交付策略并输出一句话入口**
- [ ] **Step 5: publish 只负责交付，失败只更新 delivery，不回退 PRD**
- [ ] **Step 6: 关闭 PRD 写作与发布的隐式调用**

### Task 4: 用户文档、维护规则与决策记录

**Files:**
- Modify: `README.md`
- Modify: `operation-guide.md`
- Modify: `AGENTS.md`
- Modify: `CHANGELOG.md`
- Create: `.agents/adr/0009-separate-prd-completion-from-delivery.md`
- Modify: `.agents/adr/README.md`
- Modify: `.agents/adr/0008-feishu-publish-as-fourth-confirmation-gate.md`
- Create: `.gitignore`

**Interfaces:**
- Consumes: 已实现的工作流契约。
- Produces: 一致的用户入口、维护手册、决策历史和仓库清理规则。

- [ ] **Step 1: 操作指南顶部增加 5 分钟快速开始和短启动提示词**
- [ ] **Step 2: README/AGENTS 统一 JSON、三确认点、交付策略和 setup 边界**
- [ ] **Step 3: 新增 superseding ADR，并在旧 ADR 顶部标记被取代**
- [ ] **Step 4: 在 `[Unreleased]` 记录行为变化但不升版本**
- [ ] **Step 5: 添加系统/缓存文件 `.gitignore`**

### Task 5: 一致性与跨平台验证

**Files:**
- Verify only.

**Interfaces:**
- Consumes: 全部修改。
- Produces: 可复现的验证证据和残留风险。

- [ ] **Step 1: 运行 `bash scripts/doc-impact-check.sh` 并据结果补齐文档**
- [ ] **Step 2: 运行门禁 self-test、Python 编译、PRD 正反夹具和 `bash scripts/validate.sh`**
- [ ] **Step 3: 运行 shell 语法检查、`git diff --check` 和附件指定残留扫描**
- [ ] **Step 4: 检查 Windows 路径/PowerShell 示例；本机无 Windows 时明确交由 `validate-windows` CI 未实机验证**
- [ ] **Step 5: 输出修改文件、未修改文件原因、验证结果、风险、版本与 Git 状态**
