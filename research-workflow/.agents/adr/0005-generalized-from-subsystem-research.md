# ADR-0005：从 subsystem-research-workflow 通用化而来

状态：已采纳

## 背景

原 `subsystem-research-workflow` skill 专为游戏/MUD 子系统调研设计：内置 11 人游戏团队、user-stories/engine-insights 分层、现代/玩家心理/商业化三视角。但它抽出的方法论（grilling 对齐 + 编号目录 + 三阶段多 Agent Workflow + 红队 + 评审委员会汇总）其实是领域无关的。当要调研非游戏对象（认证模块、ETL 管道、缓存层）时，要么硬套游戏视角，要么无 skill 可用。

## 决策

新建 `research-workflow` 作为通用化版本，抽取原 skill 的方法论骨架（grilling + 编号目录 + 三阶段 Workflow + 红队 + 评审委员会），去除游戏/MUD 硬编码，改为通用核心 + 可插拔领域预设（见 [ADR-0004](0004-pluggable-domain-presets.md)）。原 `subsystem-research-workflow/` 保留不动，仍可作为游戏/MUD 专用 skill 直接使用；其精华（11 人游戏团队、分层、三视角）迁入 `references/domain-presets/game-mud.md` + `game-mud.brief.md`，通过 `--preset game-mud` 复用。通用软件模块/系统/流程调研直接用本 skill（选 `software-system` 或 `none`）。

## 备选方案

- 就地改造 `subsystem-research-workflow` 为通用：被否，破坏既有游戏专用用户的使用与既有 eval，且通用化会稀释游戏领域的开箱即用度。
- 删除原 skill、只留通用版：被否，丢失游戏专用入口，已有用户被迫迁移。
- 把通用核心做成原 skill 的「基类」、原 skill 继承：被否，skill 无继承机制，强行模拟只会引入耦合。
- 通用版不内置 game-mud 预设、让用户从原 skill 自行搬运：被否，迁移成本转嫁给用户，且两份 skill 的 game-mud 内容会立刻漂移。

## 后果

- 两个 skill 并存：本 skill 通用 + 原游戏专用 skill 保留。`README.md`「与 subsystem-research-workflow 的关系」一节明确这一关系。
- `game-mud` 预设是原 skill 精华的镜像，后续原 skill 若演进，需评估是否同步到预设（手动同步，不做自动）。
- `evals/evals.json` 既含软件模块 eval（auth-module）、通用 eval（data-pipeline），也含游戏 eval（combat-system 用 game-mud 预设），覆盖三类的回归。
- 本 ADR 记录「为何有两份相似 skill」这一令新贡献者意外的历史决策。
