# 架构决策记录（ADR）

本目录以编号追加式记录难逆、令新贡献者意外的架构决策的理由。

## 约定

- 编号零填充三位（`0001-<slug>.md`），按时间递增，不复用编号。
- 追加式：改决策不修改既有 ADR，而是新增 superseding ADR 并在旧 ADR 顶部标「被 ADR-00NN 取代」，使反转可见。
- 每个 ADR 只记 **背景 / 决策 / 备选方案 / 后果**，不复述可变规则--可变规则的唯一权威源仍在 `SKILL.md`、`AGENTS.md`、`references/` 与 `scripts/`。
- 决策点在 `AGENTS.md` / `SKILL.md` 内联引用对应 ADR，读者一跳解析「为何如此」。
- 状态：`已采纳` / `已被取代` / `已废弃`。

## 索引

- [0001 - 以 Claude Code plugin 形态发布](0001-ship-as-claude-code-plugin.md)
- [0002 - PRD 经 lark-cli/飞书云文档发布，非本地 PDF](0002-publish-via-lark-cli-not-pdf.md)
- [0003 - 知识包可选且只读](0003-knowledge-packs-optional-readonly.md)
- [0004 - 三个确认门为铁律](0004-confirmation-gates-ironclad.md)
- [0005 - 子 Skill 用 ../../references/ 相对路径，要求整仓符号链接](0005-relative-path-whole-repo-linking.md)
- [0006 - 根编排器位于仓库根，非 skills/ 下](0006-root-orchestrator-at-repo-root.md)
- [0007 - 正式需求使用机器可读阶段状态与硬门禁（格式部分已被取代）](0007-machine-readable-stage-gates.md)
- [0008 - 飞书发布升为第四道确认门（已被取代）](0008-feishu-publish-as-fourth-confirmation-gate.md)
- [0009 - PRD 完成与项目交付分离](0009-separate-prd-completion-from-delivery.md)

- [0010 - PRD 使用统一研发执行结构](0010-execution-oriented-prd-structure.md)
