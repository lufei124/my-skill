# 共享交付模板

## 目录

1. 工作目录
2. 项目上下文
3. 决策账本
3a. 术语账本
4. 阶段状态
5. 评审任务
6. 评审问题
7. 变更记录
8. 校验报告
9. PRD 补充模板
10. 交付记录
11. 知识维护提案

## 1. 工作目录

```text
00-stage-state.json
context-snapshot.md
00-research-findings.md
01-requirement-summary.md
01-requirement-decisions.md
02-prototype/index.html
03-prd-v0.1.md
04-review-report.md
05-prd-v0.2.md
06-lint-report.md
07-prd-final.md
08-delivery-record.md
09-knowledge-proposals.md
csv/
字段说明/
csv-config-guide.md
CHANGELOG.md
```

`00-stage-state.json` 是正式需求唯一的跨阶段状态源，由根编排器创建和修改；子 Skill 只读校验。新需求的 `projectContext.file` 指向 `00-research-findings.md`；历史需求存在 `00-project-context.md` 时可继续保留和引用，不批量重命名、不要求用户迁移。《需求理解与方案摘要》固定文件名 `01-requirement-summary.md`，`requirementSummary.file` 指向它；历史需求以 `01-requirement-decisions.md` 兼容承载摘要时可继续引用，不批量迁移。`context-snapshot.md` 是协调 Agent 自动维护的阶段摘要与证据索引，不是调研记录、状态源或业务权威源。目标游戏项目未另定目录规范时，本次共享工作目录放在 `history/<日期>-<需求简称>/`；按复杂度和实际阶段创建所需文件，L1 与窄任务不创建无关空文件。`06-lint-report.md` 由 `scripts/lint-prd.py` 自动产出。`02-prototype/index.html` 仅在原型适用时生成；正式豁免不创建占位原型。`07-prd-final.md` 冻结与 `docs/prd/<需求简称>.md` 同步的完成条件见 [stage-gates.md](stage-gates.md)「正式 PRD 流程完成的唯一判定」，本节不复述。PRD 终稿与飞书交付相互独立。

PRD 涉及配置表时，同步产出 `csv/`、`字段说明/` 和 `csv-config-guide.md`，结构与格式以 [csv-config-deliverable.md](csv-config-deliverable.md) 为唯一权威源。配置交付物不是 PRD 正文的替代品；PRD 保留规则契约，配置交付物保留字段定义、枚举、演示数据和配置顺序。

## 2. 需求调研结论

`00-research-findings.md` 是新正式需求默认的调研产物，由需求发现阶段自动维护；记录事实、证据、冲突、未知项和风险，不是新的确认门。`00-project-context.md` 是旧格式兼容文件；继续历史需求时可以保留，需要进入新流程时由协调 Agent 基于旧文件补充新格式，不删除旧文件。正式调研完成后，协调 Agent 必须把现有 `projectContext` 更新为 `status=completed`、允许的调研文件相对路径和非空版本；L1 也必须生成精简产物。

```markdown
# 需求调研结论

- 需求名称：
- 复杂度：
- 调研时间：
- 调研负责人：
- 调研状态：

## 1. 用户目标与问题

## 2. 当前现状

### 2.1 文档定义

### 2.2 实际实现

### 2.3 数据与用户反馈

没有量化证据时写：当前缺少量化证据。

## 3. 目标状态

## 4. 当前状态与目标状态差异

## 5. 项目约束

## 6. 历史决策与原因

## 7. 外部规则与参考

## 8. 冲突项

| 主题 | 来源 A | 来源 B | 当前判断 | 待确认人 |
|---|---|---|---|---|

## 9. 未知项

## 10. 风险

## 11. 来源索引

| 结论 | 来源类型 | 文件/系统/链接 | 版本或时间 | 可信状态 |
|---|---|---|---|---|

可信状态：当前有效 / 可能过期 / 历史参考 / 存在冲突。

## 12. 调研结论

## 13. 需要用户确认的问题
```

机器门禁只检查最低结构：新格式文件必须非空，并保留「当前现状、目标状态、当前状态与目标状态差异、风险、来源索引」五个稳定标题；这不替代对证据质量和结论完整性的人工/Agent 判断。历史 `00-project-context.md` 至少不得为空。

## 2a. 当前阶段上下文快照

`context-snapshot.md` 由协调 Agent 自动生成和增量更新；用户无需手工维护。它只用于定位当前证据，不覆盖原始权威材料。完整加载、冻结和回读规则见 [context-loading.md](context-loading.md)。

```markdown
# 当前阶段上下文快照

- 快照版本：
- 目标阶段：prd / review
- 需求名称：
- 复杂度：L1 / L2 / L3
- 生成时间：
- 协调 Agent：
- 阶段状态版本：

## 0. 来源版本

| 来源 | 文件 | 版本 | 内容指纹/更新时间 | 状态 |
|---|---|---|---|---|
| 调研结论 | 00-research-findings.md 或旧 00-project-context.md |  |  | 当前 |
| 需求摘要 |  |  |  | 当前 |
| 决策账本 |  |  |  | 当前 |
| 原型 metadata / 豁免 |  |  |  | 当前 |
| 当前 PRD |  |  |  | 当前 |

## 1. 目标与成功标准

每条关键结论注明来源。

## 2. 本期范围

### 包含

### 不包含

## 3. 公共业务核心

- 用户目标：
- 主流程：
- 核心规则：
- 关键状态：
- 关键异常：
- 当前风险：

## 4. 已确认决策

字段与 [决策账本](#3-决策账本) 对齐，只摘取快照所需列；不新增字段、不改状态枚举。

| 决策编号 | 决定 | 状态 | 来源 | 原型证据 |
|---|---|---|---|---|
| D-### |  | 已确认 |  |  |

## 5. 待确认项与阻塞项

仅列当前仍有效的待确认 D-### 和 blocker。

| 编号 | 内容 | 类型 | 阻塞对象 | 待谁确认 |
|---|---|---|---|---|
| D-### / blocker-### |  | 待确认 / 阻塞 |  |  |

## 6. 页面、流程与状态

原型不适用时写正式豁免依据，不虚构页面内容。

## 7. 业务规则摘要

## 8. 配置、数据与技术约束

只保留与当前阶段直接相关的内容。

## 9. 关键异常和边界

## 10. 当前风险

## 11. 证据索引

| 结论/问题 | 权威来源 | 文件或章节 | 是否已核验 |
|---|---|---|---|
```

快照要求：

- 每条关键结论可追溯到权威来源；
- 不复制完整 PRD、完整 HTML、整个项目知识库或无关历史；
- 不把 AI 推断写成已确认事实；
- 与原始材料冲突时以权威原文为准，并重新生成受影响部分；
- 不是新的确认门，不要求用户手工生成。

## 3. 决策账本

```text
决策编号：D-001
主题：
状态：待确认 / 已确认 / 已排除 / 已替代
决定：
信息来源：
决定人：
确认时间：
选择原因：
替代方案：
影响页面：
影响规则：
影响配置和字段：
影响数据和埋点：
关联历史规则：
替代的决策编号：
长期决策候选：是 / 否
```

只有协调 Agent 能把状态改为“已确认”。“长期决策候选”标“是”需同时满足：难回退、无背景会困惑、真有取舍；标“是”的决策访谈结束后经知识维护提案落 `knowledge/decisions/`，标“否”的只存本次工作目录。

## 3a. 术语账本

访谈期间 inline 维护，结晶即写；访谈结束并入《需求理解与方案摘要》「术语表」。

```text
规范术语：
定义：（1–2 句，说“是什么”，不说“做什么”）
avoid 别名：
来源：（用户确认 / 项目知识库 / 历史规则）
长期性：本次需求 / 跨 PRD 复用
```

只收本项目/本需求专属术语，不收通用编程概念。标“跨 PRD 复用”的术语经知识维护提案落 `knowledge/glossary/`。

## 4. 阶段状态

正式需求创建 `00-stage-state.json`。下例是 JSON 1.1 初始实例；必需字段、允许枚举和复杂度策略以 [stage-state.schema.json](stage-state.schema.json) 为唯一权威源，不在本文重复维护词表。

```json
{
  "schemaVersion": "1.1",
  "requirement": {
    "name": "",
    "mode": "existing_module",
    "complexity": "L2",
    "owner": "",
    "currentStage": "requirement_discovery"
  },
  "projectContext": {
    "status": "not_started",
    "file": "",
    "version": ""
  },
  "requirementSummary": {
    "status": "draft",
    "file": "",
    "version": ""
  },
  "prototype": {
    "applicability": "required",
    "status": "not_started",
    "file": "",
    "version": "",
    "confirmedAt": "",
    "waiverReason": "",
    "approvedBy": "",
    "approvedAt": ""
  },
  "prd": {
    "status": "not_started",
    "file": "",
    "version": "",
    "syncedTo": ""
  },
  "review": {
    "status": "not_started",
    "file": "",
    "version": "",
    "openP0": null
  },
  "validation": {
    "status": "not_started",
    "file": "",
    "targetPrdVersion": ""
  },
  "delivery": {
    "required": false,
    "channel": "feishu",
    "status": "not_required",
    "file": "",
    "publishedAt": ""
  },
  "knowledgeProposal": {
    "status": "not_evaluated",
    "file": ""
  },
  "blockers": [],
  "nextAction": "",
  "updatedAt": ""
}
```

只有根编排器可以修改状态。`review.openP0` 在未评审时用 `null`，不得用字段缺失或默认值伪装为 0。重大评审争议复用 `blockers` 标记；无争议直接通过、争议暂停与标记格式统一见 [stage-gates.md](stage-gates.md)，本模板不另立词表。原型 required/waived、PRD 完成、交付状态和机器门禁也以该规范为准。

调研完成后的状态示例：

```json
{
  "projectContext": {
    "status": "completed",
    "file": "00-research-findings.md",
    "version": "v1.0"
  }
}
```

新需求使用 `00-research-findings.md`；历史兼容可使用 `00-project-context.md`。路径必须相对当前需求目录且文件真实存在，不得用其他 Markdown 文件冒充。

需求摘要确认后的状态示例：

```json
{
  "requirementSummary": {
    "status": "confirmed",
    "file": "01-requirement-summary.md",
    "version": "v1.0"
  }
}
```

新需求使用 `01-requirement-summary.md`；历史兼容可使用 `01-requirement-decisions.md`。

## 5. 评审任务

协调 Agent 给评审 Agent 的输入：

```text
评审角色：
任务阶段：
快照文件及 snapshotVersion：
决策账本文件及版本：
确认原型文件及 prototypeVersion：
PRD 文件及 prdVersion：
本次评审范围：
明确不在本次范围：
输出格式：使用“评审问题”

约束：
- 只评审，不修改共享文件
- 不把推断标为已确认
- 不自行扩大范围
- 重大产品分歧交给协调 Agent 和用户
```

## 6. 评审问题

```text
问题编号：
reviewRole：
snapshotVersion：
prdVersion：
prototypeVersion：
reviewedAt：
风险等级：P0 / P1 / P2
关联章节：
关联页面：
关联规则：
问题描述：
影响：
修改建议：
是否建议本期处理：
是否涉及产品决策：
复现场景（攻击轴发现必填）：
```

每个角色的报告头必须记录上述五个版本追踪字段，即使该角色没有问题也不得省略。waived 路径的 `prototypeVersion` 写正式豁免证据版本或 `waived:<批准时间>`；无原型窄任务写 `not_applicable:narrow_task`。

每角色预算：每个启用角色默认只浮出 top 5 发现或 ≤300 字，P0/P1 豁免以免阻塞项被压缩；零发现角色可省略。

协调 Agent 合并前必须检查所有角色使用相同 `snapshotVersion`、`prdVersion`，required 路径的相关角色使用相同 `prototypeVersion`，并检查评审期间输入是否变化。发现过期输入时不得直接汇总为 passed；向过期角色提供当前输入，只重审受影响部分，并记录不一致原因。

合并报告在给出排序列表前，先按角色分段总结（`## <角色名>` + top 发现 + 一句整体裁决；零发现角色省略问题段但保留版本头；标准轴、保真轴、攻击轴（L2/L3）各作一段），再显式记录角色间分歧裁决（分歧双方、风险等级、裁决结果与理由）；P0 条目附反驳尝试记录；最后给重复问题、推荐方案、不建议的过度扩展和 PRD 修改清单。不得把分歧折叠为单一排序列表。

## 7. 变更记录

```text
变更编号：
来源问题：
修改章节：
修改前：
修改后：
修改原因：
影响范围：
同步检查结果：
- 原型：
- 页面文案：
- 客户端：
- 服务端：
- 配置：
- 数据结构：
- 埋点：
- 验收：
- 风险：
```

## 8. 校验报告

```text
# PRD 校验报告

校验结论：通过 / 有条件通过 / 不通过
校验对象及版本：
确认原型版本：

阻塞问题：
格式问题：
完整性问题：
一致性问题：
移动游戏专项问题：
自动修复内容：
需要产品确认的问题：
规则与验收映射缺口：
未标记推断：
```

最终版本条件（原型不适用时，以完整豁免记录替代“原型已确认”）：

- 无 P0
- 核心执行章节完整；按需章节只在实际涉及时存在
- required 原型已确认且 PRD 一致，或正式豁免证据完整且 PRD 未引入 UI/交互变化
- 规则和验收有唯一编号及映射
- 配置命名和字段格式符合规范
- 客户端和服务端职责明确
- 涉及埋点或指标时，事件与口径支持分析目标
- 无未标记推断

## 9. PRD 写作模板

```markdown
# <需求名称>

- 版本：
- 负责人：
- 状态：
- 复杂度：L1 / L2 / L3
- 计划版本：
- 关联原型：

## 1. 功能说明

### 实现目标

### 改动范围

### 涉及模块

| 模块 | 本次影响 |
|---|---|

## 2. 总体流程

简单需求使用编号步骤；复杂需求先按 `prd-spec.md` 判断图型，再按需读取 `prd-diagrams.md` 对应章节。

## 3. 功能规则

| 规则ID | 场景/条件 | 业务规则 | 客户端处理 | 服务端处理 | 最终结果 |
|---|---|---|---|---|---|

## 4. 页面和交互

仅 UI/交互变化时生成。

## 5. 接口、数据和配置

只生成实际涉及的小节；不生成运营后台章节。

## 6. 异常和边界

| 场景 | 客户端表现 | 服务端处理 | 最终数据 | 恢复方式 |
|---|---|---|---|---|

## 7. 验收标准

| Case ID | 关联规则 | 前置条件 | 操作 | 预期结果 |
|---|---|---|---|---|

生成记录：<创建人> · <带时区时间> · mobile-game-product-forge <版本> · <模式> · 知识来源：<模块或无>
```

多模块默认只填“涉及模块”表，不逐模块拆章。只有形成独立业务闭环时，才在“功能规则”内按业务能力分组。完整配置表、埋点、三方依据、状态机、迁移和灰度模板见 [prd-spec.md](prd-spec.md) 对应条件触发专项。

## 9a. 配置 CSV 说明模板

PRD 涉及配置表时使用，文件名为 `csv-config-guide.md`，与 `csv/`、`字段说明/` 放在同一需求目录。详细格式与字段说明写法见 [csv-config-deliverable.md](csv-config-deliverable.md)。

```markdown
# CSV 配置说明

## 1. 配置目标

- 本系统通过配置表控制……
- 与相邻系统的边界：……

## 2. 表清单与配置顺序

| 顺序 | 表名 | 依赖表 | 配置目标 | 优先级 |
|---|---|---|---|---|
| 1 | example.csv | 无 | 示例表 | 必须先配 |

## 3. 每张表的字段概述

### example.csv

| 字段 | 类型 | 概述 |
|---|---|---|
| Id | string | 唯一标识 |
| Name | string | 显示名称，需翻译 |

## 4. 系统配置顺序

1. 先配置……
2. 再配置……
3. 最后配置……

## 5. 边界与回滚

- 新增字段时……
- 配置错误时……
```

## 10. 交付记录

仅在项目交付策略要求或用户明确执行交付时写入 `08-delivery-record.md`。交付记录不决定 PRD 是否已终稿；发布失败记录 `delivery.status=failed`，不回退 `prd.status=final`。PRD 正文的紧凑生成记录以主 `SKILL.md`「文档来源信息」节为唯一权威源；交付记录为独立审计产物，可保留下面的详细发布字段。详见 `skills/game-prd-publish/SKILL.md`。

```text
创建人：
创建时间：
使用的 Skill：mobile-game-product-forge
Skill 版本：（随包发布，见 package.json）
需求处理模式：模式1 / 模式2 / 模式3
是否关联项目知识库：是 / 否
使用的知识模块：

飞书文档 URL：
飞书 node_token：
发布时间：（带时区 ISO 8601）
发布状态：成功 / 部分成功 / 失败
待确认项：
```

## 11. 知识维护提案

知识维护提案写入 `09-knowledge-proposals.md`，按状态词追踪提案-落库交接。字段与 `project-knowledge.md` 第 5 节一致（唯一权威），本节补充状态词表与持久化结构。AI 只追加提案并维护状态词，不写 `knowledge/`；落库由人工回填。

```text
提案编号：KP-<模块>-NNN
目标知识模块：
目标文件：
变更类型：新增 / 修订 / 废弃 / 替代
触发来源：
现有知识：
拟变更内容：
证据：
影响范围：
冲突与风险：
需要人工确认：
建议负责人：
状态：待确认 / 已采纳待写入 / 已落库 / 已驳回
落库时间：（人工回填，带时区 ISO 8601）
落库人：（人工回填）
```

状态词表：`待确认`（提案已提出，等用户逐项确认）→ `已采纳待写入`（用户确认，等人工落库）→ `已落库`（人工落库完成，回填时间与落库人）/ `已驳回`（用户否决，保留记录备查）。跨会话可审计：`已采纳待写入` 即待办知识变更清单。
