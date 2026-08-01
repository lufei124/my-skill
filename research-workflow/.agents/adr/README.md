# 架构决策记录（ADR）

本目录以编号追加式记录难逆、令新贡献者意外的架构决策的理由。

## 约定

- 编号零填充三位（`0001-<slug>.md`），按时间递增，不复用编号。
- 追加式：改决策不修改既有 ADR，而是新增 superseding ADR 并在旧 ADR 顶部标「被 ADR-00NN 取代」，使反转可见。
- 每个 ADR 只记 **背景 / 决策 / 备选方案 / 后果**，不复述可变规则--可变规则的唯一权威源仍在 `SKILL.md`、`AGENTS.md`、`references/` 与 `scripts/`。
- 决策点在 `AGENTS.md` / `SKILL.md` 内联引用对应 ADR，读者一跳解析「为何如此」。
- 状态：`已采纳` / `已被取代` / `已废弃`。

## 索引

- [0001 - grilling 对齐强制不可跳过](0001-grilling-first-mandatory.md)
- [0002 - 编号主题目录 + 固定 6 层结构](0002-numbered-topic-six-layer-dir.md)
- [0003 - 三阶段 Workflow：并行初稿 -> 红队 -> 评审委员会](0003-three-phase-workflow.md)
- [0004 - 通用核心 + 可插拔领域预设](0004-pluggable-domain-presets.md)
- [0005 - 从 subsystem-research-workflow 通用化而来](0005-generalized-from-subsystem-research.md)
- [0006 - 以 Claude Code plugin 形态发布 + package.json 唯一版本源](0006-ship-as-plugin-and-version-sot.md)
