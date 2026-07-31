---
name: research-workflow
description: 当用户要求对项目中的某个子系统、模块或流程进行全面研究调研、源码分析、设计评审时使用本 skill。触发词包括"调研 X""全面分析 X""组织团队评审 X""对 X 做深度研究""帮我理解 X 子系统/模块""提取 X 的设计思想""对 X 做源码考古"等。本 skill 先通过 grilling 对齐范围、领域预设、团队、产出与约束，然后组织多 Agent 虚拟调研团队，并行产出原始素材、视角化 stories、设计可选方案、红队对抗与最终汇总报告，保存到 .scratch/research/NN-topic-name/ 下。内置 game-mud 与 software-system 领域预设，也可无预设纯通用运行。默认不自动 commit。
---

# 深度调研工作流（通用）

## 何时使用

本 skill 用于对项目中的单一研究对象（子系统、模块、流程、机制等）进行深度源码/资料调研与设计批判。它通过组织虚拟多角色团队，强制对齐目标后并行产出结构化文档。领域无关 —— 既适用于游戏/MUD 子系统，也适用于软件模块、SaaS 功能、数据流程等。

当用户提到以下任意意图时触发：

- "帮我调研一下 X 系统/模块"
- "全面分析源码中的 X"
- "组织团队评审 X"
- "对 X 做深度研究"
- "X 的设计思想/原始细节"
- "为重写/重构提取 X 的机制"
- "对 X 做源码考古"

## 执行流程

### 阶段 0：Grilling 对齐（强制，不可跳过）

使用 `grilling` skill 或等效连续提问，逐一向用户确认以下决策点，直到达成共享理解。每个问题等待用户回答后再继续。若用户已在初始请求中明确某一点，可跳过该问题，但需在总则中记录。

必须覆盖的决策点：

1. **调研范围**：研究对象的边界（核心机制、代表性实例、与周边系统交互）。
2. **调研目标**：忠实还原 / 为重写或抽象做准备 / 引入现代批判，三者主次。
3. **领域预设**：选用 `game-mud` / `software-system` / `none`（纯通用），并在其基础上增删。
4. **团队角色**：使用默认角色模板还是调整（见 `references/team-roles.md`）。
5. **产出结构**：是否使用默认 6 层目录，是否增减层级。
6. **stories 视角**：actor 视角必选，是否还需要 system / operator 视角。
7. **保存位置**：默认 `.scratch/research/NN-topic-name/`，NN 自动递增。
8. **对抗与评审机制**：模式 A（成对挑战）或模式 B（评审委员会 + 红队，推荐）。
9. **执行方式**：默认 Workflow 多 Agent 并行。
10. **批判性视角范围**：需要哪些外部视角（现代实践 / 体验留存 / 价值增长等），哪些最重要。
11. **资料来源**：仅一手源码 / 是否纳入文档与数据 / 是否允许二手参考。
12. **是否自动 commit**：默认否。

详细问题清单见 `references/grilling-questions.md`。选定领域预设后，预设文档中的"追加问题"也要一并确认（见 `references/domain-presets/`）。

### 阶段 1：初始化目录与总则

1. 扫描 `.scratch/research/` 下已有主题目录，确定下一个序号 NN。
2. 创建 `NN-topic-name/` 目录。
3. 在该目录下创建 6 层子目录与 `00-brief/brief.md` 总则文件。
4. 可以使用 `scripts/create_research_skeleton.py` 自动创建骨架（支持 `--preset` 注入领域专属内容）：

   ```bash
   python research-workflow/scripts/create_research_skeleton.py <topic-name> [--preset game-mud|software-system|none] [--root <research-root>]
   ```

### 阶段 2：多 Agent 并行 Workflow

使用 Workflow 工具启动三阶段调研。Workflow 脚本模板见 `references/workflow-template.md`。

**Phase 1：并行初稿**

- 资料考古组：源码/资料清单、代表性实例切片、机制抽象。
- 抽象与方案组：可复用核心抽象、扩展表面、创作者视角。
- 批判性外部视角组：现代实践对照、体验与留存、价值与增长评估。

**Phase 2：红队对抗**

- 横向对比验证：找出共同模式与特例，验证抽象覆盖度。
- 现代实践挑战：对既有机制与抽象方案提出尖锐质疑。
- 体验风险挑战：识别使用者流失点与必须的保护机制。
- 价值风险挑战：识别成本/收益风险与不可持续陷阱。

**Phase 3：评审委员会汇总**

- 评审委员会审阅所有初稿与红队报告，统一文风、消除矛盾、裁决分歧，生成最终报告。

### 阶段 3：补全失败产出

Workflow 完成后，检查是否有 agent 失败。如有：

1. 单独使用 Agent 工具重新运行失败角色。
2. 如果最终报告已在失败前生成，在报告中补充说明或增加附录引用补全文件。

### 阶段 4：最终检查与汇报

1. 检查所有预期文件是否存在且非空。
2. 检查最终报告是否引用所有关键产出。
3. 向用户汇报：产出结构、文件清单、核心摘要、执行过程中的问题。
4. **仅在用户明确要求时才执行 commit & push**。

## 默认目录结构

```bash
.scratch/research/NN-topic-name/
├── 00-brief/
│   └── brief.md                    # 总则、范围、团队、方法、约束
├── 01-raw-findings/                # 一手资料：源码清单、调用链、数据结构、机制抽象
├── 02-perspectives/                # 视角化分析：actor / system / operator stories
├── 03-design-options/              # 设计可选方案、改进方向、风险警示
├── 04-redteam-review/              # 红队对抗记录
└── 05-synthesis/                   # 评审委员会最终汇总
```

各层语义与默认文件清单见 `references/output-structure.md`。领域预设可重命名或增删层级，映射关系见对应预设文档。

## 约束与原则

- **只基于一手资料**：所有结论必须能从当前仓库源码/文档/数据中找到证据；二手资料仅作参考并显式标注。
- **不做行为等价验证**：不追求逐字复刻原始系统行为。
- **全局与细节兼顾**：既要有宏观脉络，也要有代表性实例细节。
- **批判性外部视角**：对过时、不符合当代实践或不可持续的设计显式标注（具体视角由 grilling 决定）。
- **可复用目录结构**：`.scratch/research/` 按主题编号，方便后续扩展。
- **默认不自动 commit**：由用户决定是否提交。

## 团队角色

默认团队角色原型与职责见 `references/team-roles.md`。可在 grilling 阶段按领域增删。

## 领域预设

为常见领域提供开箱即用的角色清单、产出层级映射、专属 grilling 问题与 brief 增量：

- `references/domain-presets/game-mud.md` —— 游戏/MUD 子系统（迁移自原 `subsystem-research-workflow` 的精华）。
- `references/domain-presets/software-system.md` —— 通用软件模块/系统/流程调研。

**如何选预设**：研究对象是游戏/MUD 子系统选 `game-mud`；是软件模块、系统或数据流程选 `software-system`；不确定或想完全自定义选 `none`，在 grilling 中按需增删角色。

## Workflow 模板

`references/workflow-template.md` 提供可直接改编的 JavaScript Workflow 脚本模板。

## 示例

### 示例 1：非游戏（软件模块）

用户："帮我组织团队深度调研一下这个仓库里的认证鉴权模块，基于一手源码，输出到 .scratch/research/ 下。"

Skill 行为：

1. 进入 grilling，确认认证模块范围、目标、选用 `software-system` 预设、团队侧重（安全/可维护视角加权）、保存位置。
2. 创建 `.scratch/research/01-auth-module/` 与默认 6 层子目录。
3. 启动 Workflow，组织调研团队并行工作。
4. 产出源码清单、机制抽象、视角化 stories、现代实践批判、安全/可维护风险红队报告、最终汇总。
5. 汇报产出结构，不自动 commit。

### 示例 2：游戏/MUD（使用预设）

用户："帮我组织团队深度调研一下战斗系统。"

Skill 行为：

1. 进入 grilling，确认战斗系统范围、选用 `game-mud` 预设、团队、产出、保存位置。
2. 创建 `.scratch/research/02-combat-system/`，brief 注入 game-mud 增量内容。
3. 启动 Workflow，组织调研团队并行工作。
4. 产出源码清单、机制抽象、三层 stories、现代设计批判、玩家心理分析、商业化评估、红队报告、最终汇总。
5. 汇报产出结构，不自动 commit。
