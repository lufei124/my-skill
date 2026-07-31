# 领域预设：game-mud（游戏/MUD 子系统）

本预设把原 `subsystem-research-workflow` skill 的精华迁入通用 `research-workflow` 框架。适用于游戏/MUD 项目中的子系统调研（任务系统、战斗系统、社交系统、经济系统、门派系统、交通系统等）。

使用方式：`create_research_skeleton.py <topic> --preset game-mud`，或在 grilling 阶段 0 选定本预设。

## 角色特化

通用角色原型（见 `team-roles.md`）在本预设中特化为以下 11 人团队：

| 通用原型 | game-mud 特化角色 | 产出文件 |
|---|---|---|
| 资料考古员 | LPC 源码考古员 | `01-raw-findings/source-inventory.md` |
| 场景切片员 | 玩法切片策划 | `01-raw-findings/usage-slices.md`、`02-perspectives/actor-stories.md`（原 `player-stories.md`） |
| 机制抽象师 | 任务机制设计师 | `01-raw-findings/mechanisms.md`、`02-perspectives/system-stories.md` |
| 方案设计师 | 引擎架构师（2+ 人） | `03-design-options/abstraction-options.md`、`03-design-options/extension-surface.md`（原 `ugc-surface.md`） |
| 创作者视角评审员 | UGC 游戏专家 | `03-design-options/creator-perspective.md`、`02-perspectives/operator-stories.md` |
| 横向验证员 | 横向对比验证员 | `04-redteam-review/cross-check-report.md` |
| 现代实践评审员 | 现代任务玩法设计师 | `03-design-options/modern-practice-review.md`（原 `modern-design-review.md`）、`04-redteam-review/modern-challenges.md` |
| 体验与留存评审员 | 玩家心理与留存专家 | `03-design-options/experience-review.md`（原 `player-psychology.md`）、`04-redteam-review/experience-risks.md` |
| 价值与增长评审员 | 商业化与增长专家 | `03-design-options/value-review.md`（原 `commercialization.md`）、`04-redteam-review/value-risks.md`（原 `commercial-risks.md`） |

终审组（评审委员会 5 人）：玩法切片策划、引擎架构师 1 人、UGC 游戏专家、现代任务玩法设计师、商业化与增长专家 → `05-synthesis/final-report.md`。

## 产出层级映射

通用 6 层保持不变，文件命名按上表特化。与原 `subsystem-research-workflow` 的对应关系：

- `01-raw-findings/` — 同名，文件同义。
- `02-user-stories/` → `02-perspectives/`：`player-stories.md` → `actor-stories.md`；`system-stories.md` 同名；`operator-stories.md` 同名。
- `03-engine-insights/` → `03-design-options/`：`abstraction-options.md` 同名；`ugc-surface.md` → `extension-surface.md`；`creator-perspective.md` 同名；`modern-design-review.md` → `modern-practice-review.md`；`player-psychology.md` → `experience-review.md`；`commercialization.md` → `value-review.md`。
- `04-redteam-review/` — 同层；`commercial-risks.md` → `value-risks.md`，其余同名。
- `05-synthesis/` — 同名。

## grilling 追加问题

选定本预设后，在通用 grilling 问题（见 `grilling-questions.md`）基础上追加确认：

- **现代视角权重**：现代玩法设计、玩家心理、商业化三个视角，哪个权重最高？（推荐至少包含现代玩法设计 + 一个风险视角）
- **engine 抽象边界**：如果目标是 engine 抽象，本次是否只产出设计输入、不直接输出接口契约？（推荐是）
- **User Stories 视角**：玩家视角必选，是否还需要巫师/运营视角、系统/NPC 自动触发视角？（推荐三层都覆盖）

## brief 增量

`--preset game-mud` 时，`create_research_skeleton.py` 会把 `references/domain-presets/game-mud.brief.md` 的内容注入到 `00-brief/brief.md` 的目标与范围章节，强调：基于当前仓库一手源码、引入现代游戏设计/玩家心理/商业化/UGC 扩展视角、本次止步于设计输入层不输出 engine 接口契约。

## 批判性视角建议

- 现代实践对照：对标当前主流 MMO / 开放世界 / 手游设计。
- 体验与留存：动机心理学、留存曲线、心流节奏、社交压力。
- 价值与增长：付费设计、UGC 创作者经济、题材包消费、用户增长。
