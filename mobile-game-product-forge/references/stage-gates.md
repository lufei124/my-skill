# 阶段状态与硬门禁

## 1. 适用范围与状态所有权

本规范用于 `mobile-game-product-forge` 的正式需求编排。正式需求必须由根编排器启动，在独立工作目录创建 `00-stage-state.json`；根编排器是唯一写入者，子 Skill 只读状态并执行机器门禁。

用户明确只做原型、评审、埋点、校验或交付时，可以显式调用对应子 Skill 并标记 `narrow_task`。窄任务不创建、不修改 `00-stage-state.json`，也不调用正式阶段门禁；只要提供了正式状态文件，`review / validation / final / publish / delivery` 就必须继承调研、需求摘要以及 required 原型或 not_applicable 豁免的共同前置。原型不适用的正式路径不是窄任务，仍受正式 PRD 门禁保护。

三个产品确认点是：

1. 需求理解确认；
2. 原型确认，或无 UI/交互变化时由产品负责人确认原型豁免；
3. 重大评审争议确认（仅在实际存在重大争议时触发）。

飞书发布是项目交付策略，不是第四个产品确认点。PRD 完成条件始终是 `prd.status=final` 且 `validation.status=passed`。

## 2. 状态契约

新需求只生成 JSON 1.1 状态。结构、必需字段、枚举和 L1/L2/L3 策略的唯一机器可读来源是 [stage-state.schema.json](stage-state.schema.json)；[templates.md](templates.md) 只提供实例，不另立词表。

- 状态文件：`history/<日期>-<需求简称>/00-stage-state.json`
- Schema：`references/stage-state.schema.json`
- 旧 `00-stage-state.yaml`：历史需求可原样保留，不强制迁移；新脚本读到时返回 `INVALID_STATE` 并提示“旧状态格式”。

状态与文件冲突时按更保守状态处理。文件存在、文件名含 `final`、聊天里似乎确认过，都不能代替显式状态和确认记录。

所有正式需求进入原型或 PRD 前都必须完成调研。协调 Agent 在需求发现 Skill 写出调研产物后更新现有字段：

```json
{
  "projectContext": {
    "status": "completed",
    "file": "00-research-findings.md",
    "version": "v1.0"
  }
}
```

`file` 必须是当前需求目录内的相对路径，文件真实存在；新需求只允许 `00-research-findings.md`，历史兼容允许 `00-project-context.md`（可位于当前需求目录的既有子目录）。`version` 必须非空。新格式调研文件不得为空，并至少包含「当前现状、目标状态、当前状态与目标状态差异、风险、来源索引」五个稳定标题；旧格式调研文件至少不得为空。调研完成不增加用户确认门。

### 跨字段一致性（全局）

机器门禁在判断目标阶段前先检查状态内部是否自洽；以下任一情况返回 `INVALID_STATE`（退出码 3），缺失字段不得按安全默认值补齐：

- `prototype.applicability=required` 且 `prototype.status=waived`；
- `prototype.applicability=not_applicable` 且 `prototype.status=confirmed`；
- `delivery.required=false` 但 `delivery.status` 不是 `not_required`，或 `delivery.required=true` 但状态是 `not_required`；
- `prd.status=final`，但校验未通过、校验文件不存在、`targetPrdVersion` 与 `prd.version` 不一致、PRD 文件不存在，或 `prd.syncedTo` 未记录/同步文件不存在；
- `review.status=passed`，但 `openP0` 不是显式整数 0、评审文件不存在，或仍有未解决重大争议；
- `review.status=disputed`，但没有重大争议说明标记。

重大争议复用顶层 `blockers`，不增加新的跨阶段状态字段。推荐条目为 `{"type":"major_review_dispute","description":"...","status":"open"}`；兼容字符串前缀 `[major_review_dispute]` / `[重大评审争议]`。`status` 为 `resolved`、`closed`、`decided`、`已解决` 或 `已裁定` 时视为已解决。普通 blocker 不等于重大争议。

## 3. 原型适用性

协调 Agent 推荐适用性，产品负责人确认：

- 新页面、入口、主路径、按钮、弹窗、状态反馈或交互变化：`prototype.applicability=required`，不得豁免。
- 服务端规则、配置/频控、数据口径、埋点、白名单/国家规则、订单补偿、纯技术兼容等无 UI 或交互变化：可以设为 `not_applicable`。
- Agent 不得自行豁免。产品负责人可在确认需求摘要的同一轮同时确认豁免，避免增加一次无意义往返。

进入 PRD 必须先满足共同前置：`projectContext.status=completed`，调研文件/版本有效；需求摘要已确认且文件/版本有效。随后满足二选一：

1. required：`status=confirmed`，文件和版本存在，`confirmedAt` 非空；metadata 必须分类为 `COMPLETE`、`prototypeStatus=Confirmed` 且 metadata 版本等于状态版本。`INCOMPLETE` / `INVALID` 和历史最小 metadata 均不得通过；消费 Skill 按 [context-loading.md](context-loading.md)「prototype-meta 完整性与 HTML 降级」定向回读、补齐并重新分类。
2. not_applicable：`status=waived`，`waiverReason`、`approvedBy`、`approvedAt` 均非空；不要求原型文件、metadata 或 HTML 回读。

## 4. 门禁矩阵

| target | 必须满足 | 阻塞后返回 |
|---|---|---|
| `prototype` | 调研=`completed` 且文件/版本有效；需求摘要=`confirmed` 且文件/版本有效；`prototype.applicability=required` | 调研缺口返回 `requirement_discovery`，其余返回 `requirement_confirmation` |
| `prd` | 调研与需求摘要证据完整；required 原型 metadata COMPLETE，或 not_applicable 豁免证据完整 | 调研缺口返回 `requirement_discovery`，原型分支缺口返回 `prototype` |
| `review` | 继承正式共同前置；PRD=`draft/in_review`；PRD 文件存在；版本非空 | 最早缺口对应阶段，否则 `prd` |
| `validation` | 继承正式共同前置；评审=`passed`；`openP0` 显式为整数 0；评审文件/版本与 PRD 文件/版本存在 | 最早缺口对应阶段，否则 `review` |
| `final` | 继承正式共同前置；validation 前置条件；校验=`passed`；校验文件存在；`targetPrdVersion=prd.version`；`prd.syncedTo` 已记录且同步文件存在 | 最早缺口对应阶段，否则 `validation` |
| `publish` | 继承正式共同前置；飞书交付预检：PRD=`final`、校验通过及证据一致；`delivery.required=false` 返回 `NOT_REQUIRED` | 最早缺口对应阶段，否则 `final` |
| `delivery` | 继承正式共同前置；`required=false` 返回 `NOT_REQUIRED`；否则在发布预检基础上要求 `status=published`、交付记录和发布时间 | 最早缺口对应阶段，否则 `delivery` |

`publish` 允许 `game-prd-publish` 在尚未发布时执行交付动作；`delivery` 用于检查项目交付是否完成。`delivery` 阻塞或失败不修改、不回退 `prd.status=final`。

## 5. 机器校验

```bash
# macOS / Linux / Git Bash / WSL
MGPF="${MOBILE_GAME_PRODUCT_FORGE:-${CLAUDE_PLUGIN_ROOT:-}}"
if [ -z "$MGPF" ]; then
  for d in "$HOME/.claude/skills/mobile-game-product-forge" "$HOME/.codex/skills/mobile-game-product-forge" $(ls -dt "$HOME/.claude/plugins/cache"/*/mobile-game-product-forge/*/ 2>/dev/null); do
    [ -f "$d/scripts/check-stage-gate.py" ] && MGPF="$d" && break
  done
fi
PY="$(command -v python3 || command -v python)"
"$PY" "$MGPF/scripts/check-stage-gate.py" \
  --state "<需求工作目录>/00-stage-state.json" \
  --target prd
```

```powershell
# Windows PowerShell
$MGPF = $env:MOBILE_GAME_PRODUCT_FORGE; if (-not $MGPF) { $MGPF = $env:CLAUDE_PLUGIN_ROOT }
if (-not $MGPF) {
  $cands = @("$env:USERPROFILE\.claude\skills\mobile-game-product-forge", "$env:USERPROFILE\.codex\skills\mobile-game-product-forge") + @(Get-ChildItem "$env:USERPROFILE\.claude\plugins\cache\*\mobile-game-product-forge\*" -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | ForEach-Object FullName)
  $MGPF = $cands | Where-Object { Test-Path "$_\scripts\check-stage-gate.py" } | Select-Object -First 1
}
python "$MGPF\scripts\check-stage-gate.py" --state "<需求工作目录>\00-stage-state.json" --target prd
```

脚本只使用 Python 标准库。它校验：

- JSON、Schema 版本、必需对象/字段、字段类型和枚举；
- 已声明文件路径位于当前需求目录或所属项目目录，且文件真实存在；
- prototype / PRD 以及所有正式下游门禁共同继承调研、确认摘要、required 原型或 not_applicable 豁免证据；
- 各门所需文件与版本证据；
- required 原型 metadata 状态和版本；
- required 原型 metadata 的必需字段、类型、枚举、页面/场景/状态结构、合法决策、重复 ID 和 Confirmed 最低内容；完整字段合同见 [context-loading.md](context-loading.md)「prototype-meta 完整性与 HTML 降级」；
- waived 原型的原因、批准人和批准时间；
- `review.openP0` 不缺失且显式为整数 0；
- 校验报告与当前 PRD 版本一致；
- 终稿同步证据：`final` 门禁与 `prd.status=final` 均要求 `prd.syncedTo` 非空且同步文件真实存在（完成判定第 3 条的机器核验）；
- PRD 完成与飞书交付状态分离。

退出码：

- `0`：`PASS` 或 `NOT_REQUIRED`
- `2`：`BLOCKED`；metadata 提取入口表示 `INCOMPLETE`
- `3`：`INVALID_STATE`

`--extract-prototype-meta <index.html>` 始终输出紧凑 JSON：`COMPLETE` 返回 0 并携带 metadata；合法但不完整返回 `INCOMPLETE`、精确的 `missingFields` / `invalidFields` / `duplicateIds` 和 `nextAction=read_relevant_html`，退出 2；缺失、非法 JSON 或非对象返回 `INVALID`，退出 3。Confirmed metadata 中真实业务字段仍为「待补充 / 待确认 / TODO / TBD / PLACEHOLDER / 示例」等精确占位值时归为 `INCOMPLETE`，但 `decisions[].status=待确认` 仍为合法枚举。结果不包含 HTML、CSS 或 JavaScript。该入口只用于 required 路径。

业务前置未完成（例如调研 `not_started`、摘要未确认）返回 `BLOCKED`（退出 2）。状态声明 `projectContext.status=completed` 却文件/版本为空、文件不存在、使用无关文件名或绝对路径、调研文件为空或新格式缺少最低结构标题时属于自相矛盾，返回 `INVALID_STATE`（退出 3）。

## 6. 输出合同

门禁阻塞时字段顺序固定：

```text
BLOCKED
target:
currentStage:
missingConditions:
invalidFields:
returnToStage:
nextAction:
```

状态格式或字段非法时首行为 `INVALID_STATE`，其余字段相同。`--json` 输出同名字段的 JSON object。门禁失败的同一回复中不得生成 PRD 章节、`R-###`、接口、配置表、验收 Case、终稿或发布成功结果。

## 7. 复杂度路由

协调 Agent 推荐复杂度，产品负责人可以调整；机器可读策略见 Schema 的 `x-complexityPolicies`：

- L1：精简访谈（目标 1–2 轮，主题裁剪见 game-requirement-discovery）/精简摘要；原型 required 或正式豁免；精简 PRD；启用 1–2 个最相关的直接专业角色，协调 Agent 复用 lint、门禁和已确认快照做轻量标准/保真检查，不为横切轴另启 Agent；不机械创建全部过程文件；不默认知识提案；仅项目策略要求时交付。
- L2：标准访谈（目标 3–5 轮）；原型 required 或正式豁免；标准 PRD；动态启用相关专业角色，并执行完整标准/保真横切检查与攻击轴（top 3 攻击场景，见 game-prd-review）；按长期价值决定知识提案；按项目策略交付。
- L3：完整上下文和决策追踪（访谈按需，每 5 轮向用户汇报进度并提供批量确认选项）；原型通常 required；启用全部相关专业角色，执行完整标准/保真/攻击三轴横切检查并重点识别重大风险；必须评估知识提案；按项目策略交付。

复杂度不允许删除需求理解确认、原型确认/豁免或重大争议确认。

## 8. 标准状态迁移

| 事件 | 状态更新 |
|---|---|
| 创建正式需求 | 写入 JSON 1.1；复杂度由协调 Agent 推荐、产品负责人可调整 |
| 完成需求调研 | 协调 Agent 写 `projectContext.status=completed`、允许的调研文件相对路径和非空版本；不新增确认门 |
| 用户确认需求摘要 | `requirementSummary.status=confirmed`，记录文件（`01-requirement-summary.md`，历史需求兼容 `01-requirement-decisions.md`）与版本 |
| 判定需原型 | `prototype.applicability=required` |
| 用户确认原型 | `prototype.status=confirmed`，记录文件、版本和 `confirmedAt` |
| 产品负责人确认不适用 | `applicability=not_applicable`、`status=waived`，记录原因/批准人/时间 |
| 生成 PRD 初稿 | `prd.status=draft`，记录文件与版本 |
| 开始评审 | `prd.status=in_review`、`review.status=in_progress` |
| 无重大争议且评审完成 | 计划角色完成、角色报告的 snapshot/PRD/prototype 版本一致、`openP0=0`、P1/P2 结论已记录且无须返回原型时，协调 Agent 直接写 `review.status=passed` 并向用户汇报评审摘要，无需额外确认 |
| 出现重大评审争议 | 写 `review.status=disputed`，在 `blockers` 记录重大争议并暂停；不得进入 validation/final |
| 产品负责人裁定争议 | 记录决定并关闭争议标记；若不改变交互，可写 `review.status=passed`；若改变交互，先返回原型确认、更新 PRD、重审受影响部分，再写 passed |
| 校验通过 | `validation.status=passed`，记录报告和目标 PRD 版本 |
| 冻结终稿 | 先把终稿同步到 `docs/prd/<需求简称>.md`（或项目既有正式 PRD 目录）并写入 `prd.syncedTo`，再写 `prd.status=final`；正式 PRD 流程完成 |
| 终稿后重开修订 | 记录重开原因后：`prd.status` 由 `final` 回 `in_review`、bump `prd.version`（如 v1.0→v1.1）、`validation.status=not_started` 并清空 `validation.file` 与 `targetPrdVersion`、`requirement.currentStage=review`；只重审受影响部分，不回退已确认摘要与原型；重开涉及交互或摘要变化时按评审争议与重冻规则处理；不回退 `delivery` 历史记录 |
| 重开后重新冻结终稿 | 复用「校验通过」与「冻结终稿」事件；`validation.targetPrdVersion` 必须等于 bump 后的 `prd.version`；按项目交付策略重新交付 |
| 无强制交付 | `delivery.required=false`、`status=not_required` |
| 开始飞书交付 | `delivery.status=in_progress`，PRD 仍为 `final` |
| 飞书交付成功 | `delivery.status=published`，记录交付文件与 `publishedAt` |
| 飞书交付失败 | `delivery.status=failed`，记录失败；不回退 PRD |

### 正式 PRD 流程完成的唯一判定

本节是「校验完成 / 正式 PRD 流程完成」的唯一权威定义。其他文档只引用本节，不复述条件。三条必要条件缺一不可：

1. `validation.status=passed`，且已记录校验报告与 `validation.targetPrdVersion`（等于当前 `prd.version`）。
2. 工作目录 `07-prd-final.md` 已作为冻结快照保留。
3. 正式终稿已同步到 `docs/prd/<需求简称>.md`（或项目既有正式 PRD 目录），同步位置写入 `prd.syncedTo`，随后写入 `prd.status=final`。本条由机器门禁核验：`--target final` 与 `prd.status=final` 的跨字段一致性均要求 `prd.syncedTo` 非空且文件存在。

只满足其中一条或两条时，不得声称「校验完成」「最终版」或「流程完成」。本判定与 `delivery` 完全无关：`delivery.required=false` 时流程照常完整完成，飞书交付失败也不回退本判定（见「标准状态迁移」的 `delivery` 事件）。

### 评审通过与重大争议的唯一判定

无重大争议时，评审不是第三次固定确认：计划角色全部完成，角色报告记录 `reviewRole`、`snapshotVersion`、`prdVersion`、`prototypeVersion`、`reviewedAt` 且输入版本一致，`review.openP0` 显式为整数 0、P1/P2 均已记录处理结论，且没有需要返回原型的交互变化，协调 Agent 应直接把 `review.status` 更新为 `passed`，并向用户汇报角色覆盖、P0/P1/P2 摘要、已修改项与遗留项。发现过期角色时只重审受影响部分，不新增状态字段。

实际出现以下任一情况才触发第三个确认点并写 `review.status=disputed`：商业模式或商业化规则变化、需求范围变化、核心规则或主流程变化、重大技术方案变化、多个方案均合理，或新增/改变页面、入口、按钮、弹窗、确认步骤、关键页面状态。协调 Agent 必须给出争议、推荐方案、备选方案、取舍与影响并暂停，等待产品负责人裁定。

裁定后先记录决定并关闭对应争议标记。若裁定改变页面、入口、主路径、按钮、弹窗、确认步骤或关键状态，必须返回原型阶段重新确认，随后更新 PRD 并只重审受影响部分；不得从 `disputed` 直接进入 validation/final。完整状态校验由 `check-stage-gate.py` 执行。

## 9. 旧 YAML 迁移

不批量改历史需求。需要继续维护某个旧需求时，由根编排器：

1. 读取旧 YAML 和实际阶段产物，明确提示“旧状态格式”；
2. 依据 [templates.md](templates.md) 的 JSON 1.1 模板创建同目录 `00-stage-state.json`；
3. 对每个确认状态重新核对文件、版本和用户证据，不把缺失字段默认成通过；
4. 保留原 YAML 作为历史证据，不覆盖、不删除；
5. 后续只写 JSON。
