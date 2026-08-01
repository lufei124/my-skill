---
name: game-analytics-design
description: Use only when the root mobile-game-product-forge orchestrator delegates analytics design for a confirmed feature scope, or when the user explicitly asks only for instrumentation, metrics, funnels, or experiment measurement as a narrow task. Deduplicates against existing event baselines. Do not route broad feature, system-design, or formal-PRD requests directly here; route those to the root orchestrator.
---

# 游戏埋点与指标设计

负责移动游戏需求工坊的「埋点与指标」环节。设计埋点事件、参数、漏斗和成功指标，并先对已有事件基线去重，再设计新增或扩展项。

本子 Skill 是 `mobile-game-product-forge` 的能力拆分。需求处理模式、确认门、版本号、共享工作目录由编排器持有，本子 Skill 假设前置已成立。

正式流程中，PRD 的埋点章节默认由 `game-prd-writing` 按 prd-spec「埋点和指标」内联产出；本 Skill 用于独立埋点/指标窄任务，或 PRD 写作前需要深化埋点方案时由编排器委派，产出可直接并入 PRD。

## 前置条件

1. 编排器已判定需求处理模式。
2. 模式1或模式2需已读取项目知识库登记的埋点规范和事件基线；模式3不读取项目埋点，只依据本次需求设计。
3. 作为窄任务独立调用时的最小输入：要计算什么业务结果/指标的意图（如「注册转化」「广告变现」）及对应功能范围；缺失则只问这一个问题，不进入设计。
4. 消费边界：以提供的功能范围与已读事件基线为权威，不重新访谈、不重新推导上游已确认决策；上游缺口标待确认项交回，不自行假设填充。

## 流程

1. 读取项目知识库登记的埋点规范和事件基线（模式1/模式2）。
2. 列出本次需求要计算的指标和对应漏斗。
3. 先完成已有事件去重：本次所需指标若可由已有事件计算，复用已有事件，不新增。
4. 对无法复用的指标，设计新增事件或扩展现有事件参数。
5. 标注每个事件的触发时机、参数、取值范围、采样和服务端/客户端归属。

## 输出

- 指标清单：指标名、口径、计算公式、数据来源事件、基线来源（历史/行业/用户研究/此前实验；无则标「待确认基线」并在上线方案补采集计划）
- 事件明细表：以 [../../references/prd-spec.md](../../references/prd-spec.md)「埋点和指标」的 12 列事件明细为骨架（事件分类｜事件名称｜事件标识符｜数据来源｜埋点触发时机｜属性名称｜属性标识符｜属性含义｜上线版本｜下线版本｜类型｜值含义；一行代表一个事件×属性，新标识符使用小写 `snake_case`）；采样规则与取值范围作为补充说明列于表后，关键转化事件不得采样
- 漏斗定义：步骤、转化口径、归因窗口
- 去重说明：哪些指标复用已有事件，哪些为新增
- 实验建议（若有）：分流维度、对照、成功指标、最小样本

## 规则

- 埋点必须能够计算核心指标。
- 资产、奖励、次数等结果性数据以服务端事件为准。
- 不得静默更改已有事件口径；扩展参数时标注向后兼容性。
- 模式3固定标注“未关联项目事件基线，可能与已有埋点重复，待人工核对”。

## 完成与交接

正式流程中，埋点设计并入当前 PRD 草稿（如 `03-prd-v0.1.md`）的「埋点和指标」章，交由编排器更新产物版本和本需求目录的变更记录（若存在）。若作为窄任务独立调用，直接输出埋点设计并标注去重结果。

## 参考

- 埋点与指标章节（12 列事件明细表）：[../../references/prd-spec.md](../../references/prd-spec.md)「埋点和指标」
