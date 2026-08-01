---
name: game-prd-writing
description: Use only when the root mobile-game-product-forge orchestrator has passed the formal PRD gate and explicitly delegates writing, or when the user explicitly requests only a clearly labeled non-formal PRD draft. Converts confirmed research plus a confirmed prototype or approved prototype waiver into an implementation-ready mobile-game PRD. Broad requests to design a feature or write a formal PRD must route to the root orchestrator first.
---

# 游戏 PRD 写作

负责移动游戏需求工坊的「PRD 生成」环节。把已确认需求摘要与已确认原型或正式原型豁免转化为可执行 PRD。

本子 Skill 是 `mobile-game-product-forge` 的能力拆分。需求处理模式、确认门、版本号和共享工作目录由编排器持有；正式编排时本子 Skill 只读阶段状态并验证门禁，不修改跨阶段状态。

## 前置条件

1. 正式需求调研状态=`completed`，允许的调研文件存在且版本非空。
2. 需求摘要状态=`confirmed`，且 required 原型已确认，或 not_applicable 原型豁免已由产品负责人批准。
3. 存在已确认的产品决策记录。

## 正式流程门禁

正式编排调用时，写 PRD 前必须读取工作目录 `00-stage-state.json`，并执行 `check-stage-gate.py --target prd`。两条路径共同检查调研与需求摘要证据；required 路径要求原型确认、版本一致且 metadata `COMPLETE`，waived 路径只检查原因、批准人和批准时间，不要求 `index.html` 或 metadata。退出码非 0 时不得生成 PRD 章节、`R-###`、接口、配置表或验收 Case。required 历史原型因 `INCOMPLETE` / `INVALID` 阻塞时，先按共享合同完成定向 HTML 核验和 metadata 补齐、重跑门禁；补齐失败则返回原型阶段。not_applicable 路径不得触发该兼容流程。

用户自然语言要求“写正式 PRD”时应优先进入 `$mobile-game-product-forge`。直接调用本 Skill 且缺少通过门禁的 JSON 状态时输出 `BLOCKED` 并提示从根编排器启动/恢复。只有用户明确要求“纯文档草稿/非正式 PRD”时，才可输出标记为 `narrow_task` 和“非正式产物”的草稿；不得伪装成完整流程终稿，也不得修改 `00-stage-state.json`。

## 上下文加载

默认读取：`00-stage-state.json`、目标为 `prd` 的当前 `context-snapshot.md`、当前需求摘要、当前决策账本、`prototype-meta` 或正式豁免证据，以及 PRD 规范。强制输入是必须被证据覆盖的来源集合，不表示每轮把每份原文完整加载。

不默认读取：完整 `index.html`/CSS/JavaScript/模拟数据、旧 PRD、已替代原型、历史评审报告、整个项目知识库或完整需求目录。快照缺少来源、材料冲突、metadata 不足、无法形成明确验收、用户要求追溯或命中高风险业务时，按 [上下文加载合同](../../references/context-loading.md)「快速执行索引」中「PRD」行的默认与触发扩展章节自动读取相关原文并扩大范围。

## 强制输入

```text
项目背景（若有）
+
需求访谈记录
+
需求理解与方案摘要（01-requirement-summary.md）
+
已确认产品决策
+
已确认原型或产品负责人批准的原型豁免
+
团队模板和字段规范（若有）
```

发现调研结论、摘要、决策、原型、配置、当前实现、历史规则或用户前后决定冲突时，停止受影响部分，按共享合同分别输出当前状态、目标状态、差异、来源版本、影响、建议处理和确认人。不得把当前实现直接当目标规则，也不得把历史 PRD 直接当线上事实。

## 写作规则

- PRD 必须使用项目背景（若有）、访谈记录、需求摘要、确认决策和确认原型/豁免证据。
- 按 [../references/prd-spec.md](../../references/prd-spec.md) 的统一研发执行结构写作；新 PRD 使用 7 个主章节，历史 20 章 PRD 仅作兼容。
- 所有核心规则使用唯一 `R-###` 编号；每条核心规则至少有一个可判定的 `AC-###` 验收 Case。
- 资产、奖励、次数、权限、支付和广告奖励的最终结果以服务端校验为准；客户端只做体验性校验。
- 初稿版本为 `v0.1`。
- 复杂度深度：L1/L2/L3 使用同一主结构，只调整内容深度和条件触发专项；不生成章节裁剪决定，不写空章或“不适用”占位。
- 流程重量：L1 输出精简 PRD 并只进入 1–2 个相关角色评审；L2 走标准动态评审；L3 输出完整 PRD 并进入完整相关角色评审。复杂度由协调 Agent 推荐、产品负责人可调整。
- 多模块控制：先在“涉及模块”表记录影响范围，正文仍按统一流程和 `R-###` 规则组织。不得按客户端、服务端、数据库、配置表、埋点或通用服务拆功能章节。只有业务部分具备独立入口、流程、规则集合、数据生命周期或验收闭环中的至少两项时，才可在“功能规则”内按业务能力分组；普通需求不超过 5 组。
- 运营控制：项目不生成运营后台章节；运营调整全部写入配置表合同，说明字段、默认值、读取方、生效方式、错误配置、兼容和回滚。

- 图形选择：简单流程用编号步骤；按 `prd-spec.md`「图形规范」先判断是否需要图；触发后只读取 [../references/prd-diagrams.md](../../references/prd-diagrams.md) 对应图型章节，在业务流程图、页面流转图、时序图、状态机图、模块关系图、数据流图中按问题选择。每张图只解决一种问题，普通 L2 建议不超过 2–3 张，不机械生成。Mermaid 源保留在 Markdown，发布到飞书时可转原生画板。
- 原型截图：页面和交互的关键状态需配原型截图，截图由用户提供。写作时按页面与状态列出所需截图清单（如「商城页-默认/loading/失败」），请用户提供对应图片文件；PRD 中标注占位文件名与状态，用户未提供时在该处写「待补充截图：<页面>-<状态>」，不阻塞写作。
- 数据来源标注：动态展示值、计算结果、奖励、次数、权限和价格首次出现时标明权威来源（`配置表.字段` / 服务端接口字段 / 客户端本地 / 用户输入 / 埋点）；固定静态文案不机械标注，见 `prd-spec.md`「数据来源」。
- 实现细节与原型片段：PRD 写决策不写实现，禁游戏码路径与拷贝框架代码；来自原型的决策片段可内联并标「（来自原型 vX.Y）」，裁到决策富集部分，见 `prd-spec.md`「实现边界与原型交接」。
- 三方对接：涉及第三方（苹果支付/Google Play/广告 SDK/登录分享推送等）按适用地区、目标发布日期和当前/目标 SDK 版本匹配官方文档；升级同时核查源版本、目标版本与官方迁移指南。仅在触发时增加专项依据，文档未明示标“待确认”。

## 配置 CSV 交付物

PRD 涉及配置表时，必须先产出或更新以下三类配置交付物，再写 PRD 配置章节正文。本步骤是配置章节的共同前置，不得跳过或后置。

1. **原始配置表** `csv/<table_name>.csv`
   - 前 4 行固定表头：中文字段名、翻译标记 0/1、PascalCase 英文字段名、字段类型。
   - 第 5 行起为演示数据，覆盖主流程与边界情况。
   - 英文字段名在同一表内不得重复。
2. **字段说明文档** `字段说明/<table_name>.csv 字段说明文档`
   - 逐字段说明类型、作用、为空时填写、配置说明。
   - 枚举含义、边界情况、ID 规则必须写清。
3. **配置总览** `csv-config-guide.md`
   - 说明每张表的配置目标、字段概述、依赖关系。
   - 给出整个系统的配置顺序和边界/回滚说明。

详细格式、命名和禁止事项以 [../references/csv-config-deliverable.md](../references/csv-config-deliverable.md) 为唯一权威源。PRD 正文保留规则契约（`R-###`、读取方、生效方式、异常处理），不重复复制字段说明；配置交付物作为 PRD 的配套产物写入同一需求目录。

## 原型到 PRD 交接

required 路径必须把「已确认原型」当作目标产品交互决策来源之一，不只参考截图。默认先用 `check-stage-gate.py --extract-prototype-meta` 提取 metadata，避免把完整 HTML 放入模型上下文。not_applicable 路径必须在文档信息中记录豁免原因、批准人和批准时间，跳过全部原型提取、历史兼容和 HTML 回读且不得虚构 UI。required 路径的交接规则如下：

- `COMPLETE`（退出码 0）作为第一层输入；`INCOMPLETE`（退出码 2）读取 `missingFields` / `invalidFields` / `duplicateIds` 并定位相关 HTML；`INVALID`（退出码 3）从容器或 JSON 缺口定位相关 HTML。按实际证据补齐 metadata、标记历史兼容核验并重新分类，只有 `COMPLETE` 后才继续正式 PRD。不得因不完整直接遗漏交互或把它静默当完整。
- metadata 与页面疑似不一致，或需要核对文案、按钮、弹窗、关闭/返回、二次确认、反馈和高风险交互时，先定位相关 DOM/脚本片段，必要时再读取完整 HTML。按页面与状态列出所需截图清单，缺失处写「待补充截图：<页面>-<状态>」。
- 从确认原型提取并落入 PRD：页面清单、入口/退出路径、主流程、分支流程、关键状态、页面反馈、引用的 `D-###` 决策、已解决的异常、本期包含/不包含范围。
- 原型中状态为「已确认」的 `D-###` 在 PRD 落正式 `R-###` 并建立映射；状态为「待确认」的 `D-###` 写入 PRD 待确认问题，不生成 `R-###`。
- 不复制原型 HTML/CSS/JS；原型中比散文更精确的决策片段（状态机/页面结构/交互时序）可内联并标「（来自原型 vX.Y）」，裁到决策富集部分。
- 评审工具栏、手机外框、状态切换按钮等评审辅助不属于正式页面设计，不写入 PRD 的 UI 要求。
- 原型中的假数据/假接口/假支付/假广告仅为模拟，不得写成正式技术方案、接口契约或服务端校验规则。
- PRD、确认摘要/决策和确认原型冲突时按共享合同的产品目标权威与冲突格式处理，不静默选择；当前实现、配置和历史 PRD 只用于判断现状与差异，不覆盖已确认目标。
- 原型关键页面、主路径、确认步骤、弹窗结构、核心按钮状态或关键状态变更，须先回原型重新确认，再据此更新 PRD，不绕过确认门直接改 PRD。
- 单次需求、模块级范围一致：原型未覆盖的模块/页面不写入 PRD 本期范围；如需扩展，回到需求理解或原型阶段补齐，不在 PRD 阶段静默扩张。
- HTML 中仍找不到支撑 metadata 的页面、主场景或状态证据时，输出证据缺口并返回 `game-prototype`；不得伪造字段或绕过 PRD 门禁。

## 文档来源信息

所有正式生成的 PRD、产品方案、需求分析、评审报告和校验报告，必须在**文档末尾写一行紧凑生成记录**，不写入第 0 章文档信息，也不另起来源信息块。格式与填写规则以主 `SKILL.md`「文档来源信息」节为唯一权威源，本子 Skill 不复制。评审前预检按文末位置解析该行（见 [../game-prd-review/SKILL.md](../game-prd-review/SKILL.md) 第 0 节）。

第 0 章文档信息只承载需求名称、版本、负责人、状态、复杂度、计划版本、关联原型和 `not_applicable` 豁免记录，不承载生成记录。

## 完成与交接

PRD 初稿写入共享工作目录后，交由编排器更新产物版本和本需求目录的变更记录（若存在），随后按复杂度进入评审。

若作为窄任务独立调用，只输出明确标记的非正式 PRD 草稿与待确认问题，不写正式流程状态。

## 参考

- 上下文加载清单：[../references/context-loading.md](../../references/context-loading.md)「快速执行索引」——「PRD」行是本阶段默认与扩展章节的唯一权威清单，本 Skill 不复制
- 阶段状态与硬门禁：[../references/stage-gates.md](../../references/stage-gates.md)

- PRD 研发执行结构与规则合同：[../references/prd-spec.md](../../references/prd-spec.md)
- 按需图形示例与限制：[../references/prd-diagrams.md](../../references/prd-diagrams.md)（仅图形触发后读取对应章节）
- 配置 CSV 交付物格式与禁止事项：[../references/csv-config-deliverable.md](../../references/csv-config-deliverable.md)
- 交付文件模板：[../references/templates.md](../../references/templates.md)
- 移动游戏专项检查：[../references/mobile-game-checklist.md](../../references/mobile-game-checklist.md)
- 三方对接读取飞书内文档：[../references/feishu-publish.md](../../references/feishu-publish.md) 第 5 节
