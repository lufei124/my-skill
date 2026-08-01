# ADR-0004：通用核心 + 可插拔领域预设

状态：已采纳

## 背景

本 skill 由游戏/MUD 专用的 `subsystem-research-workflow` 通用化而来（见 [ADR-0005](0005-generalized-from-subsystem-research.md)）。若把游戏团队角色、产出层级映射、专属 grilling 问题硬编码在正文里，则调研软件模块/数据流程时要么被迫套用无关的游戏视角，要么得 fork 一份 skill。反之，若做成完全空白、每次从零配，又丢失了开箱即用的领域经验。

## 决策

采用**通用核心 + 可插拔领域预设**：`SKILL.md` / `references/`（grilling-questions / team-roles / output-structure / workflow-template）是领域无关的通用核心；`references/domain-presets/<preset>.md` 是给人读的领域说明（角色特化、层级映射、追加 grilling 问题），`references/domain-presets/<preset>.brief.md` 是给脚本读的 brief 增量片段。`create_research_skeleton.py` 的 `PRESETS` 字典登记可用预设，`--preset` 注入对应 brief 增量到 `00-brief/brief.md`。默认 `none`（纯通用），内置 `game-mud` 与 `software-system`。每个 `<preset>.md` 必须配对一个 `<preset>.brief.md`（反之亦然），由 `validate.sh` 校验。

## 备选方案

- 保留游戏硬编码、另起一个软件 skill：被否，双份维护通用方法论（grilling + 编号目录 + 三阶段 Workflow），漂移不可避免。
- 完全空白、无预设：被否，丢失开箱即用的领域经验，每次重复 grilling 从零配角色。
- 预设只给说明文档、不注入 brief：被否，说明文档给人读但不进产物，brief 增量能让目标/范围章节自动带上领域约束，减少遗漏。
- 把 brief 增量内嵌在 `<preset>.md` 里用标记分隔：被否，人读与脚本读混在一个文件，脚本解析脆弱；拆成 `.md` + `.brief.md` 双文件职责清晰。

## 后果

- 新增领域预设：在 `domain-presets/` 加 `<name>.md` + `<name>.brief.md`，在 `create_research_skeleton.py` 的 `PRESETS` 登记，在 `evals/evals.json`（若需）加 eval，`SKILL.md` / `README.md` 列表同步。`validate.sh` 校验「PRESETS 键 = domain-presets 文件集合 = 配对完整」三者一致。
- 通用核心改动只动 `SKILL.md` / `references/` 通用文件，不触碰预设。
- 预设可重命名或增删 6 层中的层级，映射关系在该预设文档内说明，通用默认仍 6 层。
- `--self-test` 对每个 preset 都跑一遍骨架生成，确保 brief 增量路径解析正确、不残留占位符。
