# 已取代：飞书发布门方案

本文件是 ADR-0008 的历史实施计划，当前方案已由 [ADR-0009](../.agents/adr/0009-separate-prd-completion-from-delivery.md) 取代。

当前有效规则：

- PRD 完成：`prd.status=final` 且 `validation.status=passed`；
- 飞书发布：由独立 `delivery` 项目策略控制，不是产品确认门；
- 新需求状态：`00-stage-state.json`，Schema 见 `references/stage-state.schema.json`；
- 历史决策理由仍可在 ADR-0008 查看，但不得作为当前执行规范。
