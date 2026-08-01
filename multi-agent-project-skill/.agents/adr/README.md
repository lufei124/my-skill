# 架构决策记录（ADR）

本目录以编号追加式记录难逆、令新贡献者意外的架构决策的理由。

## 约定

- 编号零填充三位（`0001-<slug>.md`），按时间递增，不复用编号。
- 追加式：改决策不修改既有 ADR，而是新增 superseding ADR 并在旧 ADR 顶部标「被 ADR-00NN 取代」，使反转可见。
- 每个 ADR 只记 **背景 / 决策 / 备选方案 / 后果**，不复述可变规则——可变规则的唯一权威源仍在 `SKILL.md`、`AGENTS.md`、`references/` 与 `scripts/`。
- 决策点在 `AGENTS.md` / `SKILL.md` 内联引用对应 ADR，读者一跳解析「为何如此」。
- 状态：`已采纳` / `已被取代` / `已废弃`。

> 注：本目录记录的是**本 skill 仓库自身**的架构决策，与 init 产物里目标项目的 `.agent/decisions/ADR-XXXX`（记录目标项目的决策）是两层不同的东西。本目录的 ADR 由 skill 维护者追加。

## 索引

- [0001 - assets/ 为模板唯一真相源，脚本零内嵌字符串](0001-assets-single-source-of-truth.md)
- [0002 - AGENTS.md 统一入口，平台文件只链接不复制规则](0002-agents-md-unified-entry.md)
- [0003 - 任务 ID 用 mkdir 原子分配](0003-atomic-task-id-via-mkdir.md)
- [0004 - 陈旧锁 TTL 仅触发检视，不自动释放](0004-stale-lock-ttl-no-auto-release.md)
- [0005 - 以 Claude Code plugin 形态发布](0005-ship-as-claude-code-plugin.md)
- [0006 - package.json 为唯一版本源](0006-package-json-single-version-source.md)
