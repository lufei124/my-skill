# Research Workflow Skill

一个可移植、领域无关的 skill，用于对项目中的某个子系统、模块或流程进行深度调研与设计批判。先强制对齐目标，再组织多 Agent 虚拟团队并行产出结构化文档。

## 内容

- `SKILL.md`：Agent 行为守则（何时使用 + 阶段 0-4 执行流程）
- `scripts/create_research_skeleton.py`：创建 `.scratch/research/NN-topic/` 骨架，支持 `--preset` 注入领域专属内容
- `scripts/grade_research_init.py`：评分脚本，检查初始化输出是否满足断言
- `scripts/aggregate_benchmark.py`：汇总 benchmark 结果
- `references/grilling-questions.md`：通用 grilling 问题清单
- `references/team-roles.md`：通用默认角色原型
- `references/output-structure.md`：通用产出目录结构与各层语义
- `references/workflow-template.md`：多 Agent Workflow 脚本模板
- `references/domain-presets/`：领域预设（game-mud / software-system）

## 快速开始

```bash
python research-workflow/scripts/create_research_skeleton.py auth-module --preset software-system
```

该命令会在当前项目的 `.scratch/research/` 下创建带序号主题目录：

```text
.scratch/research/01-auth-module/
├── 00-brief/brief.md       # 总则（已按 preset 注入领域增量）
├── 01-raw-findings/
├── 02-perspectives/
├── 03-design-options/
├── 04-redteam-review/
└── 05-synthesis/
```

可用的 `--preset` 值：`game-mud`、`software-system`、`none`（默认，纯通用）。

## 执行流程概览

1. **阶段 0 Grilling 对齐**（强制）：逐一确认范围、目标、领域预设、团队、产出、对抗机制、执行方式、是否 commit。
2. **阶段 1 初始化**：创建编号主题目录与 6 层子目录 + brief 总则。
3. **阶段 2 三阶段 Workflow**：并行初稿 → 红队对抗 → 评审委员会汇总。
4. **阶段 3 补全失败产出**：重跑失败 agent。
5. **阶段 4 最终检查与汇报**：默认不自动 commit。

完整行为守则见 [`SKILL.md`](SKILL.md)。

## 与 subsystem-research-workflow 的关系

本 skill 是 `subsystem-research-workflow` 的**通用化版本**：抽取其"grilling 对齐 + 编号目录 + 三阶段多 Agent Workflow + 红队 + 评审委员会汇总"方法论，去除游戏/MUD 硬编码，改为通用核心 + 领域预设包。

- 原 `subsystem-research-workflow/` 保留不动，仍可作为游戏/MUD 专用 skill 直接使用。
- 其精华（11 人游戏团队、user-stories/engine-insights 分层、现代/玩家心理/商业化视角）已迁入 [`references/domain-presets/game-mud.md`](references/domain-presets/game-mud.md)，通过 `--preset game-mud` 复用。
- 调研通用软件模块/系统/流程时，直接用本 skill（选 `software-system` 或 `none`）。
