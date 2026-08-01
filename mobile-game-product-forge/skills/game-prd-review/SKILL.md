---
name: game-prd-review
description: Use only when the root mobile-game-product-forge orchestrator delegates review/validation for a formal PRD, or when the user explicitly asks only to review or validate an existing mobile-game PRD as a narrow task. Performs multi-role review, risk grading, safe revision vs. escalation, and validation. Do not route broad feature design, requirement creation, or formal-PRD generation directly here; route those to the root orchestrator.
---

# 游戏 PRD 评审

负责移动游戏需求工坊的「多角色评审 -> 评审处理 -> 校验」环节。对已有 PRD 做独立角色评审、合并问题、安全修订、争议升级和最终校验。

本子 Skill 是 `mobile-game-product-forge` 的能力拆分。需求处理模式、确认门、版本号、共享工作目录和多 Agent 协议由编排器持有；正式编排时本子 Skill 只读阶段状态并验证门禁，不修改跨阶段状态。

## 前置条件

1. PRD 状态为「草稿」或「评审中」（存在 PRD 初稿 `v0.1` 或更新）。
2. 编排器已提供项目上下文版本、决策记录版本、原型版本、PRD 版本作为不可变输入快照。
3. 原型版本按路径填写：required 路径填已冻结原型版本；正式 waived 路径填豁免批准信息并检查 PRD 未引入未确认 UI；窄任务「只评审自带 PRD」无原型时填「无/不适用」，明确保真校验范围。

## 正式流程门禁

正式编排调用时，进入评审前必须读取工作目录 `00-stage-state.json`，并执行 `check-stage-gate.py --target review`。该门禁继承调研完成、需求摘要确认以及 required 原型完整或 not_applicable 豁免完整的共同前置；进入终稿校验前再执行 `--target validation`。任一门禁失败只输出门禁结果，不启动评审或生成终稿。

用户明确“只评审现有 PRD”时可作为 `narrow_task` 独立调用，须标记未执行完整流程门禁；缺少确认原型时跳过保真轴并明确风险，不修改阶段状态。

## 上下文加载

默认读取：`00-stage-state.json`、目标为 `review` 的冻结 `context-snapshot.md`、当前 PRD、当前角色规则，以及 required 路径的 `prototype-meta` 或 waived 路径的豁免证据。只读状态和快照指定的当前版本。

不默认读取：完整需求目录、旧 PRD、已替代原型、历史评审报告、完整 HTML、整个项目知识库或其他角色的完整专业规范。证据索引缺口、metadata 与 PRD 疑似漂移、多角色结论冲突、用户要求追溯、无法形成明确问题或命中高风险业务时，按 [上下文加载合同](../../references/context-loading.md)「快速执行索引」中「评审」行的默认与触发扩展章节自动回读相关原文；不得因软预算降低评审覆盖。

required 路径先分类 metadata：`COMPLETE` 作为公共核心；`INCOMPLETE` 按字段清单回读相关 HTML；`INVALID` 走历史原型降级。metadata 不完整不能静默缩小保真轴。

## 0. 预检（fan-out 前）

并行评审前先做结构可解析性预检，避免结构残缺的 PRD 进入多个并行评审 Agent 各自重发现同一缺陷、错误埋在子 Agent 上下文里难以归因。预检只判「可解析」不判「内容正确」；完整格式校验（埋点 12 列、规则-验收映射缺口等）仍留第 3 节校验。

预检项（任一失败一次性报告并停，不 fan-out）：

1. PRD 非空，核心执行章节（功能说明、功能规则、异常和边界、验收标准）可解析；L2/L3 还需总体流程。页面、接口、数据、配置、埋点只在实际涉及时检查。
2. 规则编号 `R-NNN`、验收编号 `AC-NNN` 格式可解析（唯一性与映射留第 3 节）。
3. 涉及配置时，配置表表头结构可识别（`<中文表名>（<table_name>.csv）` 与 `<字段分组>（N 个字段）`）；不要求运营后台章节。
4. 文末紧凑生成记录可解析（见主 `SKILL.md`「文档来源信息」节）。

预检复用 `lint-prd.py` 的可解析子集；若已产出 `06-lint-report.md` 先读其结构类问题。预检不通过时输出结构问题清单交回修订，不进入多角色评审。

## 1. 多角色评审

按复杂度和风险启用学科轴：L1 只选 1–2 个最相关的直接专业角色，由协调 Agent 复用 lint、门禁和确认快照做轻量标准/保真检查，不为横切轴另启 Agent；L2 动态选择相关角色并执行完整横切检查；L3 启用全部相关角色、执行完整横切检查并重点识别重大风险。不得让 L1 默认承担完整多角色流程。

- 产品负责人：实现目标、范围、规则、低成本替代、模块过拆和过度设计
- 交互负责人：移动操作路径、层级、单手操作、弹窗、页面状态、错误反馈和 UI 一致性
- 客户端负责人：实现、状态、缓存、生命周期、弱网、动画、资源、适配和兼容
- 服务端负责人：模型、接口、权限、幂等、并发、状态、事务、补偿、回滚和配置校验
- 数据负责人：指标口径、埋点、漏斗、实验和可验证性
- 测试负责人：正常、异常、边界、平台、版本、设备、配置、回归和验收可执行性——L2/L3 对每条 `AC-###` 按 `R-###` 字面执行一遍，无法据规则判定通过/失败的标「不可判定」并指出缺失条件
- 配置负责人：配置字段、默认值、误配置、生效方式、地区渠道、兼容和回滚
- 商业化负责人：广告、付费、订阅、收益、转化和平台合规

### 横切三轴

L2/L3 评审除学科轴外必带标准、保真、攻击三条横切轴并各出独立裁决段（攻击轴 L2 精简执行）；L1 由协调 Agent 做轻量检查（不含攻击轴）并合并到摘要。发现只浮出，争议仍由「评审争议确认门」裁定：

- 标准轴：PRD 是否遵循 [../references/prd-spec.md](../../references/prd-spec.md) 约定，可借 `lint-prd.py` 输出与「PRD smell baseline」（见 prd-spec.md「禁止模糊表达与 PRD smell」）；偏离标 `标准偏离`。
- 保真轴：required 路径核对已确认摘要与冻结原型；waived 路径核对豁免边界且 PRD 未虚构交互；偏离标 `漂移`。
- 攻击轴（L2/L3；L1 不启用）：以破坏者身份主动构造具体场景攻击 PRD，覆盖五类：经济/奖励漏洞（重复领取、并发、重放、补签组合刷取）；规则矛盾（两条 `R-###` 在同一场景推导出不同结果）；状态机死角（不可达、无法退出、无恢复路径的状态）；时间边界（时区、跨天瞬间、赛季/活动切换）；平台时序（切后台、断网、杀进程与关键操作交叠）。每条发现必须附「复现场景」：初始状态 → 操作序列 → 按 `R-###` 逐步推导 → 矛盾或漏洞结果；无法给出复现场景的抽象担忧（如「可能存在并发问题」）不得作为发现浮出。L2 只浮出 top 3 攻击场景（P0 豁免预算），L3 按每角色预算完整执行。发现按 P0/P1/P2 分级进入既有合并流程，不新增独立通道，不自动触发争议门。

### 并行与分歧保留

运行时支持隔离上下文并行时，先冻结同一快照和当前 PRD。每个角色收到相同的公共业务核心（用户目标、范围、主流程、核心规则、关键状态/异常/风险、版本）和本角色专业增量，不重新读取整个项目或完整 HTML，不相互继承未合并结论，不直接编辑 PRD，不决定重大产品问题。只有 PRD 很长、角色只需少量章节或 L3 跨模块上下文明显过大时才生成临时角色切片；切片必须保留公共核心且不成为权威文档。

每个角色输出头必须记录 `reviewRole`、`snapshotVersion`、`prdVersion`、`prototypeVersion`、`reviewedAt`。角色返回后，协调 Agent 只读取冻结快照、当前 PRD 和各角色问题列表，先验证所有角色的快照/PRD 版本一致，以及 required 路径相关角色的原型版本一致，并检查评审期间输入是否被修改。任一角色过期时不得进入 `passed`；只向过期角色提供当前输入并重审受影响部分，记录不一致原因。

版本一致后再检查数据目标、端状态、商业规则验收及同一规则的矛盾理解；发现事实冲突按证据索引扩大原文读取。合并段必须保留各角色分段（见 [../references/templates.md](../../references/templates.md)「评审问题」）和分歧裁决，不得折叠为单一排序列表。运行时不支持隔离并行时，回退为单 Agent 依次扮演各角色，输入合同与输出合同不变。

### 每角色预算

每个启用角色只浮出 top 发现（默认 top 5 或 ≤300 字），P0/P1 豁免以免阻塞项被压缩；零发现角色可在合并段省略。预算迫使聚合面信号密集，避免 8 角色无界输出使评审不可读。

### PRD smell baseline

每次评审带入固定 smell 清单（见 prd-spec.md「禁止模糊表达与 PRD smell」）；`lint-prd.py` 已覆盖项跳过，项目/playbook 标准可 override。

风险分级：

- P0：阻塞开发或可能造成严重线上事故，必须修改
- P1：明显逻辑、体验或维护风险，建议本期修改
- P2：不影响本期上线，可后续优化

## 2. 评审处理

### P0 反驳验证（合并前）

合并前，协调 Agent 对每条 P0 及拟触发评审争议确认门的发现执行一次反驳尝试：以「证明该发现不成立」为目标，只依据 PRD 原文、冻结快照、已确认摘要与原型 metadata 核对，不得引入证据外的推断。反驳成立的降级（P1/P2）或删除并记录理由；反驳失败的保留，并在合并报告该条目附「反驳尝试：未推翻（<一句理由>）」。运行时支持隔离并行时，可将反驳派给未参与原发现的独立 Agent 执行。反驳验证不适用于 lint 机器判定项。

合并重复问题和角色分歧后，由协调 Agent 统一修订。

可直接修订：

- 格式或编号错误
- 已有内容的前后冲突
- 缺少异常、字段说明、验收 Case 或埋点参数说明

需要用户确认的六类事项见下文「评审争议确认门」，不得由 Agent 决定。

其中第 6 项（交互类）经产品负责人裁定确需改变交互时，返回 `game-prototype` 重新确认，随后更新 PRD 并只重审受影响部分，再写 `passed`；返回原型是裁定后的解决路径，不是独立于 `disputed` 的分类。

需要重冻需求摘要（调用 `game-requirement-discovery`）：

- 评审争议确认门确认核心规则、主流程或范围变化，且使已冻结《需求理解与方案摘要》失效时
- 重冻方式：bump 摘要（`01-requirement-summary.md`）版本为 `v1.1-Confirmed`（增量修订）或标旧版 `v1.0-Superseded`（重大替代），更新决策账本（`01-requirement-decisions.md`）后再进原型；不得在 PRD 层打补丁绕过摘要重冻（混淆「评审已解决」与「摘要已冻结」会让陈旧摘要误导原型返工）

每次规则修改同步检查：原型、页面文案、客户端、服务端、配置、数据结构、埋点、验收和风险。

### 评审状态收口

计划角色均完成、所有角色输入版本一致、`openP0=0`、P1/P2 均记录处理结论，且不存在重大争议（含需返回原型的交互变化——交互变化本身即重大争议事项）时，协调 Agent 直接写 `review.status=passed`，并向用户汇报角色覆盖、P0/P1/P2 摘要、已修改项与遗留项，不额外请求确认。

「所有角色输入版本一致」由脚本判定，不依赖协调 Agent 逐段目检：角色分段写入 `04-review-report.md` 后、写 `passed` 前运行版本头一致性校验（`MGPF` 定位片段同下文第 3 节校验环节）：

```bash
"$PY" "$MGPF/scripts/lint-review-report.py" 04-review-report.md
```

退出码 0 才允许收口为 `passed`；1 表示缺字段或版本不一致，按上文只重审受影响角色后重跑；2 表示报告缺失或角色版本头不可解析，先按 [../references/templates.md](../../references/templates.md) 第 6 节修复报告格式。waived 路径与无原型窄任务的 `prototypeVersion` 特例值按该节约定填写，脚本不将其计入实版本比对。

实际出现重大争议（含交互变化）时写 `review.status=disputed`、记录 blocker 并暂停。产品负责人裁定后，若交互未变化可关闭争议后通过；若页面、入口、主路径、按钮、弹窗、确认步骤或关键状态变化，先返回 `game-prototype` 重新确认，再更新 PRD 并重审受影响部分。重大争议范围、blocker 格式与状态迁移以 [stage-gates.md](../../references/stage-gates.md) 为唯一权威源。

## 3. 校验

检查四类问题：

1. 格式：统一执行结构、标题、命名、字段格式、编号、空章节和模糊表达
2. 完整性：实现目标、主流程、规则、相关页面、接口/数据/配置、异常、验收，以及被触发的指标/第三方/迁移/灰度专项
3. 一致性：调研、确认摘要、原型、流程、页面、规则、端职责、配置、数据来源和验收
4. 移动游戏专项：按 [../references/mobile-game-checklist.md](../../references/mobile-game-checklist.md)

格式校验脚本：运行以下命令自动校验配置表结构、埋点 12 列事件明细表、规则/验收编号唯一性与映射，报告写入工作目录 `06-lint-report.md`。按宿主 shell 选其一（macOS/Linux 与 Windows Git Bash 用 bash；Windows 原生 PowerShell 用 pwsh）：

```bash
# bash / Git Bash / WSL（Claude Code、Codex 在 Windows 走 Git Bash）
MGPF="${MOBILE_GAME_PRODUCT_FORGE:-${CLAUDE_PLUGIN_ROOT:-}}"
if [ -z "$MGPF" ]; then
  for d in "$HOME/.claude/skills/mobile-game-product-forge" "$HOME/.codex/skills/mobile-game-product-forge" $(ls -dt "$HOME/.claude/plugins/cache"/*/mobile-game-product-forge/*/ 2>/dev/null); do
    [ -f "$d/scripts/check-stage-gate.py" ] && MGPF="$d" && break
  done
fi
PY="$(command -v python3 || command -v python)"
"$PY" "$MGPF/scripts/lint-prd.py" <PRD 文件或工作目录> -o 06-lint-report.md
```

```powershell
# PowerShell（Cursor 原生 Windows，或用户直接在 pwsh 跑）
$MGPF = $env:MOBILE_GAME_PRODUCT_FORGE; if (-not $MGPF) { $MGPF = $env:CLAUDE_PLUGIN_ROOT }
if (-not $MGPF) {
  $cands = @("$env:USERPROFILE\.claude\skills\mobile-game-product-forge", "$env:USERPROFILE\.codex\skills\mobile-game-product-forge") + @(Get-ChildItem "$env:USERPROFILE\.claude\plugins\cache\*\mobile-game-product-forge\*" -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | ForEach-Object FullName)
  $MGPF = $cands | Where-Object { Test-Path "$_\scripts\check-stage-gate.py" } | Select-Object -First 1
}
python "$MGPF\scripts\lint-prd.py" <PRD 文件或工作目录> -o 06-lint-report.md
```

`MGPF` 定位 skill 仓库根，四级顺序：`MOBILE_GAME_PRODUCT_FORGE` 环境变量（逃生舱；Windows 经 `scripts/install.ps1` 安装时自动写入）→ `CLAUDE_PLUGIN_ROOT`（插件运行时若提供）→ 脚本安装目录 `~/.claude/skills/`、`~/.codex/skills/` → Claude Code 插件缓存 `~/.claude/plugins/cache/*/mobile-game-product-forge/<版本>/`；每个候选须真实含有 `scripts/check-stage-gate.py` 才被采用（防悬空软链）。Windows 上 `python3` 常缺失，bash 形式用 `command -v python3 || command -v python` 双探测、PowerShell 形式直接用 `python`。退出码非 0 表示存在格式错误，须修订后重跑；仅「提示」级（如历史标识符非 snake_case、规则未被验收引用）可列为已知项继续。脚本只覆盖第 1 类「格式」中可机器判定的部分，不替代人工对完整性、一致性、移动游戏专项的判断。

结论只允许：`通过`、`有条件通过`、`不通过`。

## 评审争议确认门

以下事项实际出现时不得由 Agent 决定；无重大争议时不触发本确认门（唯一判定以 [../references/stage-gates.md](../../references/stage-gates.md)「评审通过与重大争议的唯一判定」为准）：

1. 商业模式或商业化规则变化
2. 需求范围扩大
3. 核心规则或主流程变化（含次数维度）
4. 重大技术方案变化
5. 多个方案均合理
6. 页面、入口、按钮、弹窗、确认步骤或关键页面状态变化（新增或改变）

给出推荐方案、备选方案、取舍和影响，等待用户决定。

## 完成标准

- 无 P0 问题，核心执行章节完整；条件章节只在实际涉及时存在
- required 原型已确认且 PRD 一致，或正式豁免证据完整且 PRD 未引入 UI/交互变化（无原型窄任务只声明内部自洽）
- 规则编号、验收编号唯一且存在映射
- 配置表名、字段命名和字段格式合规
- 客户端与服务端职责清晰
- 埋点能够计算核心指标
- 移动游戏专项风险已检查
- L2/L3：攻击轴发现均已处理，P0 均有反驳记录；不可判定 AC 已修订或标记待确认
- 所有推断和未决项均有明确标记

校验不通过时输出报告并继续修订，不得把文档称为“最终版”。校验通过后交由编排器更新产物版本和本需求目录的变更记录（若存在）。若作为窄任务独立调用，只输出评审报告与建议修改清单，不直接修订既有 PRD 或正式流程状态。

## 参考

- 上下文加载清单：[../references/context-loading.md](../../references/context-loading.md)「快速执行索引」——「评审」行是本阶段默认与扩展章节的唯一权威清单，本 Skill 不复制
- 阶段状态与硬门禁：[../references/stage-gates.md](../../references/stage-gates.md)

- PRD 结构：[../references/prd-spec.md](../../references/prd-spec.md)
