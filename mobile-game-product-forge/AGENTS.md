# AGENTS.md

本文件面向在本仓库内**维护 `mobile-game-product-forge` Skill 框架**的 Agent（Claude Code / OpenAI Codex / Cursor）。它规定 Agent 如何安全修改本仓库：不是使用说明（使用见 [README.md](README.md)），不是 PRD 格式规范（见 [references/](references/)），也不复述 Skill 执行契约（见 [SKILL.md](SKILL.md)）。

## 1. 仓库身份与 Agent 职责

- 本仓库是**可安装的 Skill 框架**，不是某个游戏的项目代码。维护对象是 Skill 正文、编排逻辑、共享规范、安装配置、知识包机制、脚本与校验工具；**不得修改目标游戏项目的业务代码**。
- 仓库根目录即主编排器 Skill `mobile-game-product-forge`（`SKILL.md` + `agents/openai.yaml` + `references/`）；阶段执行下放到 `skills/<name>/`。
- 本文件只面向 Skill 仓库维护。`setup-mobile-game-product-forge` 不在目标游戏项目写入或修改 `AGENTS.md`、`CLAUDE.md`、`.cursor/` 等 Agent 规则文件；项目操作指南写入 `docs/mobile-game-product-forge/operation-guide.md`。
- 本规范适用于 Claude Code、Codex、Cursor 等仓库维护 Agent，表达不依赖某一工具独有功能。

Agent 主要职责：维护主编排器；新增/优化子 Skill；维护 `references/` 共享规范；维护安装与升级机制；维护校验脚本；保证三平台（Claude Code / Codex / Cursor）一致；保证实现、文档与配置同步。

### 仓库结构速查（role-map；完整目录树见 README.md「架构」）

| 路径 | 角色 | 可改 |
|---|---|---|
| `SKILL.md` | 主编排器：模式/复杂度/原型适用性、三个产品确认点、PRD/交付状态、路由与多 Agent 协议 | Agent |
| `agents/openai.yaml` | 主编排器 interface 元数据 + 调用策略 | Agent |
| `references/` | 共享规范：`context-loading.md` `workflow.md` `stage-gates.md` `stage-state.schema.json` `prd-spec.md` `prd-diagrams.md` `templates.md` `mobile-game-checklist.md` `project-knowledge.md` `csv-config-deliverable.md` `feishu-publish.md` | Agent |
| `skills/<name>/` | 8 个子 Skill，每个含 `SKILL.md` + `agents/openai.yaml` | Agent |
| `install-profiles/` | `core.yaml` `core-life-reboots.yaml`，声明各档案 `source_files` | Agent |
| `knowledge-packs/life-reboots/` | 可选项目知识包，`PACK.md` 维护独立包版本 | **只读** |
| `scripts/` | 安装、维护校验与运行时脚本：`check-stage-gate.py` 为 CLI，`stage_gate_core.py` 为阶段门禁核心，`prototype_meta.py` 为原型 metadata 校验，`stage_gate_selftest.py` 为门禁回归测试，`validate-regression-fixtures.py` 校验路由/能力基线，`lint-review-report.py` 校验评审报告角色版本头一致性，另含 `lint-prd.py` 等 | Agent |
| `.claude-plugin/plugin.json` | Claude Code 插件清单；`skills: ["./"]` 显式登记根编排器，默认 `skills/` 目录自动发现 8 个子 Skill（见 [ADR-0006](.agents/adr/0006-root-orchestrator-at-repo-root.md)） | Agent |
| `.agents/adr/` | 架构决策记录，追加式，只记 why + 备选 | Agent（仅追加） |
| `history/` | 开发历史归档（`progress/` `research/`） | **只读** |
| `scripts/githooks/pre-push` | 推送门禁（Gitee 无 GitHub Actions；`git config core.hooksPath scripts/githooks` 启用） | Agent |
| `package.json` | 唯一版本源 | Agent（仅发版） |
| `fixtures/` | PRD lint 夹具，以及路由/能力回归 JSON 基线 | Agent |
| `operation-guide.md` | 面向产品经理和协作角色的详细操作文档，不承载 Agent 执行契约 | Agent |
| `README.md` / `CHANGELOG.md` / `AGENTS.md` | 用户文档 / 变更记录 / 本维护手册 | Agent |

8 个子 Skill：`setup-mobile-game-product-forge`（user-invoked，一次性初始化）、`game-requirement-discovery`、`game-prototype`、`game-prd-writing`、`game-prd-review`、`game-prd-publish`、`game-analytics-design`、`game-knowledge-maintenance-proposal`。PRD 写作与发布为 explicit-only/编排器委派；其余子 Skill 虽可被模型调用，但 frontmatter description 必须限制为“根编排器委派”或用户明确的单阶段窄任务，宽泛新需求统一路由根编排器。

## 2. 指令与信息优先级（冲突时按此处理）

仓库维护冲突按以下顺序裁决（高 → 低）：

1. 用户当前明确要求
2. 本次任务的验收标准
3. 当前目录/子目录下更具体的约束（子 Skill 内 > 根）
4. 本 `AGENTS.md`
5. 实际代码、脚本与校验规则体现的真实契约（`scripts/validate.sh`、`validate-p0-architecture.sh`、`lint-prd.py` 的实际断言）
6. `references/` 共享规范
7. `knowledge-packs/`（项目事实，AI 只读）
8. `history/`（历史参考，不构成当前规范）

规则：

- **文档与脚本冲突**：脚本是「当前实际能通过校验的契约」的事实来源。文档（`AGENTS.md` / `references/`）与脚本不一致时，先报告冲突（来源、影响、建议），判断哪一方反映既定规则——`AGENTS.md` 是维护规则的权威表述，脚本是其实现——再修落后的一方，**不静默迁就任一方**。
- `history/` **只作历史参考**，不得当作当前规范引用或回滚依据。
- `knowledge-packs/` **默认只读**，AI 不得修改项目知识事实（见 [ADR-0003](.agents/adr/0003-knowledge-packs-optional-readonly.md)）；维护走 `game-knowledge-maintenance-proposal` 只输出提案。
- 不得自行覆盖存在冲突的项目事实或已确认决策；发现冲突必须报告，不静默选择。

> 注：本节是**仓库维护**冲突优先级。产品需求证据不再使用单一线性排序；产品目标、当前现状和外部约束三类权威模型见 [references/context-loading.md](references/context-loading.md)「三类权威来源模型」，不要与本节混用。

## 3. 架构边界与状态所有权（不可破坏）

| 层 | 持有 | 禁止 |
|---|---|---|
| 主编排器 `SKILL.md` | 跨阶段状态：模式、复杂度、原型适用性、三个确认点、PRD/交付、知识边界、工作目录、版本、多 Agent 与路由 | 把具体阶段执行规则堆入编排器 |
| 子 Skill `skills/<name>/SKILL.md` | 单一阶段执行：不可变输入快照 → 本环节产物 + 待确认项 | 持有跨阶段状态；复制编排器状态；承担多个阶段 |
| `references/` | 多 Skill 共享领域规则 | 把同一规则复制到多个 `SKILL.md` |
| `knowledge-packs/` | 项目事实 | AI 写入；只随 `core-life-reboots` 安装 |
| `install-profiles/` | 安装档案 `source_files` | 手工同步清单（由 `validate.sh` #6/#6b/#12 校验） |
| `.claude-plugin/plugin.json` | 插件清单（根入口 `./`；默认 `skills/` 自动扫描子 Skill） | 省略根入口；重复逐项登记默认 `skills/` 造成注册漂移（[ADR-0006](.agents/adr/0006-root-orchestrator-at-repo-root.md)） |

不可破坏的边界：

- 跨阶段状态只由主编排器创建和修改；新需求只生成 `00-stage-state.json`，子 Skill 只读并执行门禁。历史 YAML 不强制迁移、不由新脚本解析。
- 同一规则只在一个层维护：共享规则入 `references/`，阶段规则入对应子 Skill，编排状态入 `SKILL.md`。**禁止用复制文本解决共享依赖**。
- 上下文加载算法、三类权威模型、调研来源与深度、软预算、HTML 降级、高风险深读、多角色公共核心和专业增量只在 `references/context-loading.md` 维护；根和子 Skill 只保留本层默认输入、默认排除项、扩展触发与稳定章节标题链接，不得要求每轮全文加载合同。`00-research-findings.md` 是新需求调研产物，`00-project-context.md` 只作历史兼容，`context-snapshot.md` 只作阶段摘要与证据索引；快照/切片不得升级为权威源或硬读取上限。
- 所有正式需求必须完成调研并由协调 Agent 写入现有 `projectContext`，L1 只允许精简、不允许跳过；新格式调研文件必须非空且包含稳定最低结构，旧格式至少非空。这不是新增确认门。prototype 与 PRD 目标都必须执行该共同前置门禁。
- metadata 完整字段、枚举、重复 ID、Confirmed 占位值与历史 HTML 降级合同只在 `references/context-loading.md`「prototype-meta 完整性与 HTML 降级」维护；脚本集中持有机器枚举和占位词。required 路径未达到 `COMPLETE` 不得进入 PRD；not_applicable + waived 路径不得被强制要求 HTML 或 metadata。
- PRD 结构以 [ADR-0010](.agents/adr/0010-execution-oriented-prd-structure.md) 和 `references/prd-spec.md` 为准：新 PRD 使用统一 7 章研发执行结构；多模块默认只标影响范围，不按技术层拆章；项目不生成运营后台章节；历史 20 章 PRD保持兼容。
- 三个产品确认点（需求理解、原型确认/产品负责人豁免、重大评审争议）、PRD 与交付分离、知识只读边界和安装边界不得削弱（[ADR-0004](.agents/adr/0004-confirmation-gates-ironclad.md)、[ADR-0009](.agents/adr/0009-separate-prd-completion-from-delivery.md)、[ADR-0003](.agents/adr/0003-knowledge-packs-optional-readonly.md)）。第三确认点只在实际存在重大评审争议时触发；无争议不得增加固定确认轮次，详细判定集中在 `references/stage-gates.md`。

## 4. 修改前强制工作流程

修改任意文件前必须：

1. 读目标文件 + 上下游（调用方 / 被调用方）。
2. 读约束：本 `AGENTS.md` + 目标所在子目录约束 + 相关 `references/`。
3. 搜相同/相关规则（`grep -rn` 仓库内是否已有该规则），避免重复维护。
4. 判层：改动应落 主编排器 / 子 Skill / 共享规范 / 项目知识包 / 安装配置 / 插件配置 / 校验脚本 / 用户文档 中的哪一层。
5. 评影响：是否影响其他 Skill、工作流、`install-profiles/`、`plugin.json`、`agents/openai.yaml`、校验脚本、版本、`README.md`、`AGENTS.md`、`CHANGELOG.md`。
6. 定验证：按 §12 验证矩阵选定要跑的命令。
7. 执行修改。
8. 改 **完后、进 §10 文档影响的人工/Agent 判断之前**，先跑 `bash scripts/doc-impact-check.sh`，拿机器可判定的「改动路径 → §9 文档同步建议」与「§10 检查表自动标注」做参考；其余项由人工/Agent 判断（脚本建议、不阻断、退出码恒 0）。再依判断改受影响文档。

禁止只看到一个文件的问题就立即局部修改而不查上下游。

## 5. 修改原则

- 优先最小改动；不做与当前任务无关的重构。
- 不随意重命名目录、Skill、文件；不删除未知配置。
- 不覆盖其他 Agent 未提交的修改；不用破坏性 Git 命令处理未知变更。
- 不静默改变已有输入 / 输出 / 工作流契约。
- 不为适配单一 Agent 破坏跨平台兼容。
- 不以 Token、文件数量或快照存在为由停止读取必要证据；上下文优化不得降低事实完整性、原型保真、业务正确性或评审覆盖。
- 不把同一规则复制到多个文件；不把说明性文档当唯一事实，必须核对真实实现与校验脚本。
- 不为减少文件数破坏职责边界；**不让校验通过而削弱保护规则**。

较大重构前先说明：

```text
修改目标：
当前问题：
影响范围：
涉及文件：
兼容风险：
迁移方式：
验证方式：
```

## 6. Skill 开发规范

### 命名与职责

- Skill 名 `kebab-case`，阶段型以 `game-` 前缀；一个 Skill 只承担一个阶段或一类窄任务。
- 不得让一个 Skill 同时承担多个阶段；跨阶段编排归主编排器。

### 每个 Skill 必须有

- `SKILL.md`：frontmatter（`name`、`description`）+ 正文。
- `agents/openai.yaml`：`interface`（display_name / short_description / default_prompt）+ `policy.allow_implicit_invocation`（显式声明，不靠省略）。

### SKILL.md 必须描述

- 负责环节、前置条件、执行步骤、输入 / 输出 / 产物、完成条件、禁止事项、异常处理。
- **依赖编排器状态的声明**：写明模式、复杂度、原型适用性、确认点、版本、工作目录与多 Agent 协议由编排器持有；正式编排的下游 Skill 只读 `00-stage-state.json` 并执行门禁；独立窄任务标记 `narrow_task`。
- 引用共享规范用相对路径 `../../references/<file>.md`（仓库结构内有效，安装须整包链接，[ADR-0005](.agents/adr/0005-relative-path-whole-repo-linking.md)）。

### 何时新增 Skill 局部参考文件

- 仅当该规则**只本 Skill 用**且不便入 `references/` 时，才在 Skill 目录内新增；多 Skill 共用规则必须入 `references/`。
- 不强行规定每个 Skill 都要有 `examples/`、`references/`、独立版本字段、独立脚本目录（当前仓库无此固定结构）。

### 运行时脚本调用（禁止裸路径）

`lint-prd.py` 等运行时脚本从**用户项目**（cwd ≠ 仓库根）调用时，`SKILL.md` 内必须用 `MGPF` 定位片段，不得写裸 `python3 scripts/xxx.py`：

```bash
# bash / Git Bash / WSL
MGPF="${MOBILE_GAME_PRODUCT_FORGE:-${CLAUDE_PLUGIN_ROOT:-}}"
if [ -z "$MGPF" ]; then
  for d in "$HOME/.claude/skills/mobile-game-product-forge" "$HOME/.codex/skills/mobile-game-product-forge" $(ls -dt "$HOME/.claude/plugins/cache"/*/mobile-game-product-forge/*/ 2>/dev/null); do
    [ -f "$d/scripts/check-stage-gate.py" ] && MGPF="$d" && break
  done
fi
PY="$(command -v python3 || command -v python)"
"$PY" "$MGPF/scripts/lint-prd.py" ...
```

```powershell
# Windows 原生 PowerShell
$MGPF = $env:MOBILE_GAME_PRODUCT_FORGE; if (-not $MGPF) { $MGPF = $env:CLAUDE_PLUGIN_ROOT }
if (-not $MGPF) {
  $cands = @("$env:USERPROFILE\.claude\skills\mobile-game-product-forge", "$env:USERPROFILE\.codex\skills\mobile-game-product-forge") + @(Get-ChildItem "$env:USERPROFILE\.claude\plugins\cache\*\mobile-game-product-forge\*" -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | ForEach-Object FullName)
  $MGPF = $cands | Where-Object { Test-Path "$_\scripts\check-stage-gate.py" } | Select-Object -First 1
}
python "$MGPF\scripts\lint-prd.py" ...
```

定位顺序（四级）：`MOBILE_GAME_PRODUCT_FORGE` 环境变量（逃生舱；Windows 经 `scripts/install.ps1` 自动写入）→ `CLAUDE_PLUGIN_ROOT`（插件运行时若提供）→ `~/.claude/skills/`、`~/.codex/skills/`（脚本安装轨）→ `~/.claude/plugins/cache/*/mobile-game-product-forge/<版本>/`（插件安装轨）；候选目录须真实含 `scripts/check-stage-gate.py` 才采用，防悬空软链。Windows 上 `python3` 常缺失，bash 形式用 `command -v python3 || command -v python` 双探测。`validate.sh` #8 校验 SKILL.md 引用的 `scripts/*` 存在。

### 跨平台可执行

- 表达不依赖 Claude 独有语义；Codex / Cursor 读到同一 `SKILL.md` 须能执行。
- `agents/openai.yaml` 与 `SKILL.md` frontmatter 描述的能力保持一致。

## 7. 新增 / 删除 / 重命名子 Skill 同步清单

新增子 Skill `skills/<name>/`：

1. 建 `SKILL.md` + `agents/openai.yaml`，按是否应被自然语言自动路由显式选择 `allow_implicit_invocation`；正式内容写作/交付类入口默认考虑 explicit-only，禁止机械设 true。
2. 不在 `.claude-plugin/plugin.json` 逐项追加子 Skill。清单保持 `skills: ["./"]` 显式注册根编排器；Claude Code 按默认 `skills/` 目录发现子 Skill。新增目录由 `validate.sh` #5/#5b 与回归夹具检查。
3. `install-profiles/core.yaml` 与 `core-life-reboots.yaml` 的 `source_files` 追加 `skills/<name>/`（两份清单须一致，`validate.sh` #12）。
4. 主编排器 `SKILL.md`「子 Skill 编排」表登记阶段与触发（`validate.sh` #7b 校验路由）。
5. `README.md`「包含的 Skill」表 + 本 `AGENTS.md` §1 速查登记（`validate.sh` #7 校验两文档提及）。
6. 如新增阶段，同步 `references/workflow.md` 阶段表。
7. 检查相关校验脚本是否需扩展；`CHANGELOG.md` 追加 `[Unreleased]` 条目。
8. 跑 `bash scripts/validate.sh`。

删除 / 重命名子 Skill：反向执行上述全部步骤，**不得残留** `install-profiles` / 根路由表 / 路由回归夹具 / `README` / `AGENTS` / `workflow.md` 引用；`plugin.json` 仍保持根入口 `skills: ["./"]`，不维护子 Skill 清单（`validate.sh` #5b / #6b / #7 / #7b / #13d 捕获部分残留，其余靠 §11 一致性检查）。

## 8. 文档编写规范

- 可执行表达；明确「必须 / 应当 / 禁止 / 仅当 / 完成后」。
- 明确输入、输出、完成条件；避免空泛目标。
- 不重复 `references/` 已有规范，用相对路径引用。
- 复杂流程用简短编号步骤；真实文件路径与真实命令。
- 不含只适用于 Claude 或只适用于 Codex 的隐含语义。

不建议：「这个 Skill 用来帮助产品经理提升效率。」
建议：「输入结构化或非结构化需求，完成需求澄清后输出需求理解确认文档；未通过确认门不得进入 PRD 阶段。」

## 9. 维护文档同步机制（强制）

每次修改仓库——无论改 Skill / 流程 / 目录 / 脚本 / 安装方式——**必须执行一次文档影响检查**。规则：检查所有相关文档；**只要仓库能力、架构、使用方式或维护方式发生变化，就必须同步对应文档**；不机械改所有文档。

各文档同步条件：

- **README.md**（面向使用者 / 产品 / 开发 / 安装者）：Skill 增删改；能力 / 输入输出 / 适用场景变；主工作流 / 阶段数 / 顺序变；安装 / 升级 / 卸载变；安装档案变；插件订阅变；支持平台变；调用入口变；知识包安装 / 使用变；目录结构用户可感变化；新增 / 废弃能力。只写用户需理解内容，不写 Agent 内部约束。
- **`operation-guide.md`**（详细用户操作文档）：角色分工、阶段操作、阶段门禁、确认方式、产物路径、窄任务入口或多人协作方式变化时同步；`operation-guide.md` 由 setup 复制到目标项目 `docs/mobile-game-product-forge/operation-guide.md`，不复制子 Skill 实现细节。
- **AGENTS.md**（本文件）：职责边界变；Skill 增删改；跨阶段状态变；确认门变；信息优先级变；知识只读边界变；新增目录 / 脚本 / 安装档案 / 校验 / 发布机制；文件职责或状态所有权变；修改流程变；验证矩阵或完成标准变；多 Agent 协作规则变；新增高风险禁止项；版本同步机制变。**不得保留已失效的目录 / 命令 / 架构说明**。
- **子 Skill `SKILL.md`**：功能目标 / 适用场景 / 输入 / 输出 / 前置 / 流程 / 调用其他 Skill / 引用共享规范 / 完成条件 / 禁止 / 异常 / 产物 / 文件路径 任一变化。不得只改脚本 / 模板 / 参考文件而留过期描述。
- **根 `SKILL.md`**：阶段型 Skill 增删改；主路由变；需求处理模式变；确认门变；信息优先级变；跨阶段状态变；共享工作目录变；知识边界变；子 Skill 前置条件变；编排器接口或输出变。
- **`references/`**：多 Skill 共用规则变化优先改此处，而非复制到多个 `SKILL.md`；改后检查引用方 Skill 描述、路由 / 前置、`README`、`AGENTS`、校验脚本是否受影响。
- **`CHANGELOG.md`**：Skill 增删；对外能力变；工作流 / 输入 / 输出 / 产物变；安装 / 升级 / 插件 / 知识包机制变；影响实际使用的重要修复；兼容性 / 校验 / 发布机制变；有迁移影响。纯格式整理 / 错别字 / 不影响行为的内部重构可不写。**无明确发布任务不自动升版本**，但须检查 `[Unreleased]` 段是否需追加（格式以当前 `CHANGELOG.md` 为准）。
- **`install-profiles/`**：Skill 清单或 `source_files` 变。
- **`.claude-plugin/plugin.json`**：根入口注册策略、插件元数据或版本变化。默认 `skills/` 下子 Skill 增删不重复写入清单，但仍须同步 install profiles、根路由、README、AGENTS 与回归夹具。
- **`agents/openai.yaml`**（各 Skill）：interface 元数据或调用策略变。

## 10. 文档影响检查表（每次完成前逐项判断）

```text
[ ] Skill 功能 / 输入 / 输出 / 流程是否变化？
[ ] 主编排器路由或跨阶段状态是否变化？
[ ] 用户安装 / 调用 / 使用方式是否变化？
[ ] 仓库结构或文件职责是否变化？
[ ] 校验 / 版本 / 发布方式是否变化？
[ ] README.md 是否需要更新？
[ ] operation-guide.md 操作文档是否需要更新？
[ ] AGENTS.md 是否需要更新？
[ ] 根目录 SKILL.md 是否需要更新？
[ ] 相关子 Skill 的 SKILL.md 是否需要更新？
[ ] references/ 是否需要更新？
[ ] install-profiles/ 是否需要更新？
[ ] Claude 插件清单是否需要更新？
[ ] agents/openai.yaml 是否需要更新？
[ ] CHANGELOG.md 是否需要更新？
```

判断「无需更新」的文档，须在任务报告中说明原因，不得直接忽略。

## 11. 文档与实现一致性

修改完成后必须核对：

- `README.md` 列出的 Skill = 实际 `skills/` 目录。
- `operation-guide.md` 的操作流程、文件路径与确认门 = 根 `SKILL.md`、`references/workflow.md`、`references/stage-gates.md` 和 `references/templates.md` 的当前契约。
- `AGENTS.md` 描述的架构 = 实际目录。
- 根 `SKILL.md` 路由 = 实际 Skill（`validate.sh` #7b）。
- 子 Skill 输入输出描述 = 实际执行规则。
- `install-profiles/` `source_files` = 真实文件（`validate.sh` #6b）。
- `plugin.json` Skill 路径 = 真实目录（`validate.sh` #5 / #5b）。
- `agents/openai.yaml` 元数据 = 当前能力。
- 校验命令 = 真实脚本。
- 版本描述 = 真实版本源（`validate.sh` #3）。
- 已删 / 重命名功能无残留引用。

禁止：实现变但文档仍写旧行为；新增 Skill 未更新注册；删文件后文档仍引旧路径；改工作流只更新一个 Skill；改校验脚本后 `AGENTS.md` 仍要求旧命令；改安装结构未更新档案；为让校验通过删文档检查规则；未改文档却声称已同步；未跑校验却声称已通过。

## 12. 验证矩阵（按改动类型，命令须真实存在）

| 改动类型 | 必跑 |
|---|---|
| 任意改动（完成前，进 §10 判断之前） | `bash scripts/doc-impact-check.sh`（建议预检，非阻断，退出码恒 0；给出 §9 文档同步建议 + §10 检查表自动标注；随后按下方矩阵跑对应强制命令） |
| 任意 Skill（`SKILL.md` / `agents/openai.yaml`） | `bash scripts/validate.sh` |
| 主编排器 / 跨阶段状态 / 确认门 / 信息优先级 / 路由 | `bash scripts/validate.sh` + 人工核对边界（§3） |
| P0 架构（安装档案 / 知识包边界 / setup 可发现性） | `bash scripts/validate.sh`（首步含 P0）；或 `bash scripts/validate-p0-architecture.sh` |
| PRD 规范 / 图形 / 模板（`references/prd-spec.md`、`prd-diagrams.md`、`templates.md`） | `python3 scripts/lint-prd.py fixtures/valid-prd.md`（退出 0）+ `python3 scripts/lint-prd.py fixtures/invalid-prd.md`（退出 1）；改了夹具须同步 |
| 安装档案（`install-profiles/`） | `bash scripts/validate.sh`（#6 / #6b / #12 / #13）+ 冒烟：`bash scripts/install.sh --agent claude --profile core-life-reboots --target /tmp/forge-smoke-target`（Windows 冒烟：`powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent claude -Profile core-life-reboots -Target <tmp>`） |
| 插件清单（`plugin.json`） | `bash scripts/validate.sh`（#5 / #5b / #13）+ `python3 -c "import json;json.load(open('.claude-plugin/plugin.json'))"`；本机有 Claude CLI 时再跑 `claude plugin validate .` |
| `agents/openai.yaml` / Skill description 路由 | `bash scripts/validate.sh`（#2b 调用策略 + #14 YAML 结构 + 路由回归夹具）；人工确认宽泛新需求进根编排器，子 Skill 只匹配委派或明确窄任务 |
| Python 脚本（`lint-prd.py`） | `python3 -m py_compile scripts/lint-prd.py` + 夹具自测（见上） |
| 评审报告版本头 lint（`lint-review-report.py`） | `python3 -m py_compile scripts/lint-review-report.py` + `python3 scripts/lint-review-report.py --self-test` |
| 阶段门禁脚本 | `python3 -m py_compile scripts/check-stage-gate.py scripts/stage_gate_core.py scripts/prototype_meta.py scripts/stage_gate_selftest.py` + `python3 scripts/check-stage-gate.py --self-test` |
| Shell 脚本（`install.sh` / `validate*.sh` / `doc-impact-check.sh`） | `bash -n scripts/install.sh`、`bash -n scripts/validate.sh`、`bash -n scripts/validate-p0-architecture.sh`、`bash -n scripts/doc-impact-check.sh` + `bash scripts/validate.sh` |
| PowerShell 脚本（`install.ps1`） | 本机有 pwsh 时 `pwsh -NoProfile -Command "&{ . ./scripts/install.ps1 -Agent claude -Target <tmp> }"`；无 pwsh 时标「未验证」并请 Windows 协作者手工冒烟（Gitee 无 CI 兜底） |
| 版本字段 | `bash scripts/validate.sh`（#3） |
| 发布前全量 | `bash scripts/release.sh <新版本>`（内含 validate.sh 全量 + 版本同步 + CHANGELOG 断言 + `claude plugin validate .`）；pre-push 钩子（`scripts/githooks/pre-push`）在推送时兜底跑 validate + install.sh 冒烟；Windows 侧无 CI，install.ps1 改动请 Windows 协作者手工冒烟 |

**只有实际执行过的校验才能报告为通过。** 未执行的标「未验证」。

## 13. 版本与发布规则

- **唯一版本源**：`package.json` `version`。
- 须同步：根 `SKILL.md` 的 `当前 Skill 版本` 与 `.claude-plugin/plugin.json` `version`；二者和 `package.json` 由 `validate.sh` #3 校验。正式文档的紧凑生成记录使用发布版本，不另设第二个硬编码版本字段。
- 子 Skill **不携带独立版本**，用占位「随包发布，见 package.json」（`validate.sh` #3b 禁止硬编码）。
- 知识包 `knowledge-packs/*/PACK.md` 维护**独立包版本**，不与 Skill 版本绑定。
- **无明确发布任务不自动升版本**。升版本一律走 `bash scripts/release.sh <新版本>`（同步 `package.json` / `plugin.json` / 根 `SKILL.md` 三处 + 断言 CHANGELOG + 全量校验）；不手工在多处改。
- **发版 = bump 版本**：插件用户的自动升级只认 `plugin.json` 的 version（版本解析 plugin.json → marketplace 条目 → commit SHA；本仓 marketplace 条目刻意不写 version）。只推 commit 不 bump，已安装用户永远不会升级。
- 每次发布在 `CHANGELOG.md` 顶部新增条目；`[Unreleased]` 积累未发布变更，发版前转正为 `## [x.y.z] - 日期`（release.sh 会断言）。
- 发布前完成 §12「发布前全量」校验。

## 14. 多 Agent 协作规则（Claude Code / Codex / Cursor 通用）

- 修改前确认工作区状态（`git status`）；不覆盖其他 Agent 未提交修改。
- 不重置 / 清理 / 回滚未知变更；不用破坏性 Git 命令处理不理解的变更。
- 一个任务尽量限定明确文件范围；改共享核心文件（`SKILL.md`、`references/*`、`scripts/validate.sh`、`install-profiles/*`、`plugin.json`）前检查是否并行修改。
- 不删除自己不理解的配置。
- 完成后输出：修改文件、修改原因、验证结果、剩余风险；只完成部分须明确说明。
- **不得声称执行过未实际执行的校验；不得声称更新过未实际更新的文档。**
- 仓库内不携带项目级 `CLAUDE.md` / `.cursor/rules` / `.github/copilot-instructions.md` / `GEMINI.md`；setup 也不写入这些规则文件。仅 `install.sh --agent cursor --target <项目>` 在用户明确安装 Cursor 集成时写目标项目 `.cursor/rules/mobile-game-product-forge.mdc`。维护本仓库不得在根新增这些文件。
- 运行时多 Agent 协议（协调 Agent 唯一状态所有者、共享工作目录、评审 Agent 只返回问题）见 [SKILL.md](SKILL.md)「多 Agent 统一协议」。

## 15. 禁止事项

- 把仓库误判为游戏代码项目；修改目标游戏业务代码。
- 声称 setup 会写入目标项目 `AGENTS.md`、`CLAUDE.md` 或 `.cursor/` 规则；setup 只写项目目录、知识、操作指南和非密钥发布配置。
- 破坏主编排器 / 子 Skill 职责边界；让子 Skill 创建或修改跨阶段状态；阶段执行细节堆入主编排器。
- 自动修改项目知识事实（`knowledge-packs/`）；把项目敏感知识写进 core 或通用插件包。
- 把 `history/` 当当前规范。
- 改安装路径不更新 `install-profiles/`；新增 Skill 不更新注册（`plugin.json` / `install-profiles` / 路由 / `README` / `AGENTS`）；删 Skill 留残留。
- 改版本不保持一致；多处手工改版本。
- 在 `SKILL.md` 写裸 `python3 scripts/xxx.py`（须用 `MGPF` 片段）。
- 为「简化」或为校验通过而删 / 弱化三个产品确认点、原型豁免批准证据、PRD/交付分离、知识只读边界、安装边界、证据回读或高风险深读约束。
- 为适配单一 Agent 破坏跨平台能力。
- 对与任务无关的文件大规模格式化。
- 未跑校验却声称通过；未做文档影响检查就结束任务；未实际更新文档却声称已同步。

## 16. 完成定义（未达此标准 = 任务未完成）

1. 功能 / 文档修改已完成。
2. 相关校验已**实际执行**（按 §12 矩阵）。
3. 已完成 §10 文档影响检查表。
4. 所有受影响维护文档已同步。
5. 文档与真实实现无已知冲突（§11）。
6. 结果明确列出已更新 / 未更新的维护文档及原因。
7. 未实际执行的检查明确标「未验证」。
8. 未解决风险明确列出。
