# 工作流参考

本文件承载正式需求的启动规则（第 0 节）和阶段总览（第 1–9 节）。各阶段执行细节以对应子 Skill 为唯一权威，本文不复制；跨阶段状态与门禁见 [stage-gates.md](stage-gates.md)，上下文加载见 [context-loading.md](context-loading.md)。

## 目录

1. 需求调研
2. 需求访谈与事实核验
3. 需求摘要
4. 交互原型
5. PRD
6. 多角色评审
7. 评审处理
8. 校验
9. PRD 完成后的独立分支

## 0. 正式需求启动与阶段门禁

正式需求必须由根编排器启动，在独立工作目录创建 `00-stage-state.json`。根编排器是唯一状态写入者；子 Skill 只读并运行 `scripts/check-stage-gate.py`。状态结构与枚举以 [stage-state.schema.json](stage-state.schema.json) 为权威，完整门禁矩阵、原型豁免、窄任务边界和输出合同见 [stage-gates.md](stage-gates.md)。跨阶段材料按 [context-loading.md](context-loading.md) 渐进加载：默认当前版本和证据索引，证据不足、冲突、高风险或不确定时自动扩大读取。

启动时协调 Agent 推荐需求模式和复杂度，并可给出原型适用性初步建议；完成调研和需求理解确认后再正式写入原型适用性，产品负责人可以调整。复杂度对访谈、原型、评审与完成后分支的具体重量以 [stage-gates.md](stage-gates.md) 第 7 节「复杂度路由」为唯一权威，本文不复制。

目标游戏项目未另定目录规范时，工作目录默认：`history/<日期>-<需求简称>/`。用户询问“怎么开始”“怎么继续”时，优先指向项目内 `docs/mobile-game-product-forge/operation-guide.md`；不存在时使用已安装 Skill 的 `operation-guide.md` 并提示运行 setup。

### 0.1 创建工作目录前先确认落点

创建任何文件前必须先确认落点，不得静默在当前工作目录建 `history/`：

1. 检测目标项目是否已初始化：存在 `knowledge/INDEX.md` 或既有 `history/<日期>-<需求简称>/` 即视为已初始化，按既有目录规范继续，不再追问。
2. 未初始化时，先说明「将在 `<绝对路径>/history/<日期>-<需求简称>/` 建立工作目录」，并提示可改为先运行 `$setup-mobile-game-product-forge` 完成初始化（含 `docs/prd/`、操作指南、交付策略和知识包）；**等产品负责人确认落点后才创建任何文件**。
3. 落点确认不是新的产品确认门：不写入 `00-stage-state.json`，不改变复杂度、阶段顺序或既有确认门数量。用户已在本轮明确给出目标目录时视为已确认，不重复追问。

### 0.2 恢复类请求必须消歧到唯一需求目录

「继续上次的需求」「继续商城那个」这类指代型请求，先扫 `history/*/00-stage-state.json` 形成候选集，再按候选数处理：

| 候选数 | 处理 |
|---|---|
| 0 | 视为新需求，按 0.1 确认落点后启动 |
| 1 | 直接继续该需求，汇报需求简称、当前阶段和下一步 |
| ≥2 | 必须列出全部候选（需求简称 + 日期 + `requirement.currentStage`）请产品负责人点选；等待选择后才读写任何状态 |

禁止按目录最近修改时间、目录排序或名称相似度自行猜选，也不得先写入再纠正——写错需求目录的状态没有回滚。用户的指代同时命中多个模块名（如两个商城相关需求）时按 ≥2 处理，即使其中一个明显更近。

### 0.3 存量或外部 PRD 走窄任务接入，不发状态源

用户拿来一份既有 PRD（存量需求、他人产出、外部文档）只要求评审或校验时，走窄任务接入，不进正式流程：

- **不创建 `00-stage-state.json`，不写任何阶段状态**，不推 `review` / `validation` / `prd` / `delivery` 任何字段（窄任务边界见 [stage-gates.md](stage-gates.md) 第 1 节）。
- 不因缺少调研产物、需求摘要或确认原型而要求用户补齐整条正式流程；缺失的前置只在报告里写明未执行的门禁与由此降低的覆盖（如无确认原型则跳过保真轴）。
- 输出两份独立产物：评审报告和按严重度排序的修改清单。不改写用户 PRD 原文，除非用户明确要求代改；产物必须标记 `narrow_task`，不得称为「终稿」或「已通过校验」。
- 用户随后要求把它转为正式需求时，才由根编排器新建工作目录和状态源，并从需求调研阶段补齐证据；不得把窄任务报告直接当作正式评审记录。

## 1. 需求调研

通过用户访谈、项目知识、当前实现核验、历史证据、数据与用户反馈、必要外部调研六类来源建立可信现状，识别冲突、未知项和风险。所有正式需求都必须完成本阶段并输出 `00-research-findings.md`（结构见 [templates.md](templates.md)「需求调研结论」；历史需求兼容旧 `00-project-context.md`）。完成后由协调 Agent 写入 `projectContext.status=completed`、调研文件相对路径和非空版本，再发起需求理解确认；该状态更新不是新的用户确认门。

六类来源、模式1 现状飞书文档读取与 L1/L2/L3 调研深度以 [../skills/game-requirement-discovery/SKILL.md](../skills/game-requirement-discovery/SKILL.md) 与 [context-loading.md](context-loading.md)「需求调研来源与现状核验」「L1/L2/L3 调研深度」为唯一权威。

## 2. 需求访谈

按 13 主题的决策依赖顺序推进，每轮询问 1–3 个会改变方案的问题，并维护决策、术语两本 inline 账本。轮次预算、主题裁剪、逼问手段、术语澄清、长期决策过滤与收敛许可以 [../skills/game-requirement-discovery/SKILL.md](../skills/game-requirement-discovery/SKILL.md) 为唯一权威。

调研完成与阶段交接（`context-snapshot.md` 的生成时机、冻结与复用）见 [context-loading.md](context-loading.md)「context-snapshot 定位与冻结」。

## 3. 需求摘要

访谈收敛后输出《需求理解与方案摘要》（`01-requirement-summary.md`）：16 项骨架的独立可过目文档，关键决策点附推荐方案、备选与影响，不套 PRD 章节躯壳、不提前编 `R-###`/`AC-###`。它是需求理解确认门的确认对象。摘要结构、术语表与已确认决策的呈现规则以 [../skills/game-requirement-discovery/SKILL.md](../skills/game-requirement-discovery/SKILL.md) 第 3 节为唯一权威。

## 4. 交互原型

需求摘要确认后正式判断原型适用性：有新页面、入口、主路径、按钮、弹窗、状态反馈或交互变化必须 `required`；无 UI/交互变化可由产品负责人明确确认 `not_applicable + waived`。适用性建议和豁免确认可与需求摘要同轮呈现，但状态顺序仍是先完成调研、再确认摘要、再落原型分支；豁免路径不调用 `game-prototype`。需要原型时，进入前执行 `check-stage-gate.py --target prototype`，未通过只输出 `BLOCKED`。

原型生成规则、评审工具栏、`D-###` 标注、内嵌 metadata 合同、迭代与确认门以 [../skills/game-prototype/SKILL.md](../skills/game-prototype/SKILL.md) 为唯一权威；适用性判定与豁免证据合同见 [stage-gates.md](stage-gates.md) 第 3 节。

## 5. PRD

进入 PRD 前执行 `check-stage-gate.py --target prd`：先校验调研完成证据与确认摘要，随后 required 路径要求原型 metadata `COMPLETE` 且版本一致，not_applicable 路径只校验豁免证据。PRD 以确认摘要、确认决策和确认原型/豁免为强制输入，初稿版本 `v0.1`，按 [prd-spec.md](prd-spec.md) 统一 7 章研发执行结构写作。

强制输入、冲突处理、原型到 PRD 交接、图形选择与截图清单以 [../skills/game-prd-writing/SKILL.md](../skills/game-prd-writing/SKILL.md) 为唯一权威。涉及埋点时按 [prd-spec.md](prd-spec.md)「埋点和指标」产出 12 列事件明细表；需深化埋点/指标方案时由编排器委派 `game-analytics-design`，产出以同一骨架并入本章。

## 6. 多角色评审

进入评审前执行 `check-stage-gate.py --target review`；并行评审前先做结构可解析性预检，失败一次性报告并停，不 fan-out。按复杂度和风险启用学科角色与标准、保真、攻击三条横切轴；所有角色使用同一冻结快照、公共业务核心和当前 PRD 版本，输出头记录 `reviewRole`、`snapshotVersion`、`prdVersion`、`prototypeVersion`、`reviewedAt` 五个版本追踪字段，风险按 P0/P1/P2 分级。

角色清单、预检项、横切三轴、每角色预算与并行合同以 [../skills/game-prd-review/SKILL.md](../skills/game-prd-review/SKILL.md) 为唯一权威；共享核心与角色切片见 [context-loading.md](context-loading.md)「多角色共享核心与专业增量」「角色切片、版本一致性与冲突汇总」。

## 7. 评审处理

协调 Agent 合并重复问题与角色分歧后统一修订：格式/编号错误、前后冲突和已有内容缺口可直接修订；命中重大争议事项（商业化规则、需求范围、核心规则或主流程、重大技术方案、多方案均合理、交互变化）不得由 Agent 决定，唯一判定、裁定后返回原型与状态迁移见 [stage-gates.md](stage-gates.md)「评审通过与重大争议的唯一判定」。

P0 反驳验证、需要重冻需求摘要的情形与每次规则修改的逐项同步检查以 [../skills/game-prd-review/SKILL.md](../skills/game-prd-review/SKILL.md) 第 2 节为唯一权威。

## 8. 校验

进入校验前执行 `check-stage-gate.py --target validation`；门禁未通过返回评审处理。检查格式、完整性、一致性与移动游戏专项四类问题，结论只允许：`通过`、`有条件通过`、`不通过`；完成条件按 [stage-gates.md](stage-gates.md)「正式 PRD 流程完成的唯一判定」执行，本节不复述。

四类检查细节与 `lint-prd.py` 格式校验调用以 [../skills/game-prd-review/SKILL.md](../skills/game-prd-review/SKILL.md) 第 3 节为唯一权威。

## 9. PRD 完成后的独立分支

知识维护提案和项目交付是两个独立分支，没有固定先后顺序，也不互相作为前置条件。

- **知识维护提案**：L1 默认不生成，L2 按长期价值决定，L3 必须评估（结论可以是不需要）；只输出提案，不直接写入知识库。提案格式与归档规则以 [../skills/game-knowledge-maintenance-proposal/SKILL.md](../skills/game-knowledge-maintenance-proposal/SKILL.md) 与 [project-knowledge.md](project-knowledge.md) 第 5 节为唯一权威。
- **项目交付**：仅 `delivery.required=true` 或用户明确要求“只发布”时调用 `game-prd-publish`，发布前执行 `check-stage-gate.py --target publish`（`required=false` 返回 `NOT_REQUIRED`）；成功写 `delivery.status=published`，失败写 `delivery.status=failed`，不回退 `prd.status=final`。绑定探测、发布命令与交付记录以 [../skills/game-prd-publish/SKILL.md](../skills/game-prd-publish/SKILL.md) 与 [feishu-publish.md](feishu-publish.md) 为唯一权威。
