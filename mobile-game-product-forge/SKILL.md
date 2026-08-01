---
name: mobile-game-product-forge
description: Default entry for any new, broad, end-to-end, continued, or formal iOS/Android game product requirement when the user has not explicitly limited the request to one narrow stage. Orchestrates evidence-backed research, prototype applicability, PRD, review, validation, and optional delivery across gameplay, live operations, monetization, ads, IAP, subscriptions, accounts, configuration, analytics, experiments, and SDK integrations. Broad requests such as designing a system, adding a feature, revising a module, or writing a formal PRD must route here rather than directly to a stage sub-skill.
---

# 移动游戏产品需求工坊

当前 Skill 版本：`3.4.0`

版本唯一来源为仓库根目录 `package.json` 的 `version` 字段；`CHANGELOG.md` 记录变更。本文件的版本字段与 `.claude-plugin/plugin.json` 的版本必须与之一致，由 `scripts/validate.sh` 校验。知识包 `PACK.md` 维护各自独立的包版本，不与 Skill 版本绑定。

## 目标

把移动游戏产品想法、已确认原型或现有 PRD 转化为产品、设计、客户端、服务端、测试、数据和运营可以执行的需求。先识别当前阶段，只补齐缺失环节；绝不把推断伪装成已确认需求。

## 开始前

1. 启动或恢复前先执行 [references/workflow.md](references/workflow.md) 第 0 节的三条启动规则：新需求创建任何文件前确认落点（0.1）；「继续上次」类恢复请求消歧到唯一需求目录后才读写状态（0.2）；存量/外部 PRD 只求评审时走窄任务接入、不发状态源（0.3）。
2. 正式需求先读取 `00-stage-state.json`；新需求则建立共享工作目录，并从 [references/templates.md](references/templates.md) 创建 JSON 1.1 状态。结构与枚举以 [references/stage-state.schema.json](references/stage-state.schema.json) 为权威。历史 YAML 不强制迁移，新需求不得再生成 YAML。窄任务明确标记 `narrow_task`，不伪造正式流程状态。
3. 根据状态和用户当前输入判断阶段：想法、访谈中、需求已确认、原型已确认、PRD 待评审、PRD 待校验，或窄任务。
4. 默认按“状态 → 当前阶段记录的当前文件 → `context-snapshot.md` → 当前阶段必要共享合同/子 Skill”读取，先检查证据完整性，再决定是否读取相关原文或扩展原文。
5. 按“需求处理模式”读取项目知识索引；只读当前需求直接相关模块和当前有效版本。
6. 根据识别出的阶段，只读取需要的其他参考文件：
   - 模式1或模式2先读取目标项目的 `knowledge/INDEX.md`；只读取索引登记且与当前需求直接相关的知识。
   - 涉及埋点、指标或数据需求时，读取项目知识库登记的埋点规范和事件基线，先完成已有事件去重，再设计新增或扩展项。
   - 写 PRD、配置、字段、埋点或验收时，读取 [references/prd-spec.md](references/prd-spec.md)。
   - PRD 判断需要图时，只读取 [references/prd-diagrams.md](references/prd-diagrams.md) 对应图型章节；不默认加载整份图形规范。
   - 涉及设备适配、生命周期、网络、资产、广告、IAP、时间、版本或上线时，读取 [references/mobile-game-checklist.md](references/mobile-game-checklist.md)。
   - 创建或更新交付文件时，读取 [references/templates.md](references/templates.md)。

上下文加载以 [references/context-loading.md](references/context-loading.md) 为唯一共享合同，其「快速执行索引」是各阶段加载清单的唯一权威源：先读该表，再按「根编排器」行的默认章节加载，其余章节按各阶段行与触发器读取；本节不复制章节清单。README、操作指南、全部 references、全部子 Skill、完整需求目录、历史材料集合和完整 HTML 均不在默认输入中；但证据不足、来源冲突、高风险、用户追溯或无法确认是否遗漏时必须自动扩大读取。快照和角色切片只用于定位，不是业务权威源。

## 用户入口与操作指南

- 用户询问“怎么开始”“怎么继续”“完整流程是什么”时，优先读取目标项目的 `docs/mobile-game-product-forge/operation-guide.md`，告诉用户文件路径并给出与当前阶段匹配的启动提示词。
- 项目内指南不存在时，读取本 Skill 的 [operation-guide.md](operation-guide.md)，并提示用户显式调用 `$setup-mobile-game-product-forge` 将指南写入项目。
- 新的正式需求必须从 `$mobile-game-product-forge` 启动；直接调用子 Skill 只视为明确的窄任务。

## 项目知识库

项目知识库是项目长期记忆，不是本次需求的临时材料，也不属于通用 Skill 的默认安装内容。完整发现、读取、缺失处理和维护边界见 [references/project-knowledge.md](references/project-knowledge.md)。

硬性规则：

1. 先查找项目根目录的 `knowledge/INDEX.md`，再按索引读取与本次需求直接相关的架构、模块、UI、配置、埋点和决策知识。
2. 默认只读。PRD、分析结果、推断、评审建议和背景更新建议均不得直接写入 `knowledge/`。
3. 知识缺失、过期或互相冲突时，记录缺口和影响，不自行补全。
4. 用户要求维护知识时，进入独立的“知识维护提案”流程，只输出目标文件、依据、拟变更内容、冲突和待人工确认项；本 Skill 不直接写入知识库。
5. 模式3不得读取项目知识库，也不得使用兼容的项目背景、项目埋点或历史决策文件。

若项目没有知识库，Skill 仍可使用：模式1或模式2必须报告知识缺口，只依据用户本次资料和通用规范继续；模式3不受影响。不得自动读取仓库内未安装的 `knowledge-packs/`。

需要为项目创建知识目录或安装可选知识包时，必须由用户显式调用 `setup-mobile-game-product-forge`；正常PRD流程不承担初始化职责。

## 需求处理模式

模式判断先于阶段路由。阶段路由决定“需求成熟到哪一步”，模式决定“是否以及如何使用项目历史”，两者不可互相替代。

| 模式 | 判断条件 | 知识读取 | 核心处理 |
|---|---|---|---|
| 模式1：已有模块迭代 | 需求命中知识库中已有模块、配置、页面或能力 | 读取项目架构、对应模块、相关UI/配置/埋点、历史决策与版本 | 识别复用点、改动点、影响模块和兼容风险，基于已有架构推进分析与PRD |
| 模式2：新增独立模块 | 知识库无对应模块，或需求形成独立玩法/系统边界 | 读取项目架构、相邻模块、公共能力、UI/配置/埋点规范与相关决策 | 设计模块边界及整体框架，说明接入点、复用能力、依赖、影响和新增资产 |
| 模式3：通用规范模式 | 用户明确要求不关联项目历史或只按通用规范处理 | 不读取任何项目知识库或兼容项目知识源 | 仅使用通用 Skill 规则和用户本次材料；仍执行需求确认与原型适用性判断 |

判断顺序：

1. 用户明确要求“不关联项目历史”“不读取知识库”时，直接使用模式3。
2. 否则读取知识库索引并识别所属模块；命中已有模块使用模式1。
3. 未命中且能够形成清晰独立边界时使用模式2。
4. 所属模块或是否独立会显著改变方案时，标为“模式待确认”，只问必要问题，不擅自选择。

模式1重点检查：现有能力能否复用、已有配置是否修改、历史版本是否兼容、是否影响其他模块；并主动索取该模块现状飞书文档读取背景（`lark-cli docs +fetch`），不重复且有长期价值则提案归档到 `knowledge/requirements/`。

模式2重点检查：如何融入整体架构、与已有系统的关系、可复用公共能力，以及是否新增配置、数据、UI规范和埋点。
模式3只跳过项目知识读取，不跳过需求理解、原型确认、评审争议等既有确认门。

## 信息与证据权威

不得用一条线性优先级同时判断产品目标、当前线上现状和外部约束。统一模型见 [references/context-loading.md](references/context-loading.md)「三类权威来源模型」：

- 产品目标：用户最新明确确认优先；已确认摘要/决策、确认原型和已评审 PRD 发生冲突时不得静默覆盖。
- 当前现状：以当前线上行为、代码、正式配置、接口/数据库等实际证据为强证据，但不得把当前缺陷直接当目标规则。
- 外部约束：平台政策与合规使用适用于目标地区和目标发布日期的最新官方规则；SDK、API 和技术行为使用与当前接入版本或明确目标升级版本匹配的官方文档；升级任务同时核查源版本、目标版本和官方迁移指南。

发现冲突时按合同「冲突处理：当前状态、目标状态与改动」输出来源版本、当前状态、目标状态和需同步产物。AI 推断必须标为“待确认”，不得覆盖确认决策或写入最终 PRD 的已确认规则。

## 阶段路由

| 当前输入 | 从哪里开始 |
|---|---|
| 一句话或模糊想法 | 需求调研（用户、现状、证据）→ 摘要草稿 |
| 访谈中 | 按访谈规则继续推进，不重新开始 |
| 已有明确需求摘要 | 核对关键决策 → 需求理解确认 |
| 已确认可交互原型 | PRD 生成 |
| 已有完整 PRD（待评审） | 评审 → 修订 → 校验 |
| PRD 已通过评审，只待校验 | 只校验（跳过评审，不重复评审已通过项） |
| PRD 终稿且通过校验 | 正式 PRD 流程完成；知识提案与按项目策略交付为独立分支 |
| 已有飞书 PRD 待重审 | `lark-cli docs +fetch` 拉取为快照 → 评审（缺原型支撑标待确认，提示回 `game-prototype`） |
| 只要配置、字段、埋点或验收 | 只执行该窄任务并检查直接依赖 |

不要机械执行完整流程。窄任务不需要强制制作原型或整份 PRD。

所有正式需求都必须完成需求调研，但正式 PRD 不一定需要原型。固定顺序是：调研完成并由编排器写入 `projectContext` → 需求理解确认 → 判断原型适用性；`required` 进入原型确认并要求 metadata `COMPLETE`，`not_applicable` 由产品负责人确认豁免后直接进入 PRD 门禁。

## 子 Skill 编排

本编排器持有并唯一写入 `00-stage-state.json` 中的跨阶段状态：需求处理模式、复杂度、原型适用性、三个产品确认点、PRD 与交付状态、信息优先级、共享工作目录、版本号与多 Agent 协议。各阶段具体执行规则由对应子 Skill 承担。编排器位于仓库根的理由见 [ADR-0006](.agents/adr/0006-root-orchestrator-at-repo-root.md)。

| 阶段 | 子 Skill | 触发 |
|---|---|---|
| 需求调研 -> 需求摘要草稿 | `game-requirement-discovery` | 所有正式需求；完成后由编排器写入 `projectContext.status=completed`、调研文件相对路径和版本，再发起需求理解确认 |
| 交互原型生成与迭代 | `game-prototype` | 需求理解确认且原型适用时 |
| PRD 生成 | `game-prd-writing` | 原型确认或原型豁免后 |
| 多角色评审 -> 评审处理 -> 校验 | `game-prd-review` | PRD 初稿存在时 |
| 埋点与指标设计 | `game-analytics-design` | 独立埋点/指标窄任务，或 PRD 写作前需深化埋点方案时由编排器委派；正式流程中埋点默认由 `game-prd-writing` 按 prd-spec「埋点和指标」产出 |
| 项目知识维护提案 | `game-knowledge-maintenance-proposal` | PRD 完成后的独立分支；L3 必须评估 |
| PRD 发布与交付（飞书云文档） | `game-prd-publish` | PRD 完成且项目交付策略要求，或用户显式“只发布” |

调用边界：

- 新功能、新系统、已有模块迭代、继续历史正式需求、正式 PRD，以及没有明确限定阶段的自然语言请求，统一由根编排器处理。
- 子 Skill 只在两种情况下执行：根编排器明确委派当前阶段；或用户明确要求“只做调研 / 只做原型 / 只评审 / 只补埋点 / 只做知识提案”等单一窄任务。仅出现“设计、优化、增加、修改、写需求”等宽泛表达，不足以直接触发子 Skill。
- 子 Skill 独立执行窄任务时，自行完成本环节并输出，不承担跨阶段编排；必须标记 `narrow_task`，不创建或修改正式状态，也不声称完成完整正式流程。
- 编排器委派子 Skill 时，负责在其前后执行确认门、更新状态与版本；进入下游阶段前按 [references/stage-gates.md](references/stage-gates.md) 运行机器门禁；正式 `review / validation / final / publish / delivery` 继承全部上游共同前置。子 Skill 只读状态、校验门禁并返回本环节产物与待确认问题。状态写入时机严格按该规范「标准状态迁移」执行，不提前提升状态。

路由基线：

| 用户意图 | 入口 | 执行模式 |
|---|---|---|
| 新功能、新系统、模块改版、继续正式需求、写正式 PRD | `mobile-game-product-forge` | 正式编排 |
| 终稿后需求变更（重开修订） | `mobile-game-product-forge` | 正式编排：按 [references/stage-gates.md](references/stage-gates.md)「终稿后重开修订」事件执行 |
| 明确“只调研/只澄清，不继续原型或 PRD” | `game-requirement-discovery` | `narrow_task` |
| 明确“只做/迭代可点击原型” | `game-prototype` | `narrow_task` |
| 明确“只评审/只校验这份已有 PRD” | `game-prd-review` | `narrow_task` |
| 明确“只补埋点、指标或实验口径” | `game-analytics-design` | `narrow_task` |
| 明确“只生成非正式 PRD 草稿” | `game-prd-writing` | `narrow_task`，显式调用 |
| 明确“只发布已终稿 PRD” | `game-prd-publish` | 显式调用 |
| 初始化或重新配置项目 | `setup-mobile-game-product-forge` | 用户显式调用 |
- `game-prd-publish` 仅负责交付，不确认 PRD 内容；`delivery.required=false` 时不调用。飞书交付失败只写 `delivery.status=failed`，不回退 `prd.status=final`。发布经 lark-cli/飞书云文档而非本地 PDF 的理由见 [ADR-0002](.agents/adr/0002-publish-via-lark-cli-not-pdf.md)；完成与交付拆分见 [ADR-0009](.agents/adr/0009-separate-prd-completion-from-delivery.md)。
- 独立调用状态合同：子 Skill 作为窄任务独立调用时，直接输出本环节产物与待确认问题，不更新正式流程状态。单次需求目录的变更记录与 Skill 仓库根 `CHANGELOG.md` 是两类文件，不得混写；如需修改既有共享文件，输出建议修改清单交由用户决定，或提示回到编排模式。
- 消费边界（synthesize-don't-re-interview）：子 Skill 以已确认原始材料为权威，以编排器提供的快照作证据导航；不重新访谈、不重新推导上游已确认决策。快照证据不足时自动回读相关原文，上游真实缺口才标为待确认项交回，不自行假设填充。
- 合并点（on-ramp 至命名检查点）：窄任务独立调用发现需回上游时，合并至命名检查点而非在当前层打补丁--独立评审发现原型级问题 -> 合并至交互原型确认门；独立埋点发现指标口径冲突 -> 合并至需求理解确认门；独立发布发现 PRD 未过校验 -> 合并至校验门；独立发布发现 PRD 未终稿 -> 合并至终稿；独立原型改变核心规则 -> 合并至需求理解确认门。

## 三个产品确认点

**铁律：没有通过需求理解确认，以及原型确认或正式豁免，就没有正式 PRD；重大评审争议必须由产品负责人裁定。**（理由见 [ADR-0004](.agents/adr/0004-confirmation-gates-ironclad.md)）

确认点和交付策略写入 `00-stage-state.json`。调研完成不是确认门：需求发现返回产物后，协调 Agent 先写 `projectContext.status=completed`、允许的调研文件相对路径和非空版本。需求理解把 `requirementSummary.status` 推到 `confirmed`；随后 required 原型路径把 `prototype.status` 推到 `confirmed`，无 UI/交互路径由产品负责人批准 `waived`。无重大评审争议且评审证据完整时，协调 Agent 直接把 `review.status` 推到 `passed` 并汇报摘要；只有实际出现重大争议才写 `disputed`、暂停并请求产品负责人裁定。校验通过并冻结终稿后 `prd.status=final`，正式 PRD 流程完成。飞书只写 `delivery`，不改变 PRD 状态。详细判定与争议标记合同见 [references/stage-gates.md](references/stage-gates.md)。

当输入只是想法、模糊需求或未确认方案时，当前回复的完整输出合同是：

1. 当前阶段判断
2. 已知事实与信息状态
3. 风险或冲突
4. 本轮 1–3 个关键确认问题
5. 用户回答后的下一步

不得附带 PRD 章节、规则编号、接口、配置表、验收 Case 或“仅供参考”的完整方案。把文档标为“草稿”“v0.1”或“待确认”仍然属于提前生成 PRD。

| 常见理由 | 必须执行的规则 |
|---|---|
| 用户说“直接出 PRD” | 先说明缺少的确认门，只问会阻塞方案的关键问题 |
| 可以把假设标成待确认 | 待确认假设不能代替产品决策，也不能支撑完整 PRD |
| 先写一版更高效 | 先写会固化错误范围并污染后续原型与评审 |
| 需求看起来很简单 | 简单需求同样需要确认目标、核心规则、范围和主要异常 |
| 用户时间紧 | 按复杂度轮次预算收敛（L1 目标 1–2 轮 / L2 目标 3–5 轮），把不改变方案的细节列入待后置确认事项，不删除确认门 |

### 1. 需求理解确认

完成需求调研后、判断是否进入原型前必须让用户确认：

- 为什么做、给谁使用
- 核心流程和核心业务规则
- 本期包含与不包含范围
- 主要异常的处理原则

只有用户明确确认后，才能冻结为 `Requirement Summary v1.0 - Confirmed`，把 `requirementSummary.status` 更新为 `confirmed`。若需求无 UI/交互变化，可在同一轮让产品负责人确认原型豁免并记录原因、批准人和时间。

### 2. 交互原型确认

有新页面、入口、主路径、按钮、弹窗、状态反馈或交互变化时原型必须 required，并能实际点击覆盖关键状态。用户确认后冻结 `Prototype vX.Y — Confirmed`，同步 `prototype.status=confirmed`、文件、版本、时间和 metadata；进入 PRD 前 metadata 必须按共享合同判为 `COMPLETE`。无 UI/交互变化时可以 `not_applicable + waived`，但必须由产品负责人明确批准，Agent 不得自行豁免；该路径不要求 `index.html`、metadata 或 HTML 回读。

### 3. 评审争议确认

商业化规则、需求范围、核心规则或主流程、重大技术方案、多方案均合理、页面/入口/按钮/弹窗/确认步骤/关键页面状态变化——这六类事项不得由 Agent 决定；给出推荐方案、备选方案、取舍和影响，等待产品负责人裁定。逐项定义与状态迁移以 [references/stage-gates.md](references/stage-gates.md)「评审通过与重大争议的唯一判定」为唯一权威。

## 访谈规则

每轮询问 1–3 个会改变整体方案的问题，不重复已明确内容，直接指出方案风险并给出推荐与备选；满足确认门后输出《需求理解与方案摘要》再请求确认。访谈主题顺序、决策/术语账本、轮次预算与收敛规则以 `skills/game-requirement-discovery/SKILL.md` 为唯一权威。

## 原型规则

先判断适用性：有 UI/交互变化必须制作原型；无 UI/交互变化可由产品负责人正式豁免，复杂度不能替代适用性判断。原型是单次需求、模块级的可点击评审产物（默认自包含单文件 `02-prototype/index.html`），主流程必须可点击走通，不修改正式游戏代码；生成规则、设备默认值、评审工具栏、决策编号 `D-###`、内嵌原型元数据、迭代与异常处理以 `skills/game-prototype/SKILL.md` 为唯一权威。

## PRD 与评审

- 正式 PRD 必须使用已完成的调研结论、需求摘要、确认决策和确认原型/豁免证据，并区分当前实现与目标规则；按 [references/prd-spec.md](references/prd-spec.md) 的统一研发执行结构写作，所有核心规则使用唯一 `R-###` 编号且至少映射一个可判定 `AC-###`。写作细节以 `skills/game-prd-writing/SKILL.md` 为唯一权威。
- 复杂度决定内容深度与评审重量（L1 精简、1–2 个直接专业角色；L2 标准、动态相关角色；L3 完整、全部相关角色），机器可读策略与横切检查重量以 [references/stage-gates.md](references/stage-gates.md)「复杂度路由」为唯一权威；产品负责人可调整级别。L1 不默认知识提案，L3 必须评估知识提案。
- 评审角色独立输出问题，不直接编辑 PRD，不决定重大产品问题；协调 Agent 合并重复问题和角色分歧后统一修订。无重大争议、P0 清零且 P1/P2 已记录处理结论时直接通过评审并汇报摘要，不增加用户确认轮次；有重大争议（含页面、入口、主路径、按钮、弹窗、确认步骤或关键页面状态变化）写 `disputed` 并暂停，裁定改变交互后先返回原型重新确认，再更新 PRD 并只重审受影响部分。角色清单、横切轴与收口细节以 `skills/game-prd-review/SKILL.md` 为唯一权威。
- 资产、奖励、次数、权限、支付和广告奖励的最终结果以服务端校验为准；客户端只做体验性校验。

## 文档来源信息

所有正式生成的 PRD、产品方案、需求分析、评审报告和校验报告，在文档末尾保留一行紧凑生成记录，不占用研发正文：

```text
生成记录：<创建人> · <带时区时间> · mobile-game-product-forge 3.3.0 · <模式> · 知识来源：<模块或无>
```

- 创建人优先读取当前项目 Git `user.name`；无 Git 配置时使用当前用户名称；仍不可得时写“待补充”，不得猜测。
- 创建时间使用带时区的 ISO 8601 时间。
- 知识来源只列实际使用的模块名和版本/更新时间；完整路径保留在调研或证据索引中，未读取写“无”。
- 模式3固定写“知识来源：无”。
- 引用知识结论时保留来源路径；知识缺失不等于可以推断。

## 多 Agent 统一协议

此协议与 Agent 品牌和调度工具无关：

1. 协调 Agent 是 `00-stage-state.json` 的唯一写入者，负责用户确认、阶段状态、版本号、合并和最终输出；其他 Agent 只读。
2. 所有 Agent 使用同一冻结 `context-snapshot.md`、公共业务核心和当前产物版本，不依赖聊天记忆传递事实；快照不是权威源，证据缺口按共享合同回读原文。
3. 评审 Agent 的输入必须包括：任务阶段、冻结快照版本、公共业务核心、当前 PRD 版本、原型 metadata 或豁免证据、评审角色、专业增量章节和输出格式。
4. 评审 Agent 只返回问题与建议，并在报告头记录 `reviewRole`、`snapshotVersion`、`prdVersion`、`prototypeVersion`、`reviewedAt`；禁止修改共享文件、扩大范围或把推断标为确认。
5. 协调 Agent 合并前检查所有角色输入版本一致；过期角色只重审受影响部分，不得直接通过。版本一致后再读取冻结快照、当前 PRD 和角色问题列表，检查跨角色理解冲突；仅在冲突或证据不足时扩大原文读取，再处理安全修订项和争议项。
6. 每次写入共享文件后更新产物版本和本需求目录的变更记录（若存在）。Skill 仓库根 `CHANGELOG.md` 只记录 Skill 能力变更，不记录单次产品需求。

如果运行环境没有并行或子 Agent 能力，由一个 Agent 按角色顺序独立评审；输出合同保持不变。

## 校验与完成

最终标记前检查：

- 无 P0 问题，核心执行章节完整；条件章节只在实际涉及时生成
- required 原型已确认且 PRD 一致，或正式豁免证据完整且 PRD 未引入 UI/交互变化
- 规则编号、验收编号唯一且存在映射
- 配置表名、字段命名和字段格式合规
- 客户端与服务端职责清晰
- 涉及埋点或指标时，事件与口径能够支持分析目标
- 移动游戏专项风险已检查
- 所有推断和未决项均有明确标记

阶段顺序机器门禁由 `scripts/check-stage-gate.py` 完成；配置表、埋点表与编号格式的机器校验由 skill 仓库的 `scripts/lint-prd.py` 完成（调用方式见 [game-prd-review](skills/game-prd-review/SKILL.md) 校验环节），产出 `06-lint-report.md`；检查清单中的「规则/验收编号映射」与「配置表名及字段格式合规」两项以脚本结论为准。

校验不通过时输出报告并继续修订，不得把文档称为“最终版”。

正式 PRD 流程是否完成，按 [references/stage-gates.md](references/stage-gates.md)「正式 PRD 流程完成的唯一判定」判断，本节不复述条件。完成后两个分支互相独立：

- 知识维护：L1 默认不生成，L2 按长期价值决定，L3 必须评估；提案不得直接写入知识库。
- 项目交付：仅 `delivery.required=true` 时调用 `game-prd-publish`；失败记录 `delivery.status=failed`，不回退 PRD。`required=false` 时无需飞书即可完整完成。
