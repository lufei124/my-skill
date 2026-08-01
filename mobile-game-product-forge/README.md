# mobile-game-product-forge

移动游戏产品需求工坊：把游戏想法、已确认原型或现有 PRD 转化为产品、设计、客户端、服务端、测试、数据和运营可执行的需求。先识别当前阶段，只补齐缺失环节，绝不把推断伪装成已确认需求。

当前版本：见 `package.json`（唯一版本源）。变更记录见 `CHANGELOG.md`。

## 包含的 Skill


| Skill                                 | 作用                                       | 调用方式          |
| ------------------------------------- | ---------------------------------------- | ------------- |
| `mobile-game-product-forge`           | 主编排器：模式/复杂度/原型适用性、JSON 状态、三个产品确认点与机器门禁 | 新需求、正式需求和未限定阶段的宽泛请求默认入口 |
| `setup-mobile-game-product-forge`     | 一次性项目初始化，选择知识档案、文档目录并写入操作指南 | 用户主动调用 |
| `game-requirement-discovery`          | 多来源需求调研、现状核验与摘要草稿 | 编排器委派；或明确“只调研/只澄清” |
| `game-prototype`                      | 单次需求、模块级单文件可点击 HTML 原型 | 编排器委派；或明确“只做/迭代原型” |
| `game-prd-writing`                    | 确认原型或正式豁免后生成 PRD | 显式调用 / 编排器委派 |
| `game-prd-review`                     | 多角色评审、争议升级、校验 | 编排器委派；或明确“只评审/只校验已有 PRD” |
| `game-analytics-design`               | 埋点事件、指标、漏斗设计并去重已有基线 | 编排器委派；或明确“只补埋点/指标” |
| `game-knowledge-maintenance-proposal` | 知识维护提案，只输出不写入 | PRD 完成后编排器委派；或明确只做提案 |
| `game-prd-publish`                    | 按项目策略把终稿交付飞书，不改变 PRD 终稿状态 | 显式调用 / 编排器委派 |


主编排器通过每个需求的 `00-stage-state.json` 唯一持有跨阶段状态，结构和枚举由 `references/stage-state.schema.json` 集中定义；子 Skill 只读校验。历史 YAML 不强制迁移，新需求只生成 JSON。

所有正式需求先自动维护 `00-research-findings.md`，记录当前现状、目标状态、实现核验、数据反馈、冲突、未知项、风险和来源；L1 允许精简但不能跳过。新格式调研文件必须非空并保留现状、目标、差异、风险和来源索引等最低结构，旧 `00-project-context.md` 可继续兼容但也不得为空。协调 Agent 记录调研完成状态、文件和版本后再发起需求理解确认。需求摘要与原型确认/豁免后，系统再生成 `context-snapshot.md` 作为具体阶段的摘要和证据索引。这些状态更新都不是新的确认门，用户无需手工维护。

## 安装

前置条件：Python 3（机器门禁与 PRD 校验脚本必需；macOS 可通过 `xcode-select --install` 获得）；Node.js/npx（仅飞书发布需要，可选）。产品经理请直接照 [安装与升级指南](install-guide.md) 操作，本节是概览。

提供两种安装档案：

- `core`：只装通用工作流，不含项目知识。
- `core + life-reboots`：通用工作流加 Life Reboots 项目知识包（知识包由安装后的 setup 或脚本 `--target` 初始化到项目，与安装方式无关）。

### 方式一：Claude Code 插件（推荐）

一次性前置：本机能以 SSH 访问 Gitee 私有仓（配置步骤见 [安装与升级指南](install-guide.md)）。然后两条命令：

```bash
claude plugin marketplace add git@gitee.com:xianlan---shanghai-g/mobile-game-product-forge.git
claude plugin install mobile-game-product-forge@fairyland-forge
```

也可在 Claude Code 会话内用 `/plugin marketplace add …` 与 `/plugin install …` 完成。安装落在 `~/.claude/plugins/cache/`，升级自动进行（见「升级」）。marketplace 清单 `.claude-plugin/marketplace.json` 与插件清单 `plugin.json` 同仓自托：插件条目不写 version，版本解析统一落到 `plugin.json`（`git@` 形式 URL 是有意为之——Gitee 不支持 owner/repo 简写，且私有仓的后台自动刷新只有 SSH 可用）。

### 方式二：安装脚本（Codex / Cursor / 兜底）

macOS / Linux / Windows Git Bash：

```bash
bash scripts/install.sh --agent codex              # 链接到 Codex
bash scripts/install.sh --agent claude             # 链接到 Claude Code
bash scripts/install.sh --agent cursor --target .  # 写入当前项目的 Cursor 规则
bash scripts/install.sh --agent all                # 全部
```

Windows 原生（PowerShell 5.1+，无需 Git Bash）：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent claude
powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent all -Profile core-life-reboots -Target .\my-game
```

脚本默认整包链接（Windows 优先软链、开发者模式不可用时回退复制），保留仓库结构以使子 Skill 的相对引用（`../../references/...`）生效。可选参数：

- `--agent codex|claude|cursor|all` / `-Agent codex|claude|cursor|all`：目标 Agent（默认 `codex`）。
- `--profile core|core-life-reboots` / `-Profile …`：配合 `--target`/`-Target` 时一并初始化项目知识包（默认 `core`）。
- `--target <项目目录>` / `-Target <dir>`：把知识包安装到目标项目（不覆盖已有文件，冲突只报告）。
- `--force` / `-Force`：替换已存在的安装。`--unlink` / `-Unlink`：移除安装。

`install-profiles/*.yaml` 是**校验清单，不是安装配置**：安装脚本不解析它们，安装范围由整包软链决定，`--profile` / `-Profile` 只决定是否安装知识包。两份 YAML 里的 `skills` / `source_files` 由 `scripts/validate.sh` 消费，用于防止子 Skill 漏登记或路径写错——改它们不会改变任何安装行为。

`codex` / `claude` 把整个仓库链接（或 Windows 复制）到 `~/.codex/skills/` 或 `~/.claude/skills/`；`cursor` 在目标项目写 `.cursor/rules/mobile-game-product-forge.mdc` 规则文件。`install.ps1` 额外把仓库路径写入用户环境变量 `MOBILE_GAME_PRODUCT_FORGE`，使运行时定位片段开箱可用；`-Unlink` 时清除该变量。

### 安装后：项目初始化

在目标游戏项目里调用 `$setup-mobile-game-product-forge`，探测项目后选择档案，建立 `docs/prd/` 与 `history/`，写入操作指南，选择飞书是否为强制项目交付策略，并按需初始化知识包。setup 不写入或修改项目的 `AGENTS.md`、`CLAUDE.md`、`.cursor/` 等 Agent 规则文件。

## 升级

### 插件安装（推荐轨）

维护者推送并 bump 版本后，同事侧 Claude Code 启动时后台刷新 marketplace 并自动升级到新版（私有仓要求 marketplace 以 `git@` SSH 形式添加，HTTPS 后台刷新会因凭据助手被禁而失败）。手动触发：`claude plugin update mobile-game-product-forge@fairyland-forge` 或会话内 `/plugin`，更新后重启会话生效。**不 bump `plugin.json` 版本的推送对已安装用户不可见**——发版必须走 `scripts/release.sh`。

插件升级覆盖的是 `~/.claude/plugins/cache/` 下的版本化目录，不会触碰你项目里的任何东西（见「用户数据边界」）。

### 脚本安装（git 轨）

`--agent codex|claude` 把整个仓库软链到 `~/.codex/skills/` 或 `~/.claude/skills/`，仓库本身就是安装源：

```bash
cd <仓库目录>
git pull                      # 升级完成，无需重跑 install.sh
bash scripts/validate.sh      # 自检
```

只有仓库目录被移动、或软链被删时才需要 `bash scripts/install.sh --agent all --force` 重新指向。Claude Code 插件环境升级后运行 `/reload-plugins`。

### ZIP 分发

解压到新目录再改指向，不要覆盖旧目录：

```bash
unzip mobile-game-product-forge-<版本>.zip -d <新目录>
bash <新目录>/scripts/install.sh --agent all --force   # 软链改指新目录
bash <新目录>/scripts/validate.sh
rm -rf <旧目录>                                        # 确认新版可用后再删
```

### 用户数据边界

升级只动 skill 仓库，不动目标游戏项目：`knowledge/`、`history/`、`docs/prd/` 都在你的项目里，安装脚本从不删除它们（`--unlink` / `-Unlink` 只移除软链和 Cursor 规则，明确保留项目知识）。

知识包升级是唯一会写入目标项目的动作，按 `<项目>/knowledge/.installed-packs/<包名>.md` 回执做三态合并：

```bash
bash scripts/install.sh --agent claude --profile core-life-reboots --target <项目目录>
# knowledge: created=新增 identical=未变 pack_updated=你没改过、随包升级 conflicts=你改过、原样保留
```

`conflicts` 不为 0 表示这些文件你改过：脚本保留你的版本、不覆盖，需要人工合并后再决定是否采纳新版内容。

### 升级后自检

1. `bash scripts/validate.sh` 全绿（需要 Python 3）。
2. 版本对齐：`package.json`、`.claude-plugin/plugin.json` 与根 `SKILL.md`「当前 Skill 版本」三者一致（`validate.sh` 已断言，不需手工比对）。
3. 团队口径核对：正式文档文末的紧凑生成记录带版本号，用它确认协作方跑在同一版本上。

## 使用

完整的角色分工、阶段状态、机器门禁、确认方式、窄任务和多人协作说明见 [操作指南](operation-guide.md)。初始化后，项目内副本位于 `docs/mobile-game-product-forge/operation-guide.md`；用户询问“怎么开始/继续”时，Agent 应优先指向该文件。

### 开始一个正式需求

不要直接调用 `$game-prd-writing`。在目标项目根目录使用根编排器：

```text
使用 $mobile-game-product-forge 开始一个正式需求。
需求名称：【填写】
初始想法：【填写】
已有材料：【可选】
负责人：【填写】
```

### 端到端流程

主编排器先完成需求调研，再推进：需求理解确认 → 判断原型适用性 → required 原型确认或 not_applicable 产品负责人豁免 → PRD → 按复杂度动态评审 →（仅实际存在重大争议时）产品负责人确认 → 校验终稿。所有正式需求都必须调研，但只有 UI/交互变化才强制原型；无重大争议时协调 Agent 汇报评审摘要后直接通过，`prd.status=final` 且校验通过即完成正式 PRD。

完成后，知识维护提案与按项目策略发布飞书是两个独立分支，不互相作为前置。飞书未启用或发布失败都不回退 PRD。

## PRD 研发执行结构

新 PRD 默认使用统一 7 章：功能说明、总体流程、功能规则、页面和交互（按需）、接口/数据/配置（按需）、异常和边界、验收标准。L1/L2/L3 使用同一结构，只调整深度和条件触发专项，不再维护 20 章清单和章节裁剪决定。

“实现目标”只说明功能需要达成什么结果；增长、商业化或实验类需求才补指标。多模块先用“涉及模块”表记录影响范围，正文继续按统一流程和 `R-###` 规则组织，不按客户端、服务端、数据库、配置或埋点拆章。只有形成独立业务闭环时，才在规则章节内按业务能力有限分组。

项目没有运营后台，所有运营控制统一写配置表。复杂内容按问题选择业务流程图、页面流转图、时序图、状态机图、模块关系图或数据流图；简单流程用编号步骤，普通 L2 通常不超过 2–3 张图。历史 20 章 PRD 继续兼容。

### 证据驱动上下文

系统分别判断产品目标、当前现状和外部约束，不把历史 PRD 当线上事实，也不把当前代码直接当目标规则。需求调研按 L1/L2/L3 核验用户输入、项目知识、当前实现、必要历史、数据反馈和适用的官方资料：政策/合规匹配目标地区与发布日期，SDK/API 匹配当前或已确认目标版本，升级同时核查源版本、目标版本和迁移指南。PRD 前生成、评审前冻结 `context-snapshot.md`。required 路径只有 `prototype-meta=COMPLETE` 才能进入正式 PRD；历史最小或无效 metadata 会定向回读 HTML、补齐并重跑门禁，失败则返回原型阶段。not_applicable 豁免路径不读取或要求 HTML/metadata。多角色复用公共核心，并检查快照、PRD 和原型版本一致。

### 窄任务

不必走完整流程：

- 只评审已有 PRD：`$game-prd-review`
- 只设计埋点：`$game-analytics-design`
- 只建原型：`$game-prototype`
- 只发布：`$game-prd-publish`

### 交互原型

有 UI/交互变化时，`game-prototype` 默认生成单文件、可点击 HTML 原型（`02-prototype/index.html`，浏览器直接打开，无需前端依赖），经用户确认且 metadata 完整后进入 PRD。无 UI/交互变化时可由产品负责人正式豁免；Agent 不得自行豁免，豁免不是窄任务，也不要求 `index.html` 或 metadata。



### 三个产品确认点

需求理解确认；原型确认，或无 UI/交互变化时由产品负责人确认豁免；仅在实际出现重大评审争议时确认。飞书不是第四个产品确认点。正式状态写入 `00-stage-state.json`，由 `scripts/check-stage-gate.py` 校验；详细合同见 `references/stage-gates.md`。

## 需求处理模式


| 模式           | 适用        | 项目知识      |
| ------------ | --------- | --------- |
| 模式1：已有模块迭代   | 命中知识库已有模块 | 读取并复用     |
| 模式2：新增独立模块   | 知识库无对应模块  | 读取架构与相邻模块 |
| 模式3：通用规范模式 | 不关联项目历史   | 不读取；仍执行需求确认和原型判断 |




## 项目知识包

项目知识是项目长期记忆，不属于通用 Skill 默认安装内容，默认只读。无知识库时通用 Skill 仍可运行，模式1/2 报告知识缺口。维护知识库需走独立的「知识维护提案」流程，不直接写入。

样例包 `life-reboots` 提供“项目整体背景 → 模块索引 → UI / 配置 / 数据 / 决策 / 版本需求来源”的参考知识结构。UI 模块保存项目视觉参考图，并将其整理为单文件 HTML 原型可执行的组件与适配规范；原型运行时不依赖这些图片。能力按“已上线、迁移中、目标架构、规划候选、已废弃”区分；未上线但已确认的目标架构仍是后续新需求必须检查的设计约束。

## 工作目录与产物

在目标游戏项目中，PRD 与工作产物按约定存放：

- 正式 PRD：校验通过后同步到 `docs/prd/`（本地权威源，或项目既有正式 PRD 目录）；此时 `prd.status=final`，正式 PRD 流程完成。
- 工作历史：`history/<日期>-<需求简称>/`，保存 `00-stage-state.json`、新需求调研产物 `00-research-findings.md`、阶段摘要 `context-snapshot.md` 和按复杂度实际需要的决策、原型/豁免、过程稿、评审、校验及冻结终稿；旧 `00-project-context.md` 不强制迁移。
- 格式校验报告：`06-lint-report.md`（由 `scripts/lint-prd.py` 自动产出，校验配置表结构、埋点 12 列事件明细表、规则/验收编号唯一性与映射；无需手写）。
- 交付记录：仅项目策略要求或用户显式发布时由 `game-prd-publish` 写入；失败不回退 PRD。

窄任务不必创建无关空文件；按任务阶段创建所需文件即可。

## 架构

```text
mobile-game-product-forge/          仓库根 = 主编排器 Skill
├── SKILL.md                        轻量编排器（模式/确认门/路由/校验）
├── agents/openai.yaml              主编排器 interface 元数据
├── AGENTS.md                       维护者指引
├── README.md                       用户文档
├── CHANGELOG.md                    变更记录
├── operation-guide.md              面向使用者的日常操作文档
├── install-guide.md                面向使用者的安装与升级指南（一次性配置 + 故障排查）
├── package.json                    唯一版本源
├── .claude-plugin/plugin.json      Claude 插件清单（显式根入口 + 默认 skills/ 子 Skill 扫描）
├── .claude-plugin/marketplace.json 同仓自托 marketplace（fairyland-forge，插件条目指向 ./）
├── references/                     共享领域规范（9 Markdown + 1 JSON Schema）
├── skills/                         8 个子 Skill
├── install-profiles/               core 与 core-life-reboots 安装档案
├── knowledge-packs/life-reboots/   可选项目知识包
├── scripts/                        安装、校验与运行时脚本
├── fixtures/                       PRD lint、自然语言路由与 11 类能力回归夹具
├── docs/capability-regression.md   真实质量回归执行与记录协议
└── history/                        开发历史归档（progress/research，只读参考）
```



## 参考规范（references/）

被主 Skill 与子 Skill 共享的领域规范，共 9 个 Markdown 文件和 1 个 JSON Schema：


| 文件                         | 内容             |
| -------------------------- | -------------- |
| `workflow.md`              | 需求到终稿及完成后独立分支 |
| `context-loading.md`       | 证据驱动渐进加载、快照、版本与多角色输入合同 |
| `stage-gates.md`           | JSON 状态、原型豁免、机器门禁与窄任务边界 |
| `stage-state.schema.json`  | 状态结构、必需字段、枚举与复杂度策略唯一机器源 |
| `prd-spec.md`              | PRD 研发执行结构、规则与配置契约 |
| `prd-diagrams.md`          | 六类按需图形的触发条件、示例与限制 |
| `templates.md`             | 章节与产物模板        |
| `mobile-game-checklist.md` | 移动游戏专项风险检查     |
| `project-knowledge.md`     | 知识库结构          |
| `csv-config-deliverable.md`| 配置 CSV、字段说明与配置说明交付物规范 |
| `feishu-publish.md`        | 飞书发布           |




## 脚本


| 脚本                                    | 作用                                                    |
| ------------------------------------- | ----------------------------------------------------- |
| `scripts/install.sh`                  | 跨 Agent 安装/卸载，整包链接，可选初始化知识包（macOS/Linux/Windows Git Bash）        |
| `scripts/install.ps1`                 | Windows 原生安装/卸载（PowerShell 5.1+），软链优先/复制回退，写 `MOBILE_GAME_PRODUCT_FORGE` 环境变量 |
| `scripts/validate.sh`                 | P0 架构 + P1 结构/链接/版本/元数据/调用配置/逆向覆盖校验                   |
| `scripts/validate-p0-architecture.sh` | P0 架构不变量校验（由 validate.sh 调用）                          |
| `scripts/check-stage-gate.py`        | 阶段门禁 CLI；保持原有调用方式与 `--extract-prototype-meta` 入口 |
| `scripts/stage_gate_core.py`          | 正式阶段状态、共同前置和下游门禁的核心校验逻辑 |
| `scripts/prototype_meta.py`            | prototype metadata 提取、语义完整性和占位符分类 |
| `scripts/stage_gate_selftest.py`      | 阶段门禁与 metadata 回归用例，避免测试代码膨胀 CLI 文件 |
| `scripts/validate-regression-fixtures.py` | 校验路由与 11 类真实能力回归夹具的结构、覆盖和期望结果 |
| `scripts/lint-prd.py`                 | PRD 格式校验：配置表结构、埋点 12 列、规则/验收编号，产出 `06-lint-report.md` |
| `scripts/doc-impact-check.sh`         | 维护预检：改动路径 -> 受影响维护文档建议 + AGENTS §10 检查表自动标注（建议、非阻断）      |


`check-stage-gate.py` 和 `lint-prd.py` 是运行时脚本，从用户项目调用时通过 `MGPF` 片段按四级顺序定位 skill 仓库根（`MOBILE_GAME_PRODUCT_FORGE` 环境变量 -> `CLAUDE_PLUGIN_ROOT` -> `~/.claude/skills/` / `~/.codex/skills/` -> Claude Code 插件缓存 `~/.claude/plugins/cache/*/mobile-game-product-forge/<版本>/`；候选须真实含门禁脚本，防悬空软链）。跨平台双形式：macOS/Linux 与 Windows Git Bash 用 bash 形式（`python3`/`python` 双探测）；Windows 原生 PowerShell 用 pwsh 形式（`install.ps1` 已写入 `MOBILE_GAME_PRODUCT_FORGE` 用户环境变量）。调用方式见各子 Skill 正文。

## 版本与校验

- 唯一版本源：`package.json`。`SKILL.md` 与 `.claude-plugin/plugin.json` 的版本字段必须一致，由 `scripts/validate.sh` 校验。
- 提交前跑 `bash scripts/validate.sh`（或 `npm run validate`），包含 P0 架构校验与 P1 结构/链接/版本/元数据/调用配置/路由及能力回归夹具校验。真实质量回归执行协议见 `docs/capability-regression.md`。
- 推送门禁：仓库托管在 Gitee（无 GitHub Actions），用本地 pre-push 钩子替代——`git config core.hooksPath scripts/githooks` 启用，钩子跑 validate.sh + 插件清单校验 + install.sh 语法检查。
- 发版：`bash scripts/release.sh <新版本>` 一键同步三处版本、断言 CHANGELOG、跑全量校验；不 bump 版本的推送对插件用户不可见。
- `validate.sh` 会校验 README.md 与 AGENTS.md 是否提及每个子 Skill，防止文档漂移。

发布可分发快照时，可在仓库根执行：

```bash
git archive --format=zip --output=mobile-game-product-forge-<version>.zip HEAD
```

该 ZIP 只包含 `HEAD` 已跟踪内容，天然排除 `.git`、未跟踪文件、缓存和已忽略的 `__MACOSX`；打包前先确认目标版本已提交。命令不替代版本同步与发布前校验。



## 多智能体兼容

支持 Codex、Claude Code、Cursor 三种 Agent：Claude Code 推荐走插件安装（marketplace + 自动升级），也兼容 symlink；Codex 通过 symlink 安装到 skills 目录；Cursor 通过写入 `.cursor/rules` 规则文件集成。跨平台：macOS/Linux 与 Windows Git Bash 经 `scripts/install.sh` 软链安装；Windows 原生经 `scripts/install.ps1` 软链（开发者模式）或复制安装，并把仓库路径写入 `MOBILE_GAME_PRODUCT_FORGE` 用户环境变量。仓库内不携带项目级 CLAUDE.md / Cursor 规则 / Copilot 指令 / GEMINI.md；setup 也不写入这些规则文件。Cursor 的 `.cursor/rules/mobile-game-product-forge.mdc` 仅由安装脚本在用户明确选择 `--agent cursor` 时生成。

## 许可

MIT。
