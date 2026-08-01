# Changelog

All notable changes to `mobile-game-product-forge`. The single version source is `package.json`; every other version field must match it and is checked by `scripts/validate.sh`.

## [3.4.0] - 2026-07-30

### Added

- 新增 `references/csv-config-deliverable.md`：定义 PRD 涉及配置表时必须同步产出的三类交付物——`csv/<table_name>.csv` 原始配置表、`字段说明/<table_name>.csv 字段说明文档`、`csv-config-guide.md` 配置总览。CSV 表头固定 4 行（中文字段名、翻译标记 0/1、PascalCase 英文字段名、字段类型），第 5 行起为演示数据。
- `references/templates.md` 工作目录新增 `csv/`、`字段说明/`、`csv-config-guide.md`；新增「9a. 配置 CSV 说明模板」。
- `references/prd-spec.md`「配置」章节要求 PRD 涉及配置表时同步产出上述三类配置交付物，并引用 `csv-config-deliverable.md`。
- `skills/game-prd-writing/SKILL.md` 新增「配置 CSV 交付物」环节：写 PRD 配置章节前必须先产出/更新 CSV、字段说明和配置总览，作为配置章节的共同前置。

### Changed

- `README.md` 与 `AGENTS.md` 的 references 清单登记 `csv-config-deliverable.md`。

## [3.3.0] - 2026-07-27

### Added

- 新增 `scripts/lint-review-report.py`：把「合并前所有评审角色版本头一致」从模型自觉下沉为脚本判定——校验 `04-review-report.md` 各角色段五个版本追踪字段齐全非空、`snapshotVersion`/`prdVersion` 全体一致、required 路径 `prototypeVersion` 一致（waived/窄任务特例值不计入实版本比对）。`game-prd-review`「评审状态收口」要求退出码 0 才允许写 `review.status=passed`；`validate.sh` 增加 py_compile + `--self-test`。
- 阶段门禁新增终稿同步核验：状态 `prd` 对象新增可选字段 `syncedTo`（记录 `docs/prd/<需求简称>.md` 或项目既有正式 PRD 目录的同步位置）。`--target final` 与 `prd.status=final` 的跨字段一致性均要求 `prd.syncedTo` 非空且文件真实存在，把「正式 PRD 流程完成的唯一判定」第 3 条从模型职责变为机器核验；selftest 新增 6 例。**兼容性**：已有 `prd.status=final` 的历史需求重跑 final/publish/delivery 门禁会 `INVALID_STATE`/`BLOCKED`，在状态中补写 `prd.syncedTo` 指向真实同步文件即可；不重跑门禁的历史需求不受影响。

### Changed

- 消灭 `references/workflow.md` 影子编排层：第 1–9 节与各子 Skill 逐字重复的访谈主题、摘要骨架、评审角色清单、强制输入块等压缩为「阶段摘要 + 指向唯一权威的指针」，第 0 节启动规则原样保留；根 `SKILL.md`「开始前」新增第一步显式链接 workflow 第 0 节（此前落点确认/恢复消歧/窄任务接入三条编排级规则不在编排器任何默认读取路径上）；删除 7 个子 Skill 指向 workflow 的循环"细节"背链（`game-prd-writing` 预检引用改指 `game-prd-review` 第 0 节）。
- 根 `SKILL.md` 瘦身回纯编排：「访谈规则」「原型规则」「PRD 与评审」压缩为编排级要点 + 指向对应子 Skill；重大评审争议六项清单收敛为一行枚举，逐项定义以 `stage-gates.md`「评审通过与重大争议的唯一判定」为唯一权威；`game-prd-review` 文内两份争议清单去重为一份（「评审争议确认门」节，补回「含次数维度」）。

- Claude Code 插件化分发：新增 `.claude-plugin/marketplace.json`（同仓自托 marketplace `fairyland-forge`，插件条目相对路径指向本仓、刻意不写 version 使版本解析统一落到 `plugin.json`）；`plugin.json` 补 `homepage`/`repository`（Gitee）。安装两条命令：`claude plugin marketplace add git@gitee.com:xianlan---shanghai-g/mobile-game-product-forge.git` + `claude plugin install mobile-game-product-forge@fairyland-forge`；私有仓后台自动刷新要求 SSH 形式 URL。`validate.sh` 新增 #5b 断言 marketplace 自托条目结构与"不写 version"。
- `MGPF` 运行时定位链升级为四级并加悬空链防护：`MOBILE_GAME_PRODUCT_FORGE` → `CLAUDE_PLUGIN_ROOT` → `~/.claude|.codex/skills/` → 插件缓存 `~/.claude/plugins/cache/*/mobile-game-product-forge/<版本>/`，候选须真实含 `scripts/check-stage-gate.py` 才采用（`ls -d` 会命中悬空软链，实测踩到）。同步 `references/stage-gates.md`、`skills/game-prd-review/SKILL.md`、`AGENTS.md` 样板与 `lint-prd.py` docstring（docstring 改为指向权威片段不再复制）。
- 新增 `install-guide.md`《安装与升级指南》（面向 PM：SSH 一次性配置、两条命令安装、自动升级说明、故障排查表）；`operation-guide.md` 收敛为纯日常操作并指向该指南；两份 install-profiles 登记该文件。
- 新增 `scripts/release.sh` 标准发版入口（同步 `package.json`/`plugin.json`/根 `SKILL.md` 三处版本 + 断言 CHANGELOG 条目已转正 + validate.sh 全量 + `claude plugin validate .`）；AGENTS §13 固化「发版 = bump 版本，只推 commit 已安装用户不会升级」。
- 新增 `scripts/githooks/pre-push` 推送门禁（validate.sh + install.sh 语法与临时目录冒烟 + plugin validate），`git config core.hooksPath scripts/githooks` 启用；替代在 Gitee 上不生效的 GitHub Actions（`.github/workflows/validate.yml` 已删除，README/AGENTS 引用同步改写）。
- 知识包安装回执 `installed_from:` 由绝对路径改为稳定来源标识（`plugin:<名>@<版本>` / `repo:<路径>`），避免插件缓存版本目录在升级后变成死路径；`install.sh` 与 `install.ps1` 对称实现。

- 路由回归夹具扩到 24 条并新增 `style` 字段（`textbook` / `colloquial` / `mixed_language` / `explicit_invocation`）：补 3 条口语省略式、1 条中英混合、1 条真歧义指代（`ambiguous_reference`，期望是请产品负责人点选而不是路由）。`validate-regression-fixtures.py` 断言各风格下限与歧义类期望，并打印非 textbook 占比与 1/3 目标；`docs/capability-regression.md` 新增「路由夹具的输入风格约定」。

### Fixed

- 修复三处标题类断言的子串误匹配：`grep -F '## X'` 会被 `### X` 满足，标题被降级或改写时断言仍变绿。`validate.sh` 的 context-loading 章节检查、`workflow.md` 第 0 节三条前置规则检查、README 升级小节检查统一改用 `grep -qxF`（整行匹配）。
- `validate.sh` 中 13 处以变量为模式的 `grep` 统一加 `-e`，避免取值以 `-` 开头时被当作选项（`--agent all --force` 已踩过一次）。

- `README.md` 新增「升级」小节：明确优先 git 拉取、ZIP 只作兜底（覆盖解压不删除新版已移除的文件，是版本碎片化主因），给出 ZIP 换目录 + `--force` 改指向的命令序列、用户数据边界（`knowledge/` / `history/` / `docs/prd/` 都在目标项目，安装脚本从不删除）、知识包三态合并回执口径，以及升级后三步自检。
- `install-profiles/*.yaml` 顶部标注「校验清单，不驱动安装」，README 安装小节同步说明：安装范围由整包软链决定，`--profile` 只决定是否安装知识包，两份 YAML 仅由 `scripts/validate.sh` 消费。`validate.sh #20` 双向锁定：声明缺失会失败，`install.sh` / `install.ps1` 一旦开始读取 `install-profiles/` 也会失败并要求同步改声明。

- `references/stage-gates.md` 新增「正式 PRD 流程完成的唯一判定」：`validation.status=passed`、`07-prd-final.md` 已冻结、终稿已同步 `docs/prd/` 三条必要条件缺一不可；`SKILL.md`、`references/workflow.md`、`references/templates.md` 三处改为引用该节，不再各自复述条件。
- `references/context-loading.md`「快速执行索引」增加「触发时扩展读取」列，并声明本表是各阶段加载清单的唯一权威源；根编排器与四个阶段子 Skill 改为指向对应行，不再复制章节清单。
- `references/templates.md` 上下文快照模板第 4/5 章补齐表头骨架（已确认决策、待确认项与阻塞项），字段与决策账本对齐，便于后续机器校验。
- 路由回归夹具新增 `ROUTE-019`（`setup_guarded`）：自然语言初始化请求期望根编排器提示用户显式调用 setup，而不是静默代办；新增执行模式 `user_action_required` 与 `expectedBehavior` 字段。
- `scripts/validate.sh` 新增五条断言：#15 生成记录唯一位置（文末紧凑生成记录，禁止回到文档信息区）；#16 跨文件「第 N 节」引用必须命中真实 `## N.` 标题；#17 上下文加载清单只能指向「快速执行索引」，不得在子 Skill 内复制；#18 正式启动三条前置规则必须在 `workflow.md` 第 0 节成文；#19 截图占位符按有条件通过且发布门硬拦。
- `references/workflow.md` 第 0 节新增三条正式启动前置规则：0.1 创建工作目录前先确认落点（检测 `knowledge/INDEX.md` 或既有 `history/`，未初始化时说明绝对路径并等确认，不静默建目录）；0.2 恢复类请求必须先扫 `history/*/00-stage-state.json` 形成候选集，多候选时列出「简称 + 日期 + 当前阶段」由产品负责人点选，禁止按最近修改时间猜选；0.3 存量或外部 PRD 走窄任务接入，不创建 `00-stage-state.json`、不写任何阶段状态，只输出评审报告与修改清单。
- `scripts/lint-prd.py` 新增第 6 类校验「占位符」：逐条列出「待补充截图：<页面>-<状态>」，结论降为「有条件通过（存在 N 处待补充截图，交付前须确认）」，退出码仍为 0（缺图不阻塞研发理解）。新增 `fixtures/placeholder-prd.md` 回归夹具。
- `game-prd-publish` 前置条件新增第 3 条：终稿仍有「待补充截图」时停止发布，逐条列出页面-状态，须补图或由产品负责人显式确认「按现状发布」并写入交付记录；占位符只拦交付，不改 `prd.status=final` 与校验结论。

### Fixed

- `game-prd-writing` 曾要求把来源信息写入「文档信息区」，与主 `SKILL.md`「文末一行紧凑生成记录」和评审前预检的解析位置冲突，会导致预检判不可解析或产出双份来源信息。
- `game-prd-publish` 指向 `references/workflow.md` 第 10 节，该文件只到第 9 节；改为第 9 节（交付在 9.2）。
- `ROUTE-018` 曾期望自然语言触发 `setup-mobile-game-product-forge`，与该 Skill `disable-model-invocation: true` 的架构不变量冲突；改为显式调用形式，并由 `scripts/validate-regression-fixtures.py` 断言 `setup` 类用例必须是显式调用、`setup_guarded` 用例必须保留。

## [3.2.0] - 2026-07-26

### Added

- 新增独立 `references/prd-diagrams.md`：定义用户业务流程图、页面流转图、客户端—服务端时序图、状态机图、模块关系图和数据流图的触发条件、示例与限制；只在图形触发后读取对应章节，避免主 PRD 规范常驻过长。
- 新增 ADR-0010 与实施计划，记录研发执行型 PRD 结构及历史兼容决策。

### Changed

- PRD 从默认 20 章改为统一 7 章研发执行结构：功能说明、总体流程、功能规则、页面和交互（按需）、接口/数据/配置（按需）、异常和边界、验收标准。L1/L2/L3 共用结构，只调整深度与条件专项，不再维护章节裁剪决定。
- “需求目标”收敛为简短“实现目标”；只有增长、商业化、实验等需求才要求指标与成功判断。
- 多模块需求默认只在“涉及模块”表记录影响范围，正文按统一流程和 `R-###` 组织；禁止按客户端、服务端、数据库、配置或埋点拆功能章节，仅独立业务闭环可在规则章内有限分组。
- 删除运营后台 PRD 章节，运营控制统一通过配置表描述字段、默认值、读取方、生效方式、错误配置、兼容和回滚。
- `lint-prd.py` 支持规则表/验收表中的 `R-###` / `AC-###`，校验新结构并兼容历史 20 章 PRD；fixtures 同步到新结构。
- 复制安装档案补充 `scripts/lint-prd.py`，确保非整仓软链安装也能执行 PRD 格式校验。
- 正式文档来源信息改为文末一行紧凑生成记录，减少研发正文噪音。

## [3.1.0] - 2026-07-26

### Added

- 新增 18 条自然语言路由回归夹具、8 类真实能力回归场景、零依赖结构校验脚本与人工质量回归记录协议，覆盖 L1/L2/L3、原型双路径、冲突处理、历史原型和窄任务。

- Life Reboots 知识包新增 `ui/` 模块，收录 6 张用户确认的按钮、弹窗、表单、列表、属性条与关闭按钮参考图，并提炼为单文件 HTML 原型可执行的视觉、组件、状态、无障碍和移动端适配规范。
- 新增 `references/context-loading.md` 作为唯一共享上下文加载合同，定义权威来源、三层渐进加载、证据索引快照、当前版本优先、历史按需、metadata/HTML 降级、高风险深读、多角色公共核心与专业增量、软预算和轻量回归场景。
- `check-stage-gate.py` 新增 `--extract-prototype-meta` 标准库入口，只输出紧凑 JSON metadata；缺失或非法 metadata 返回非零，不把 HTML/CSS/JavaScript 带入模型上下文。
- 新需求增加自动维护的 `00-research-findings.md` 调研产物，覆盖用户、项目知识、当前实现、历史、数据/反馈和外部官方证据；旧 `00-project-context.md` 保持兼容。

### Changed

- Claude 插件清单改为 `skills: ["./"]` 显式注册根编排器，并依赖默认 `skills/` 扫描 8 个子 Skill；同步 ADR、维护校验和安装说明，避免插件模式只发现子 Skill。
- 收紧根编排器与子 Skill 的自然语言路由边界：新需求、正式需求、历史正式需求续作及未限定阶段的宽泛请求默认进入根编排器；子 Skill 仅接受编排器委派或用户明确的单阶段窄任务。
- 外部证据从笼统“最新官方资料”改为适用性匹配：政策按目标地区、渠道和发布日期，SDK/API 按当前接入或已确认目标版本，升级任务同时核查源版本、目标版本和官方迁移指南。
- 正式 `review / validation / final / publish / delivery` 门禁继承调研、需求摘要以及原型确认或正式豁免的共同前置；`narrow_task` 保持不创建正式状态的独立路径。
- 阶段门禁拆分为 CLI、阶段核心、prototype metadata 校验和自测模块，保持命令兼容并降低单文件维护成本。
- Life Reboots UI 参考图改用 WebP，在保留透明通道和可读性的前提下降低知识包体积。
- Life Reboots 知识包版本 `1.2.0` → `1.3.0`；项目总索引新增 UI 入口，生成或迭代原型时按需读取项目视觉规范和相关参考图，但生成的 `index.html` 保持自包含。
- 根编排器和需求发现、原型、PRD 写作、PRD 评审改为证据驱动加载：默认当前状态、当前快照和当前产物，证据不足/冲突/高风险时自动扩大原文；PRD 不再默认读取完整 HTML，多角色复用冻结公共核心与专业增量。
- `context-snapshot.md` 升级为协调 Agent 自动维护的“阶段摘要 + 来源版本 + 证据索引”，支持按决策、原型、PRD 或知识来源变化增量更新；快照不是状态源、权威源或新确认门。
- 权威来源拆为产品目标、当前现状和外部约束三类；明确当前状态、目标状态及改动，不再用同一线性顺序静默裁决不同性质的证据。
- `prototype-meta` 增加 COMPLETE/INCOMPLETE/INVALID 分类、最小字段/类型/页面场景状态/`D-###` 完整性检查和 HTML 自动降级；多角色报告记录并校验 snapshot/PRD/prototype 版本，过期角色只重审受影响部分。
- 收敛评审通过语义：无重大争议且评审证据完整时由协调 Agent 直接通过并汇报摘要；实际出现重大争议才写 `disputed` 并请求产品负责人裁定，交互变化仍须返回原型确认后重审受影响部分。
- L1 明确为 1–2 个直接专业角色加协调 Agent 轻量标准/保真检查，不为横切轴另启 Agent；L2/L3 保留完整横切检查，L3 强化重大风险识别。
- README 增加基于 `git archive` 的可分发 ZIP 指引，仅打包 `HEAD` 已跟踪内容。

### Fixed

- 发布版本由 `3.0.0` 升级为 `3.1.0`，同步 `package.json`、`.claude-plugin/plugin.json` 与根 `SKILL.md` 的唯一版本链；保留三个确认点、阶段状态 Schema、PRD 格式、D/R/AC 和交付解耦。
- 新格式调研产物增加非空与最低结构门禁，旧 `00-project-context.md` 至少要求非空，避免空文件或残缺调研被标记为 `projectContext.status=completed`；Confirmed prototype metadata 同时拒绝「待补充 / 待确认 / TODO / TBD / PLACEHOLDER / 示例」等真实业务字段占位值，保留 `decisions[].status=待确认` 合法枚举。
- 正式需求的 prototype / PRD 门禁现在共同校验 `projectContext.status=completed`、允许的调研文件相对路径、真实文件和非空版本；L1 只能精简调研，不能绕过调研产物，且未新增用户确认门。
- `prototype-meta` COMPLETE 从“字段大致存在”收紧为语义完整：集中校验支持的 Schema、版本/状态/设备枚举、scope 字符串数组、页面/场景/状态/决策内部结构、决策状态和四类重复 ID；Confirmed 原型必须有页面与主场景。
- required 历史最小或无效 metadata 不再直接通过 PRD 门禁，必须定向回读 HTML、补齐并重新分类；not_applicable + waived 路径继续允许无 `index.html`、metadata 和 HTML 回读。
- `check-stage-gate.py` 新增原型、交付、PRD 终稿和评审状态的跨字段一致性校验；矛盾状态统一返回 `INVALID_STATE`（退出码 3），并补充重大争议与所需回归自测。

## [3.0.0] - 2026-07-26

### Added

- 新增 `references/stage-state.schema.json` 和 JSON 1.1 正式需求状态：集中定义必需字段、枚举与 L1/L2/L3 流程策略；新增原型 `required/waived` 双路径、delivery 独立状态和 12 项门禁回归自测。
- 新增 ADR-0009，取代 ADR-0008 的“飞书第四确认门”决策；新增基础 `.gitignore` 清理 macOS、Python 缓存与打包杂项。
- Life Reboots 知识包新增 `modules/`、`config/`、`analytics/reporting.md`、三项产品决策和 `requirements/v1.0.5-current-version.md`，覆盖剧本与核心玩法、商业化、NPC、平台体验、配置能力、用户维度与报表，以及 v1.0.5 飞书需求来源索引。
- `knowledge/INDEX.md` 改为“项目整体背景 + 知识状态 + 模块导航”的唯一总入口；各模块增加独立 `INDEX.md`。

### Changed

- 发布版本由 `2.4.2` 升级为 `3.0.0`，反映阶段状态 JSON 化、PRD/交付拆分及正式子 Skill 路由策略的破坏性变化。
- 正式 PRD 完成收敛为 `prd.status=final + validation.status=passed`；飞书改为 setup 可配置的项目交付策略，失败只更新 `delivery.status=failed`，不回退 PRD。知识维护提案与交付成为终稿后的独立分支。
- 新需求由受限 YAML 迁移为 `00-stage-state.json`；历史 YAML 不强制迁移且保留说明，自制 YAML 解析器已删除。门禁新增结构/枚举/路径/文件/版本、原型 metadata 版本、豁免批准证据、显式 `openP0=0` 和交付条件校验。
- L1/L2/L3 现在同时控制访谈、过程文件、原型判断、PRD 深度、评审角色、知识提案和交付重量；操作指南新增 5 分钟快速开始。`game-prd-writing`、`game-prd-publish` 改为 explicit-only，正式需求自然语言优先路由根编排器。
- Life Reboots 知识包版本 `1.1.0` → `1.2.0`。知识状态统一为“已上线 / 迁移中 / 目标架构 / 规划候选 / 已废弃”；未上线但已确认的需求作为目标架构参与后续新需求的兼容、对齐和迁移成本检查，不再与已上线能力混写。
- `architecture/life-reboots.md` 补充剧本化演进、六个产品支柱、规则与 AI 的权威边界，并显式保留目标市场口径冲突等待复核。
- 修复 README 与旧 CHANGELOG 已声明 Life Reboots 包含模块、配置和需求结构，但知识包实际缺少对应目录/文件的文档—实现漂移。

## [2.4.2] - 2026-07-25

### Added

- 新增 `references/stage-gates.md`、`scripts/check-stage-gate.py` 与 ADR-0007：正式需求使用工作目录 `00-stage-state.yaml` 作为唯一跨阶段状态源；根编排器唯一写入，子 Skill 只读校验；进入原型、PRD、评审、校验、终稿和发布前执行机器门禁，失败只输出 `BLOCKED`。脚本使用 Python 标准库，支持固定 YAML/JSON 状态格式并带自测。
- 新增 `docs/operation-guide.md`，面向产品经理和跨职能协作角色说明首次接入、模式与阶段判断、完整端到端流程、三个确认门、窄任务、多产品经理协作、回退规则和完成检查表；README 增加入口。同时明确目标项目的产物边界：过程材料与冻结快照保留在 `history/<日期>-<需求简称>/`，校验通过的正式终稿同步到 `docs/prd/` 或项目既有正式 PRD 目录。

- `scripts/lint-prd.py`：PRD 格式校验脚本（Python 标准库，无依赖），校验三类可机器判定的格式--配置表结构（表名 `snake_case.csv`、模块「N 个字段」、字段四项、大驼峰命名）、埋点 12 列事件明细表（列顺序、`snake_case` 标识符、数据来源/版本字段）、规则编号 `R-NNN`/验收编号 `AC-NNN` 唯一性与映射；产出 `06-lint-report.md`，退出码反映错误数（0 无错误 / 1 有错误 / 2 找不到 PRD）。
- `game-prd-review` 校验环节接入 `lint-prd.py`：评审完成前自动跑格式校验，报告写入工作目录 `06-lint-report.md`；脚本只覆盖可机器判定的格式，不替代人工对完整性、一致性与移动游戏专项的判断。
- `references/templates.md` 标注 `06-lint-report.md` 由 `scripts/lint-prd.py` 自动产出，无需手写。
- `.agents/adr/`：架构决策记录目录（编号追加式 ADR 0001-0007 + README 索引），只记 why + 备选、不复述可变规则；`AGENTS.md`/`SKILL.md` 决策点内联链接（禁止段、版本规则段、三门段、只读边界段等）。
- `fixtures/valid-prd.md` 与 `fixtures/invalid-prd.md`：`lint-prd.py` 自测夹具（valid 退出 0、invalid 退出 1）；`.github/workflows/validate.yml` 新增 lint 自测步与 install.sh 冒烟步（断言符号链接 + 回执 + 版本正则）。
- `references/prd-spec.md` 新增 §10 PRD smell baseline（7 项 smell）与 §11 实现细节与原型片段（禁游戏码路径/拷贝框架代码；允 API 契约/Mermaid/schema；原型片段标来源版本）；§7 成功指标须引独立基线来源，无则标「待确认基线」并补采集计划。
- `references/templates.md` §4 阶段状态补固定词表状态字段（需求摘要状态/PRD 状态/评审状态/校验状态）；新增 §11 知识维护提案模板（状态词表：待确认/已采纳待写入/已落库/已驳回）；工作目录新增 `09-knowledge-proposals.md`。
- `references/workflow.md` §2 新增「上下文预算与交接」：访谈->原型->PRD 初稿为不中断窗口（mid-interview 不 compact），tripwire 触发 handoff（账本/术语/fog 项写入工作目录），compact 仅阶段间歇。
- `knowledge-packs/life-reboots/knowledge/architecture/current-milestone.md`：从 `life-reboots.md` 拆出的时衰减里程碑5进度数据，标「待复核」+ 复核截止日。
- `scripts/validate.sh` 新增多项不变量校验：子 Skill 路由表 grep（router-can-lie 守卫）、references 覆盖 grep、回执版本不得硬编码、文档来源信息块去重、知识提案格式对齐 reference、两份 install-profiles 技能清单互验、根编排器注册策略、调用策略显式 `policy.allow_implicit_invocation`。
- `scripts/install.sh` 安装回执新增 `files:` manifest（相对路径 + sha256 前 8 位）与升级 provenance 区分（identical / pack 改 / 人工新增 / 人工改）；旧回执无 manifest 时向后兼容逐文件比对。
- SKILL.md 阶段路由表新增「PRD 终稿且通过校验 -> `game-prd-publish`」与「重审已有飞书 PRD」on-ramp 行；独立调用合同新增合并点表（on-ramp 至命名检查点）与消费边界。
- 各子 Skill `agents/openai.yaml` 显式声明 `policy.allow_implicit_invocation`（setup=false，根编排器 + 7 个 model-invoked 子 Skill=true），替换原省略传达。
- `references/prd-spec.md` §3 配置表字段规范：「为空时填写」按字段是否可空二选一——必填字段写「不可为空」、可空字段写 `0`（为空时以 `0` 兜底）；不得留空或写 `null`/`None`/`N/A`/「空值处理规则」等占位，也不以 `1`/`default` 等其他值兜底。模板占位由「空值处理规则」改为 `0`。`scripts/lint-prd.py` 新增提示级校验：「为空时填写」非 `0` 且不含「不可为空/必填/非空」时提示修正，提示不阻断（退出码不变）。
- `references/prd-spec.md` §5 数据来源标注：来源类型同时表示写入方（客户端/服务端/运营配置/用户/统计系统），并要求读取方与写入方不同时在说明列分别写明，把「客户端还是服务端写」的写入职责写成显式规范。
- `scripts/validate.sh` 新增第 14 项 `agents/openai.yaml` 结构校验（零依赖、BSD 兼容）：每份须恰好含顶级父键 `interface:` 与 `policy:`、无其他顶级键；interface 段下 `display_name`/`short_description`/`default_prompt` 三 leaf 非空；policy 段下 `allow_implicit_invocation` 为 `true|false`。容忍 `skills/game-prd-publish/agents/openai.yaml` 的 1 空格缩进瑕疵（最小缩进上的父键即顶层）。CI 经 `validate.sh` 自动覆盖。
- `scripts/doc-impact-check.sh`：在 Agent 改完、进 `AGENTS.md` §10 文档影响人工/Agent 判断之前的脚本化预检层。输入 `git diff` 工作树改动 + 未跟踪文件（或显式路径/`--base <ref>`)；把改动路径映射到 §9 文档同步建议，并自动标注 §10 检查表「`[x]`=是 / `[-]=否 / `[ ]`=待人工判断」；`knowledge-packs/**` 与 `history/**` 触发只读/历史告警。建议输出、非阻断、退出码恒 0、不入 CI。零依赖 bash（grep/awk/case），`[[:space:]]` 不用 `\s`，`${var}` 大括号避免 `$var` 后接全角字符在 macOS bash 3.2 `set -u` 下的变量名泄漏。
- `references/prd-spec.md` §3 配置表与 §7 埋点和指标各新增格式示例：配置表示例以商城商品配置示范表头/模块标题/字段四项与「为空时填写」二选一（必填=不可为空、可空=0）、枚举默认值写在「配置说明」而非兜底为空、`varchar` 限于埋点口径类型不作配置表基础类型；埋点示例以启动/页面曝光/剧情结算事件示范固定 12 列、多属性事件逐行重复事件信息、`snake_case` 标识符与有效事件下线版本留空。示例对齐现规范，与 `lint-prd.py` 校验语义一致。
- `scripts/install.ps1`：Windows 原生安装器（PowerShell 5.1+），镜像 `install.sh` 能力（`-Agent codex|claude|cursor|all`、`-Profile`、`-Target`、`-Force`、`-Unlink`、`$env:CLAUDE_SKILLS_DIR` 等同名覆盖）。软链优先（开发者模式可用时与 mac 行为一致）、失败回退 `Copy-Item`；知识包回执（`files:` manifest + `Get-FileHash` 前 8 位）格式与 `install.sh` 完全一致、跨平台互换；额外把仓库路径写入用户环境变量 `MOBILE_GAME_PRODUCT_FORGE`、`-Unlink` 时清除。
- MGPF 运行时定位片段跨平台化：实际执行点 `skills/game-prd-review/SKILL.md` 与规范性描述（`AGENTS.md`、`README.md`、`scripts/lint-prd.py` docstring）改为双形式--bash 形式（macOS/Linux/Windows Git Bash，`python3`/`python` 经 `command -v` 双探测）与 PowerShell 形式（Windows 原生，`$env:MOBILE_GAME_PRODUCT_FORGE` 优先 + `$env:USERPROFILE\…` 回退、`python` 调用）。`lint-prd.py` 本身已纯标准库跨平台，仅 docstring 用法示例同步。
- `.github/workflows/validate.yml` 新增 `validate-windows` job（`windows-latest`）：Git Bash 跑 `validate.sh` + `install.sh` 语法检查 + `lint-prd.py` 夹具自测（`python3`/`python` 双探测），pwsh 跑 `install.ps1` 冒烟（断言 `SKILL.md` 装入 + 知识包回执 + 版本正则）。与 ubuntu job 并列、互不阻塞，防 Windows 回归。

### Changed

- 版本 `2.4.1` -> `2.4.2`（同步 `package.json` / `.claude-plugin/plugin.json` / `SKILL.md` 版本字段）。
- 飞书发布升为第四道强制确认门（[ADR-0008](.agents/adr/0008-feishu-publish-as-fourth-confirmation-gate.md)）：`prd.status=已发布` 作为流程完成标志，未发布不算完成；机制层早是硬门，本次把叙事层「可选/非确认门」措辞与机制层对齐。`docs/prd/` 本地同步在终稿后、发布前完成（本地权威源），与飞书发布并存不互替。`game-prd-publish` 前置条件与 description 改为第四确认门；窄任务「只发布」仍可独立调用但不冒充完整流程完成。门契约采「只改状态词、不加完成门」方案：`check-stage-gate.py --target publish` 保持「可发布前置」语义，self-test 补 publish PASS/BLOCKED 用例。
- 正式需求启动与恢复流程收紧：必须从 `$mobile-game-product-forge` 启动，创建独立工作目录和 `00-stage-state.yaml`；`game-prototype`、`game-prd-writing`、`game-prd-review`、`game-prd-publish` 在编排模式下执行只读门禁，明确窄任务只能标记 `narrow_task`，不得冒充完整流程终稿。
- `setup-mobile-game-product-forge` 初始化时把 `docs/operation-guide.md` 写入目标项目 `docs/mobile-game-product-forge/operation-guide.md`，差异时不静默覆盖；完成后必须告诉用户指南路径和第一个正式需求的启动方式。根编排器在用户询问“怎么开始/继续”时优先指向项目内指南。
- `game-prototype` 定位收敛为单次需求、模块级的可点击评审产物：默认交付自包含单文件 `02-prototype/index.html`（HTML/CSS/JS 内嵌、浏览器直接打开、无需 npm/服务器/SDK），主流程必须可点击走通、只覆盖实际相关状态；新增轻量评审工具栏（版本/场景/页面/状态切换/重置/标注/范围/待确认问题，仅评审用、不属正式 UI）、本次范围与非范围展示、内嵌结构化原型元数据（`prototype-meta`）、决策编号 `D-###`（带状态：待确认/已确认/已排除/已替代，仅已确认映射 `R-###`）、设备适配与迭代/异常处理规则；明确禁止默认引入组件库/跨模块原型工程/npm/路由/Design Token/状态机框架/真实接口支付广告 SDK/测试与截图脚本/版本目录/长驻服务/改正式游戏代码。
- 原型到 PRD 交接结构化：`game-prd-writing` 新增「原型到 PRD 交接」节、`prd-spec.md` §11 新增交接合同、`workflow.md` §4/§5 同步；PRD 读取确认原型本身（含内嵌元数据）而非仅截图，提取页面/入口退出/主流程/分支/关键状态/页面反馈/`D-###`/已解决异常/范围，仅已确认 `D-###` 映射 `R-###`、待确认 `D-###` 写入 PRD 待确认问题不生成规则，评审工具栏/手机外框/状态切换与假数据/假接口/假支付/假广告不写入 PRD 正式 UI 与技术方案，不复制原型 HTML/CSS/JS。
- 根 `SKILL.md` 原型规则瘦身：保留默认设备/单文件形式/模块级定位/迭代约束/确认门，细节下沉 `skills/game-prototype/SKILL.md`，不再在编排器复制工具栏/元数据/HTML 实现细节；三个确认门、信息优先级、知识库只读边界、工作流阶段顺序不变。
- `templates.md` 工作目录展示 `02-prototype/index.html`、阶段状态补「确认原型文件」字段；`README.md` 与 `game-prototype/agents/openai.yaml` 描述同步为单文件模块级可点击原型（`allow_implicit_invocation` 不变）。未升级版本号（单一版本源 `package.json` 不动），未改 `install-profiles`/`plugin.json` 技能清单与安装脚本。

### Fixed

- 统一 setup 边界：README、AGENTS、setup Skill 和操作指南均明确 setup 不写入项目 `AGENTS.md`、`CLAUDE.md` 或 `.cursor/` 规则；Cursor 项目规则只由用户明确执行安装脚本时生成。
- `game-prototype` 的 `prototype-meta` 示例改为中性空结构，避免 Agent 把 VIP、人员、日期或示例决策复制到其他模块；`agents/openai.yaml` 修正英文提示词语法并把“交接 PRD”收敛为“供后续 PRD 使用”。
- `scripts/lint-prd.py` 顶部说明改为 raw docstring，消除 PowerShell 路径反斜杠触发的 Python `SyntaxWarning`。
- `scripts/doc-impact-check.sh` 修复子 Skill 引用规范时重复拼接 `references/references/...` 的建议路径，并增加 `docs/` 操作文档影响映射。
- 运行时脚本（`lint-prd.py`）从用户项目调用时找不到 `scripts/` 的 cwd 依赖 bug：此前调用写成裸 `python3 scripts/xxx.py`，仅当 cwd=skill 仓库根时生效，Agent 在用户项目（cwd=项目根）时会失败（`can't open file .../scripts/xxx.py`）。所有调用点改用 `MGPF` 定位片段（`MOBILE_GAME_PRODUCT_FORGE` 环境变量 -> `~/.claude/skills/mobile-game-product-forge` -> `~/.codex/skills/mobile-game-product-forge`），不再依赖 cwd。涉及主 `SKILL.md`、`references/workflow.md`、`references/feishu-publish.md`、`skills/game-prd-review`、`skills/game-prd-publish`、`skills/game-prd-writing`、`skills/setup-mobile-game-product-forge`。
- `scripts/install.sh` 回执 pack 版本硬编码 `version: 1.0.0` -> 从 `PACK.md` 读取为 `$pack_ver`（PACK 升版后回执不再写旧版）。
- `AGENTS.md` `mobile-game-checklist.md` 描述错误：原写「合规与防沉迷、版号、评审角色」-> 修正为「移动游戏专项：设备/生命周期/账号玩法/资产/广告/IAP/时间活动/版本灰度」。
- `CHANGELOG.md` [Unreleased] 段顺序（移至 [2.4.1] 之上，符 Keep-a-Changelog）、表头「自 2.4.0 之后」->「自 2.4.1 之后」、Fixed 段删除已删脚本（`render_pdf.py`/`capture_prototype.py`）引用。
- `scripts/doc-impact-check.sh` §10 检查表「用户安装/调用/使用方式」项误用 `&& ... && ...` 致 `touch_install=1` 时同时输出 `[x]` 与 `[-]` 两行；改为 `&& ... || ...` 三元，只输出一行。
- `.github/workflows/validate.yml` 删除未用的 ripgrep 安装步（全仓用 grep，ripgrep 误导依赖）。

### Changed

- `scripts/validate.sh` 新增第 8 项逆向覆盖校验：SKILL.md 引用的 `scripts/*` 必须存在，防止校验门/发布门依赖的脚本被误删。
- 主 `SKILL.md` 的 lint 引用改为指向 `game-prd-review` 校验环节的 `MGPF` 定位说明。
- `README.md` 与 `AGENTS.md` 基于仓库真实内容重写补全：references 补全为 6 文件（原漏列 `feishu-publish.md`）、补 `history/`/`agents/openai.yaml`/`.github/workflows/` 说明、新增脚本表与运行时脚本 `MGPF` 定位机制、新增多智能体规则文件边界段、补全校验详情（含 `npm run validate`、文档漂移检查与脚本存在检查）。
- `scripts/lint-prd.py` 扩展两类校验：structure（复杂度分级声明 + 核心章节存在）与 data_source（页面和交互出现时提示数据来源标注）。
- `game-prd-review` §1 重写为横切双轴（标准轴 + 保真轴）、隔离并行与分歧保留、每角色预算（top 5 或 ≤300 字，P0/P1 豁免）、PRD smell baseline；§0 新增预检（fan-out 前复用 `lint-prd.py` 解析子集，失败即止）；§2 新增评审确认核心规则/主流程/范围变化且使已冻结摘要失效时回 `game-requirement-discovery` 重冻摘要（bump v1.1-Confirmed 或标 v1.0-Superseded）。
- `references/templates.md` §6 评审问题补每角色预算与分段总结 + 分歧记录；§10 交付记录补文档来源信息块权威源说明。
- `references/mobile-game-checklist.md` 补 scope 说明：目标市场法定合规（防沉迷/实名/版号/隐私）随市场而异、不在本清单，须按目标市场单独补检。
- 「文档来源信息」块去重：`game-prd-writing` / `game-prd-publish` 改为指向主 `SKILL.md` 的指针（主 SKILL.md 为唯一权威源）。
- 知识维护提案格式对齐 `references/project-knowledge.md` §5 的 12 字段权威格式（补提案编号/目标知识模块/变更类型/证据/影响范围/建议负责人），加 lazy-create 规则与提案持久化（写入 `09-knowledge-proposals.md` 按状态词追踪，落库由人工回填）。
- `life-reboots.md` 拆分：稳定架构事实（定位/玩法/能力/约束/信息边界/埋点基线）保留，时衰减里程碑进度数据拆至 `current-milestone.md`；`architecture/INDEX.md` 登记两行（有效/待复核）。
- 各子 Skill 前置条件门禁于上游固定词表状态字段（`game-prd-writing` 门禁需求摘要+原型状态、`game-prd-review` 门禁 PRD 状态、`game-prd-publish` 门禁 PRD 终稿+校验通过、`game-prototype` 补摘要版本与决策账本一致性核对）；窄任务补消费边界与最小输入门禁。
- `AGENTS.md` 决策点内联链接 ADR；调用策略段改为所有 skill 显式声明；架构段补 `.agents/adr/` 与根编排器注册策略说明。
- `README.md` 补「参考规范（references/）」表列出全部 6 个 reference 文件。
- `AGENTS.md` 重写为可执行的 AI 维护手册（面向 Claude Code / Codex / Cursor）：从静态仓库说明改为 Agent 操作规范，新增「仓库身份与 Agent 职责」「指令与信息优先级（仓库维护冲突裁决，区别于 `SKILL.md` 的需求层信息优先级）」「架构边界与状态所有权」「修改前强制工作流程」「修改原则」「Skill 开发规范」「新增/删除子 Skill 同步清单」「文档编写规范」「维护文档同步机制（强制）」「文档影响检查表」「文档与实现一致性」「验证矩阵（按改动类型，命令均真实存在）」「版本与发布规则」「多 Agent 协作规则」「禁止事项」「完成定义」。建立强制维护文档同步机制：每次改动须过文档影响检查表，受影响的 `README.md`/`AGENTS.md`/`SKILL.md`/`references/`/`CHANGELOG.md` 等须同步。未改 Skill 功能；`README.md` 经核对与实际一致未改。
- 接入 `scripts/doc-impact-check.sh` 预检：`AGENTS.md` §4「修改前强制工作流程」补第 8 步（改完、进 §10 判断前先跑预检）；§12 验证矩阵补「任意改动（完成前）→ `doc-impact-check.sh`（建议、非阻断）」首行，`agents/openai.yaml` 行由「无独立 YAML linter（建议补充）」改为「`validate.sh` #2b 调用策略 + #14 YAML 结构」，Shell 脚本行补 `doc-impact-check.sh` 语法检查；`README.md` 脚本表补 `scripts/doc-impact-check.sh` 一行。
- `README.md` 使用：清理「## 使用」下空行排版瑕疵；据 `references/workflow.md` §9→§10 权威顺序明确端到端流程末段「知识维护提案（项目背景更新）在前、PRD 发布在后」均为可选收尾阶段、顺序见 `workflow.md`。

## [2.4.1] - 2026-07-25

### Changed

- PRD 发布直发飞书云文档（`lark-cli docs +create`），不再生成本地 PDF。删除 `scripts/render_pdf.py`、`scripts/requirements-pdf.txt`、`references/prd-pdf.css`；`game-prd-publish` 去掉生成本地 PDF 与上传 PDF 到云空间两个步骤，交付记录去掉本地 PDF 路径与云空间链接两行；setup/install 初始化去掉 PDF 依赖与 mermaid/mmdc 渲染提示。
- 流程图改用飞书原生画板能力，不本地渲染。PRD 中的流程/状态/架构图发布到飞书时以原生画板块写入（`<whiteboard type="mermaid/svg/plantuml">`，经 `docs +create`/`docs +update`），复杂或已有画板用配套 `lark-whiteboard` skill（`lark-cli skills read lark-whiteboard`）；`references/feishu-publish.md` 新增「在文档中插入画板/流程图」节并补飞书 CLI 与配套 Skill 总览（[larksuite/cli](https://github.com/larksuite/cli/blob/main/README.zh.md)）。
- 原型截图不再自动截取，改由用户提供。删除 `scripts/capture_prototype.py`、`scripts/requirements-prototype.txt`；写作时按页面+状态列出所需截图清单（如「商城页-默认/loading/失败」）请用户提供，未提供处写「待补充截图：<页面>-<状态>」；`docs +media-insert` 仍用于插入用户提供的截图。
- setup 删除「PRD 增强依赖」整节（PDF-mermaid 与原型截图两项可选依赖已全清）；`install.sh` 删除 PRD 增强依赖提示段。
- 顶层文档（`SKILL.md`/`README.md`/`AGENTS.md`）与 `workflow.md`/`prd-spec.md`/`templates.md`/`feishu-publish.md` 同步：阶段表与窄任务列表去 PDF、脚本表去 `render_pdf.py`/`capture_prototype.py` 及对应依赖清单、运行时脚本罗列精简为 `lint-prd.py`、references 文件数由 7 改为 6。
- 版本 `2.4.0` -> `2.4.1`。

## [2.4.0] - 2026-07-24

### Added

- 模式1（已有模块迭代）需求发现：主动读取该模块现状飞书文档（`lark-cli docs +fetch`）了解背景，不重复且有长期价值的内容按「知识维护提案」归档到知识库新模块 `knowledge/requirements/`（AI 不直接写入知识库）。
- `references/feishu-publish.md` 新增「读取既有飞书文档」节（`docs +fetch`/`+search`）与「嵌入图片到飞书文档」节（`docs +media-insert`，用于嵌入原型截图/流程图）。
- `references/project-knowledge.md` 新增「历史需求归档」节与 `requirements/` 知识模块；样例包 `life-reboots` 增补 `requirements/INDEX.md`。
- PRD 复杂度分级（L1/L2/L3）与章节裁剪：按复杂度决定必含/可选/可省章节，裁剪决定须记录，不再强制全 20 章。
- PRD 增强：复杂流程给 Mermaid 流程图/状态图；关键状态嵌原型截图（`scripts/capture_prototype.py`，Playwright 自动截取 + 用户兜底）；每个数据标来源（数据来源映射）；涉及三方对接（如苹果支付）先调研官方文档写模块并贴来源链接。
- `references/prd-spec.md` 新增「数据来源标注」「三方对接」节；`references/templates.md` 新增「章节裁剪决定」「数据来源映射」「三方对接依据」模板。
- `scripts/render_pdf.py` 增强：检测 mermaid 代码块，装了 `mmdc` 则渲染为图片嵌入 PDF，未装则保留代码块。

### Changed

- 主 Skill 模式1重点检查、PRD 与评审、需求发现子 Skill、工作流补充飞书文档读取、复杂度裁剪、流程图/截图/数据来源/三方对接规则。
- 版本 `2.3.0` -> `2.4.0`。

## [2.3.0] - 2026-07-24

### Added

- `game-prd-publish` 子 Skill：PRD 终稿后发布到飞书云文档（Docx，经 `lark-cli`）并生成本地 PDF（weasyprint），写入交付记录；可独立调用“只发布”或“只出 PDF”。
- `references/feishu-publish.md`：飞书 CLI 安装、授权绑定、发布命令、PDF 依赖与故障排查参考。
- `scripts/render_pdf.py` + `references/prd-pdf.css` + `scripts/requirements-pdf.txt`：PRD markdown 转 PDF（CJK + 表格样式）。
- `setup-mobile-game-product-forge` 新增可选「飞书发布绑定」环节：探测 `lark-cli` 与授权、写非密钥项目配置 `.feishu-publish.json`、支持手动重绑。密钥由 `lark-cli` 存 OS keychain，Skill 不经手。
- `scripts/install.sh` 末尾新增飞书发布首装提醒。
- `references/workflow.md` 新增第 10 阶段「PRD 发布与交付」。

### Changed

- 主 Skill「子 Skill 编排」表与「调用边界」「校验与完成」补充发布环节。
- 版本 `2.2.0` -> `2.3.0`。

## [2.2.0] - 2026-07-24

### Added

- 六个可独立调用的子 Skill：`game-requirement-discovery`、`game-prototype`、`game-prd-writing`、`game-prd-review`、`game-analytics-design`、`game-knowledge-maintenance-proposal`，各自带 `SKILL.md` 与 `agents/openai.yaml`。
- 主 Skill 新增「子 Skill 编排」段，按阶段路由委派并声明调用边界。
- `scripts/install.sh`：跨 Codex / Claude Code / Cursor 的统一安装脚本，支持 `core` 与 `core-life-reboots` 安装档案。
- `.claude-plugin/plugin.json`：Claude Code 插件清单。
- `package.json`：作为唯一版本源的发布清单。
- `scripts/validate.sh`：P1 结构、相对链接、版本一致性、元数据与调用配置校验。
- `.github/workflows/validate.yml`：CI 校验工作流。

### Changed

- 主 Skill 由端到端单 Skill 精简为轻量编排器，阶段执行规则下放到对应子 Skill；确认门、模式判断、信息优先级、多 Agent 协议与校验仍由编排器持有。
- 版本 `2.1.0` -> `2.2.0`。

## [2.1.0] - 2026-07-24

### Added

- 通用 Skill 与项目知识解耦；Life Rebooks 项目资料迁移为可选知识包 `knowledge-packs/life-reboots`。
- `setup-mobile-game-product-forge`：一次性、用户主动触发的项目初始化 Skill，支持 `core` 与 `core + life-reboots`。
- `install-profiles/core.yaml` 与 `install-profiles/core-life-reboots.yaml` 两套安装档案。
- 初始化与知识包升级均不得覆盖项目已有知识；知识包版本写入独立安装回执。
- `scripts/validate-p0-architecture.sh`：P0 架构校验脚本。
