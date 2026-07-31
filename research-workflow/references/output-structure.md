# 通用产出目录结构与各层语义

本 skill 默认在 `.scratch/research/NN-topic-name/` 下创建 6 层目录。各层语义领域无关；领域预设可重命名或增删层级（映射关系见对应预设文档）。

```text
.scratch/research/NN-topic-name/
├── 00-brief/
│   └── brief.md                    # 总则：范围、目标、团队、方法、约束
├── 01-raw-findings/                # 一手资料
├── 02-perspectives/                # 视角化分析（stories）
├── 03-design-options/              # 设计可选方案、改进方向、风险警示
├── 04-redteam-review/              # 红队对抗记录
└── 05-synthesis/                   # 评审委员会最终汇总
```

## 各层语义与默认文件

### 00-brief/ — 总则

- `brief.md`：调研总则。包含调研目标、范围边界（纳入/不纳入）、团队与职责、调研方法、输出目录结构、关键约束。由 `create_research_skeleton.py` 生成，可按预设注入增量内容。详见 `scripts/create_research_skeleton.py` 的 brief 模板。

### 01-raw-findings/ — 一手资料

承载基于一手源码/文档/数据的事实性产出。

- `source-inventory.md`：研究对象相关资料清单、调用链、数据结构、关键状态（资料考古员）。
- `usage-slices.md`：4-6 类代表性实例的"使用者视角 + 数据流"切片（场景切片员）。
- `mechanisms.md`：从具体实现抽象的通用机制（机制抽象师）。

### 02-perspectives/ — 视角化分析

承载不同角色视角的 stories（替代原 game-mud skill 的 user-stories 三层）。命名领域中立：

- `actor-stories.md`：使用者/终端对象视角（必选）。
- `system-stories.md`：系统/自动触发视角。
- `operator-stories.md`：运维/创作者/管理员视角。

> 与原 skill 的映射：`player-stories.md` → `actor-stories.md`；`system-stories.md` 同名；`operator-stories.md` 同名（原对应巫师/运营）。

### 03-design-options/ — 设计可选方案

承载面向"重写/抽象/改进"的设计输入与风险警示（替代原 game-mud skill 的 engine-insights 层，去掉 "engine" 字样）。

- `abstraction-options.md`：可复用核心的抽象方案（方案设计师）。
- `extension-surface.md`：扩展/定制层应暴露的最小表面（方案设计师）。
- `creator-perspective.md`：创作者/定制者视角的可扩展性评估（创作者视角评审员）。
- `modern-practice-review.md`：现代实践对照与过时风险（现代实践评审员）。
- `experience-review.md`：体验与留存点评（体验与留存评审员）。
- `value-review.md`：价值与增长评估（价值与增长评审员）。

> 与原 skill 的映射：`abstraction-options.md` / `ugc-surface.md` / `creator-perspective.md` / `modern-design-review.md` / `player-psychology.md` / `commercialization.md` 均直接对应到本层同名或近名文件（见 `domain-presets/game-mud.md` 映射表）。

### 04-redteam-review/ — 红队对抗

承载 Phase 2 红队对抗产出。

- `cross-check-report.md`：横向对比验证（横向验证员）。
- `modern-challenges.md`：现代实践挑战（现代实践评审员）。
- `experience-risks.md`：体验风险挑战（体验与留存评审员）。
- `value-risks.md`：价值风险挑战（价值与增长评审员）。

### 05-synthesis/ — 最终汇总

- `final-report.md`：评审委员会最终报告。结构：执行摘要、范围与方法、现状总览、关键发现、stories 汇总、设计建议、未决问题、附录。

## 层级调整

- 调研目标偏"忠实还原"：可弱化 `03-design-options/`，强化 `01-raw-findings/`。
- 调研目标偏"为重写做抽象输入"：强化 `03-design-options/`。
- 需要额外层级（如 MVP 建议、迁移方案、时代对比）：在 grilling 中确认后新增子目录并在 brief 中记录。
- 领域预设的重命名/映射见 `domain-presets/<preset>.md`。
