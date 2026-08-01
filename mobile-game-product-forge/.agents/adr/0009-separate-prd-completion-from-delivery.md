# ADR-0009：PRD 完成与项目交付分离

- 状态：已采纳
- 日期：2026-07-26
- 取代：[ADR-0008](0008-feishu-publish-as-fourth-confirmation-gate.md)

## 背景

仓库同时把 `docs/prd/` 定义为正式终稿、允许 setup 跳过飞书，又把飞书发布定义为第四确认门和流程完成条件，导致不使用飞书的项目无法完整结束 PRD，发布失败还可能掩盖终稿事实。

## 决策

1. PRD 完成只由 `prd.status=final` 且 `validation.status=passed` 表达。
2. 飞书发布由独立 `delivery` 状态表达，是项目策略而非产品确认门。
3. `delivery.required=false` 时无需发布；为 true 时交付失败只记 `failed`，不回退 PRD。
4. 用户层产品确认点保持三个：需求理解、原型确认/产品负责人豁免、重大评审争议。
5. 新需求使用 JSON 1.1 阶段状态；结构和枚举集中在 `references/stage-state.schema.json`。

## 备选方案

- 继续保留第四确认门：与可跳过绑定、不使用飞书和本地正式终稿冲突，被否。
- 删除发布 Skill：项目仍需要可选或强制飞书交付，被否。
- 用 `prd.status=published` 同时表达内容与交付：发布失败会污染 PRD 内容状态，被否。

## 后果

- `game-prd-publish` 只负责交付，改为 explicit-only/编排器委派。
- setup 必须询问飞书是否为强制项目策略。
- 知识维护提案与交付成为终稿后的独立分支，无固定先后。
- 历史 YAML 和 ADR-0008 保留作历史证据，新需求不再沿用其状态模型。
