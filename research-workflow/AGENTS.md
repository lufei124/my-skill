# AGENTS.md

本文件面向在本仓库内**维护 `research-workflow` Skill**的 Agent（Claude Code / OpenAI Codex / Cursor）。它规定 Agent 如何安全修改本仓库：不是使用说明（使用见 [README.md](README.md) 与 [operation-guide.md](operation-guide.md)），不是调研协议正文（见 [SKILL.md](SKILL.md)），也不复述通用参考（见 `references/`）。

## 1. 仓库身份与 Agent 职责

- 本仓库是**可安装的 Skill 框架**，不是某个被调研的目标项目。维护对象是 Skill 正文（`SKILL.md`）、骨架初始化器（`scripts/create_research_skeleton.py`）、评分器（`scripts/grade_research_init.py`）、benchmark 汇总（`scripts/aggregate_benchmark.py`）、领域预设与共享参考（`references/`）、eval（`evals/evals.json`）、安装与升级机制、校验脚本；**不得修改被调研项目的业务代码**。
- 仓库根即本 Skill 主体（`SKILL.md` + `agents/openai.yaml` + `references/` + `scripts/` + `evals/`）。本 skill 是**单编排器**：仓库内**无子 skill**。
- 本规范适用于 Claude Code、Codex、Cursor 等仓库维护 Agent，表达不依赖某一工具独有功能。

Agent 主要职责：维护 Skill 正文与调研协议（grilling 对齐 + 三阶段 Workflow）；维护 `references/` 通用参考与 `references/domain-presets/` 领域预设；维护初始化器与评分器；维护 eval 与 benchmark；维护安装与升级机制；维护校验脚本；保证三平台（Claude Code / Codex / Cursor）一致；保证实现、文档与配置同步。

### 仓库结构速查（role-map；完整目录树见 README.md「内容」）

| 路径 | 角色 | 可改 |
|---|---|---|
| `SKILL.md` | 调研协议正文：何时使用、阶段 0-4 执行流程、默认目录结构、约束原则、团队角色、领域预设、Workflow 模板、示例 | Agent |
| `agents/openai.yaml` | interface 元数据 + 调用策略 | Agent |
| `references/` | 通用共享参考：`grilling-questions.md` / `team-roles.md` / `output-structure.md` / `workflow-template.md`（领域无关） | Agent |
| `references/domain-presets/` | 领域预设：`<preset>.md`（给人读）+ `<preset>.brief.md`（给脚本注入 brief 增量），成对存在 | Agent |
| `scripts/create_research_skeleton.py` | 初始化器：创建 `.scratch/research/NN-topic/` 6 层骨架 + brief 总则，按 `--preset` 注入领域 brief 增量 | Agent |
| `scripts/grade_research_init.py` | 评分器：按 eval 断言检查初始化产出（目录结构 / brief / grilling 对齐 / 多 Agent / 批判视角 / 不过早深入源码） | Agent |
| `scripts/aggregate_benchmark.py` | benchmark 汇总：聚合 with/without_skill 的 grading + timing | Agent |
| `evals/evals.json` | eval 定义：prompt / expected_output / perspective_keywords / expected_subdirs / assertions | Agent |
| `.claude-plugin/plugin.json` | Claude Code 插件清单；`skills: ["./"]` 显式登记根编排器 | Agent |
| `.claude-plugin/marketplace.json` | 同仓自托 marketplace，单插件条目 `source: "./"`，不写 version | Agent |
| `.agents/adr/` | 架构决策记录，追加式，只记 why + 备选 | Agent（仅追加） |
| `scripts/` | 安装、维护校验脚本：`validate.sh`（校验器）、`install.sh`/`install.ps1`（安装器）、`release.sh`（发版）、`doc-impact-check.sh`（文档影响预检）、`githooks/pre-push`（推送门禁） | Agent |
| `install-profiles/core.yaml` | 安装档案 `source_files` 校验清单 | Agent |
| `package.json` | 唯一版本源 | Agent（仅发版） |
| `operation-guide.md` / `install-guide.md` | 面向使用者的日常操作 / 安装升级指南 | Agent |
| `README.md` / `CHANGELOG.md` / `AGENTS.md` | 用户文档 / 变更记录 / 本维护手册 | Agent |

## 2. 指令与信息优先级（冲突时按此处理）

仓库维护冲突按以下顺序裁决（高 -> 低）：

1. 用户当前明确要求
2. 本次任务的验收标准
3. 本 `AGENTS.md`
4. 实际代码、脚本与校验规则体现的真实契约（`scripts/validate.sh`、`create_research_skeleton.py` / `grade_research_init.py` 的实际断言）
5. `references/` 共享参考
6. `.agents/adr/`（历史决策理由，不构成当前可变规则）

规则：

- **文档与脚本冲突**：脚本是「当前实际能通过校验的契约」的事实来源。文档（`AGENTS.md` / `references/`）与脚本不一致时，先报告冲突（来源、影响、建议），判断哪一方反映既定规则--`AGENTS.md` 是维护规则的权威表述，脚本是其实现--再修落后的一方，**不静默迁就任一方**。
- `.agents/adr/` 只记「为何如此决策」，不复述可变规则；可变规则改了不需同步 ADR，除非决策本身被推翻（则新增 superseding ADR）。
- 不得自行覆盖存在冲突的既定决策；发现冲突必须报告，不静默选择。

## 3. 架构边界与状态所有权（不可破坏）

| 层 | 持有 | 禁止 |
|---|---|---|
| `SKILL.md` | 调研协议：阶段 0-4 流程、默认目录结构、约束原则 | 把脚本实现细节（序号算法、占位符）堆入协议正文 |
| `scripts/create_research_skeleton.py` | 初始化器逻辑：序号计算、6 层创建、brief 模板渲染、preset 增量注入 | 内嵌领域预设说明文本（预设说明在 `references/domain-presets/`） |
| `references/domain-presets/` | 领域预设说明 + brief 增量（成对） | 脚本内嵌 brief 副本与之并存；只加 `.md` 不加 `.brief.md`（反之亦然） |
| `references/` | 通用操作参考 | 把同一规则复制到 `SKILL.md` 与 `references/` |
| `evals/evals.json` | eval 断言定义 | 评分器里硬编码断言名而不登记进 `ASSERTION_CHECKS` |
| `install-profiles/` | 安装档案 `source_files` 校验清单 | 手工同步清单（由 `validate.sh` 校验） |
| `.claude-plugin/plugin.json` | 插件清单（根入口 `./`） | 省略根入口；逐项登记造成注册漂移 |

不可破坏的边界：

- **grilling 强制不可跳过**：阶段 0 是调研正确性的前提，不得为「快速出结果」而绕过（见 [ADR-0001](.agents/adr/0001-grilling-first-mandatory.md)）。
- **编号主题目录 + 6 层结构**是产出的机械可校验约定（见 [ADR-0002](.agents/adr/0002-numbered-topic-six-layer-dir.md)），评分器据此断言。
- **三阶段 Workflow**（并行初稿 -> 红队 -> 评审委员会）是执行方法论骨架（见 [ADR-0003](.agents/adr/0003-three-phase-workflow.md)），不得删去红队或评审阶段。
- **通用核心 + 可插拔预设**：通用正文不混入领域硬编码；领域差异只落在 `references/domain-presets/`（见 [ADR-0004](.agents/adr/0004-pluggable-domain-presets.md)）。每个 `<preset>.md` 必须配对 `<preset>.brief.md`，`validate.sh` 校验配对完整且与 `PRESETS` 字典一致。
- **默认不自动 commit**：由用户决定是否提交，不得擅自 commit/push。

## 4. 修改前强制工作流程

修改任意文件前必须：

1. 读目标文件 + 上下游（初始化器 <-> `references/domain-presets/` brief 增量 <-> `SKILL.md`/`references/` 描述；评分器 <-> `evals/evals.json` 断言）。
2. 读约束：本 `AGENTS.md` + 相关 `references/` + 相关 ADR。
3. 搜相同/相关规则（`grep -rn` 仓库内是否已有该规则），避免重复维护。
4. 判层：改动应落 协议正文 / 初始化器 / 评分器 / 通用参考 / 领域预设 / eval / 安装配置 / 插件配置 / 校验脚本 / 用户文档 中的哪一层。
5. 评影响：是否影响 `references/`、`create_research_skeleton.py`、`grade_research_init.py`、`evals/evals.json`、`SKILL.md`、`install-profiles/`、`plugin.json`、`agents/openai.yaml`、校验脚本、版本、`README.md`、`AGENTS.md`、`CHANGELOG.md`。
6. 定验证：按 §11 验证矩阵选定要跑的命令。
7. 执行修改。
8. 改 **完后、进 §9 文档影响人工/Agent 判断之前**，先跑 `bash scripts/doc-impact-check.sh`，拿机器可判定的「改动路径 -> §8 文档同步建议」做参考；其余项由人工/Agent 判断（脚本建议、不阻断、退出码恒 0）。再依判断改受影响文档。

禁止只看到一个文件的问题就立即局部修改而不查上下游。

## 5. 修改原则

- 优先最小改动；不做与当前任务无关的重构。
- 不随意重命名目录、文件；不删除未知配置。
- 不覆盖其他 Agent 未提交的修改；不用破坏性 Git 命令（`git reset --hard`、`git clean -fd`、`git push --force`）处理未知变更。
- 不静默改变已有输入 / 输出 / 工作流契约。
- 不为适配单一 Agent 破坏跨平台兼容。
- 不把同一规则复制到多个文件；不把说明性文档当唯一事实，必须核对真实实现与校验脚本。
- **不让校验通过而削弱保护规则**（尤其不得为绕过断言而删 grilling/红队/评审要求）。

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

- 本 skill 是单编排器，承担「grilling 对齐 + 多 Agent 调研 Workflow」一类职责，不再拆子 skill。

### 必须有

- `SKILL.md`：frontmatter（`name`、`description`）+ 正文。
- `agents/openai.yaml`：`interface`（display_name / short_description / default_prompt）+ `policy.allow_implicit_invocation`（显式声明，不靠省略）。

### SKILL.md 必须描述

- 何时使用、阶段 0-4 执行流程、默认目录结构、约束原则、团队角色、领域预设、Workflow 模板、示例、禁止事项。
- 「当前 Skill 版本」一行（由 `validate.sh` 校验与 `package.json` 一致）。
- 引用通用参考与领域预设用相对路径 `references/<file>.md`。

### 领域预设维护（`references/domain-presets/`）

- 新增预设：同时加 `<name>.md`（给人读的领域说明：角色特化、层级映射、追加 grilling 问题）与 `<name>.brief.md`（给脚本注入 brief 的增量片段），二者**成对**。
- 在 `create_research_skeleton.py` 的 `PRESETS` 字典登记新预设（`subdirs` + `brief_include`）。
- 在 `SKILL.md` / `README.md` 的预设列表同步登记；若需 eval 回归，在 `evals/evals.json` 加 eval。
- `validate.sh` 校验「PRESETS 键集合 = domain-presets `.md` 基名集合 = 配对完整」，三者不一致即校验失败。

### 通用参考维护（`references/`）

- 通用参考（grilling-questions / team-roles / output-structure / workflow-template）领域无关，改时不得引入特定领域硬编码。
- 改后检查 `SKILL.md`、`README.md`、`operation-guide.md` 是否仍与之相符。

### 跨平台可执行

- 表达不依赖 Claude 独有语义；Codex / Cursor 读到同一 `SKILL.md` 须能执行。
- `agents/openai.yaml` 与 `SKILL.md` frontmatter 描述的能力保持一致。
- Python 脚本用 Python 3.9 兼容语法（无 `match`、无 `X | Y` 联合类型），`from __future__ import annotations` + `typing` 模块。注：`grade_research_init.py` 既有 `Path | None` 注解（3.10+）属历史遗留，仅在 `from __future__ import annotations` 下作为注解安全（运行时不求值），新增代码避免沿用该写法。

## 7. 新增 / 删除 / 修改参考或预设文件同步清单

新增领域预设：

1. 在 `references/domain-presets/` 加 `<name>.md` + `<name>.brief.md`（成对）。
2. 在 `create_research_skeleton.py` 的 `PRESETS` 登记。
3. 在 `SKILL.md`「领域预设」、`README.md` 内容表与「如何选预设」同步登记。
4. 若需 eval 回归，在 `evals/evals.json` 加 eval（含 perspective_keywords / expected_subdirs / assertions）。
5. `install-profiles/core.yaml` 的 `source_files` 已用目录级登记（`references/`），无需逐文件改。
6. 跑 `bash scripts/validate.sh`（含预设配对、PRESETS 一致、`--self-test` 对新 preset 跑一遍骨架生成）。

新增通用参考文件：

1. 在 `references/` 加 `<file>.md`。
2. 在 `SKILL.md`、`README.md`、`operation-guide.md` 视需要引用。
3. 跑 `bash scripts/validate.sh`（含引用解析校验、README+AGENTS 提及校验）。

删除 / 重命名文件：反向执行，**不得残留** `SKILL.md` / `references/` / `README` / `install-profiles` / `operation-guide` / `evals` 中的引用；`validate.sh` 的链接解析校验会捕获部分残留，其余靠 §10 一致性检查。

新增 / 修改 eval 断言：

1. 在 `evals/evals.json` 的对应 eval 加 `assertion` 条目（`name` + `description`）。
2. 在 `grade_research_init.py` 的 `ASSERTION_CHECKS` 登记该 `name` -> 检查器映射（缺失则评分器报「未知的断言检查器」）。
3. 跑 `grade_research_init.py --self-test` 与 `validate.sh`（含 evals.json 可解析 + 断言名登记校验）。

## 8. 维护文档同步机制（强制）

每次修改仓库--无论改协议 / 参考 / 预设 / 脚本 / 目录 / 安装方式--**必须执行一次文档影响检查**。规则：检查所有相关文档；**只要仓库能力、架构、使用方式或维护方式发生变化，就必须同步对应文档**；不机械改所有文档。

各文档同步条件：

- **README.md**（面向使用者）：参考/预设清单变；骨架命令/选项变；安装 / 升级 / 卸载变；安装档案变；插件订阅变；支持平台变；调用入口变；目录结构用户可感变化；新增 / 废弃能力。只写用户需理解内容，不写 Agent 内部约束。
- **operation-guide.md**（详细用户操作文档）：调研流程、骨架生成操作、产物路径、preset 选择方式、评分/benchmark 用法变化时同步。
- **AGENTS.md**（本文件）：职责边界变；协议硬约束变；信息优先级变；新增目录 / 脚本 / 安装档案 / 校验 / 发布机制；文件职责或状态所有权变；修改流程变；验证矩阵或完成标准变；版本同步机制变。**不得保留已失效的目录 / 命令 / 架构说明**。
- **SKILL.md**：阶段流程、默认目录结构、约束原则、团队角色、领域预设清单、Workflow 模板、示例 任一变化。
- **references/**：通用参考变化优先改此处，而非复制到 `SKILL.md`；改后检查 `SKILL.md`、`README`、`operation-guide` 是否受影响。
- **references/domain-presets/**：领域预设角色/层级映射/追加问题/brief 增量变化；新增/删除预设（成对 + `PRESETS` 登记）。
- **CHANGELOG.md**：对外能力变；调研流程 / 产出 / 输入变；安装 / 升级 / 插件机制变；影响实际使用的重要修复；兼容性 / 校验 / 发布机制变；有迁移影响。纯格式整理 / 错别字可不写。**无明确发布任务不自动升版本**，但须检查 `[Unreleased]` 段是否需追加。
- **evals/evals.json**：eval prompt / 断言 / 期望产出变化；新增/删除 eval。
- **install-profiles/**：source_files 清单变。
- **.claude-plugin/plugin.json** / **marketplace.json**：根入口注册策略、插件元数据或版本变化。
- **agents/openai.yaml**：interface 元数据或调用策略变。

## 9. 文档影响检查表（每次完成前逐项判断）

```text
[ ] 协议规则 / 调研流程 / 产出 / 输入是否变化？
[ ] 用户安装 / 调用 / 使用方式是否变化？
[ ] 仓库结构或文件职责是否变化？
[ ] 校验 / 版本 / 发布方式是否变化？
[ ] README.md 是否需要更新？
[ ] operation-guide.md 操作文档是否需要更新？
[ ] AGENTS.md 是否需要更新？
[ ] SKILL.md 是否需要更新？
[ ] references/ 是否需要更新？
[ ] references/domain-presets/ 是否需要更新？
[ ] evals/evals.json 是否需要更新？
[ ] install-profiles/ 是否需要更新？
[ ] Claude 插件清单是否需要更新？
[ ] agents/openai.yaml 是否需要更新？
[ ] CHANGELOG.md 是否需要更新？
```

判断「无需更新」的文档，须在任务报告中说明原因，不得直接忽略。

## 10. 文档与实现一致性

修改完成后必须核对：

- `README.md` 列出的参考/预设/脚本 = 实际 `references/` + `scripts/` 文件。
- `operation-guide.md` 的操作流程、命令与产物路径 = `SKILL.md`、`references/output-structure.md` 与 `create_research_skeleton.py` 的当前契约。
- `AGENTS.md` 描述的架构 = 实际目录。
- `SKILL.md` 默认目录结构 = `create_research_skeleton.py` 的 `DEFAULT_SUBDIRS` + `references/output-structure.md`。
- `create_research_skeleton.py` 的 `PRESETS` 键集合 = `references/domain-presets/` 的 `.md` 基名集合 = 配对完整（`validate.sh` 校验）。
- `grade_research_init.py` 的 `ASSERTION_CHECKS` 键 ⊇ `evals/evals.json` 中用到的所有 `assertion.name`（`validate.sh` 校验）。
- `install-profiles/` `source_files` = 真实文件（`validate.sh` 校验）。
- `plugin.json` / `marketplace.json` 结构 = 真实目录（`validate.sh` 校验）。
- `agents/openai.yaml` 元数据 = 当前能力。
- 校验命令 = 真实脚本。
- 版本描述 = 真实版本源（`validate.sh` 校验三处一致）。
- 已删 / 重命名功能无残留引用。

禁止：实现变但文档仍写旧行为；改参考只更新一个文档；改校验脚本后 `AGENTS.md` 仍要求旧命令；未跑校验却声称已通过。

## 11. 验证矩阵（按改动类型，命令须真实存在）

| 改动类型 | 必跑 |
|---|---|
| 任意改动（完成前，进 §9 判断之前） | `bash scripts/doc-impact-check.sh`（建议预检，非阻断，退出码恒 0） |
| 任意 skill 文件 | `bash scripts/validate.sh` |
| 协议硬约束 / grilling / 三阶段 Workflow / 信息优先级 | `bash scripts/validate.sh` + 人工核对边界（§3） |
| `references/` 通用参考或 `create_research_skeleton.py` | `bash scripts/validate.sh`（含预设配对、PRESETS 一致校验）+ `python3 scripts/create_research_skeleton.py --self-test` |
| `references/domain-presets/` 领域预设 | `bash scripts/validate.sh` + `python3 scripts/create_research_skeleton.py --self-test`（对新/改 preset 跑骨架生成） |
| `grade_research_init.py` 或 `evals/evals.json` | `bash scripts/validate.sh`（含 evals.json 可解析 + 断言名登记校验）+ `python3 scripts/grade_research_init.py --self-test` |
| 安装档案（`install-profiles/`） | `bash scripts/validate.sh` + 冒烟：`bash scripts/install.sh --agent claude`（用 `CLAUDE_SKILLS_DIR` 指向临时目录，避免污染全局） |
| 插件清单（`plugin.json` / `marketplace.json`） | `bash scripts/validate.sh` + `python3 -c "import json;json.load(open('.claude-plugin/plugin.json'))"`；本机有 Claude CLI 时再跑 `claude plugin validate .` |
| `agents/openai.yaml` | `bash scripts/validate.sh`（YAML 结构校验） |
| Python 脚本（`create_research_skeleton.py` / `grade_research_init.py` / `aggregate_benchmark.py`） | `python3 -m py_compile scripts/<x>.py` + `python3 scripts/<x>.py --self-test`（aggregate_benchmark 无 --self-test，跑 `bash scripts/validate.sh`） |
| Shell 脚本（`install.sh` / `validate.sh` / `doc-impact-check.sh` / `release.sh`） | `bash -n scripts/install.sh` 等 + `bash scripts/validate.sh` |
| PowerShell 脚本（`install.ps1`） | 本机有 pwsh 时冒烟；无 pwsh 时标「未验证」并请 Windows 协作者手工冒烟 |
| 版本字段 | `bash scripts/validate.sh` |
| 发布前全量 | `bash scripts/release.sh <新版本>`（内含 validate.sh 全量 + 版本同步 + CHANGELOG 断言）；pre-push 钩子（`scripts/githooks/pre-push`）在推送时兜底 |

**只有实际执行过的校验才能报告为通过。** 未执行的标「未验证」。

## 12. 版本与发布规则

- **唯一版本源**：`package.json` `version`（见 [ADR-0006](.agents/adr/0006-ship-as-plugin-and-version-sot.md)）。
- 须同步：根 `SKILL.md` 的「当前 Skill 版本」与 `.claude-plugin/plugin.json` `version`；三者和 `package.json` 由 `validate.sh` 校验。
- **无明确发布任务不自动升版本**。升版本一律走 `bash scripts/release.sh <新版本>`（同步 `package.json` / `plugin.json` / 根 `SKILL.md` 三处 + 断言 CHANGELOG + 全量校验）；不手工在多处改。
- **发版 = bump 版本**：插件用户的自动升级只认 `plugin.json` 的 version。只推 commit 不 bump，已安装用户永远不会升级。
- 每次发布在 `CHANGELOG.md` 顶部新增条目；`[Unreleased]` 积累未发布变更，发版前转正为 `## [x.y.z] - 日期`（`release.sh` 会断言）。
- 发布前完成 §11「发布前全量」校验。

## 13. 多 Agent 协作规则（Claude Code / Codex / Cursor 通用）

- 修改前确认工作区状态（`git status`）；不覆盖其他 Agent 未提交修改。
- 不重置 / 清理 / 回滚未知变更；不用破坏性 Git 命令处理不理解的变更。
- 一个任务尽量限定明确文件范围；改共享核心文件（`SKILL.md`、`references/`、`scripts/create_research_skeleton.py`、`scripts/grade_research_init.py`、`evals/evals.json`、`scripts/validate.sh`、`install-profiles/`、`plugin.json`）前检查是否并行修改。
- 不删除自己不理解的配置。
- 完成后输出：修改文件、修改原因、验证结果、剩余风险；只完成部分须明确说明。
- **不得声称执行过未实际执行的校验；不得声称更新过未实际更新的文档。**
- 仓库内不携带项目级 `CLAUDE.md` / `.cursor/rules` / `.github/copilot-instructions.md` / `GEMINI.md`。

## 14. 禁止事项

- 把仓库误判为被调研的目标项目；修改目标项目业务代码。
- 为「快速出结果」绕过 grilling 对齐；删去三阶段 Workflow 中的红队或评审阶段。
- 在 `create_research_skeleton.py` 内嵌领域预设说明文本（说明在 `references/domain-presets/`）。
- 加预设只加 `.md` 不加 `.brief.md`（或反之）；加预设不在 `PRESETS` 登记。
- 在 `evals/evals.json` 用 `assertion.name` 而不在 `ASSERTION_CHECKS` 登记检查器。
- 改版本不保持一致；多处手工改版本。
- 改参考/预设不更新 `SKILL.md` / `README` / `operation-guide` / `install-profiles`；删文件留残留。
- 为「简化」或为校验通过而削弱保护规则（grilling 强制、红队、评审、一手资料约束）。
- 为适配单一 Agent 破坏跨平台能力。
- 对与任务无关的文件大规模格式化。
- 未跑校验却声称通过；未做文档影响检查就结束任务；未实际更新文档却声称已同步。
- 未经用户明确要求擅自 commit / push。

## 15. 完成定义（未达此标准 = 任务未完成）

1. 功能 / 文档修改已完成。
2. 相关校验已**实际执行**（按 §11 矩阵）。
3. 已完成 §9 文档影响检查表。
4. 所有受影响维护文档已同步。
5. 文档与真实实现无已知冲突（§10）。
6. 结果明确列出已更新 / 未更新的维护文档及原因。
7. 未实际执行的检查明确标「未验证」。
8. 未解决风险明确列出。
