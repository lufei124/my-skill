# ADR-0006: 根编排器位于仓库根，非 skills/ 下

- 状态：已采纳
- 日期：2026-07-25
- 影响：仓库结构（难逆）

## 背景

编排器（持有跨阶段状态、路由子 Skill、执行确认门与版本同步）需选位置。若作为 `skills/` 下一个子 Skill，则失去「用户调用 `mobile-game-product-forge` 时的入口」语义；若根只放 README，则无 model-invoked 入口。

## 决策

根编排器为仓库根 `SKILL.md`。它是用户调用 `mobile-game-product-forge` 时的入口，持有跨阶段状态所有权，且其「文档来源信息」块的 `Skill 版本：` 行是 `validate.sh` 版本一致性的权威读取源。

## 备选方案

- **编排器作为 skills/ 下子 Skill**：失去根入口语义，且版本源须另设，破坏单一版本源不变量。被否。
- **根只放 README，编排器内嵌文档**：无 model-invoked 入口，路由无法触发。被否。
- **版本源移到独立文件**：多一处须手工同步，违反「单一版本源」。被否。

## 后果

- 根 `SKILL.md` 是入口 + 跨阶段状态持有者 + 版本权威读取源；子 Skill 只承担本环节。
- 根编排器通过 `plugin.json` 的 `skills: ["./"]` 显式注册；Claude Code 仍会同时扫描插件默认 `skills/` 目录并加载 8 个子 Skill。这样多 Skill 插件不会因存在 `skills/` 或自定义 `skills` 字段而遗漏根 `SKILL.md`。
- `plugin.json` 不再逐项重复登记默认 `skills/` 下的子目录，避免新增/删除子 Skill 时产生双重清单漂移；子 Skill 完整性由默认目录扫描、`install-profiles` 与 `validate.sh` 反向覆盖共同保证。
- 根在两份 `install-profiles` 中继续登记为 `mobile-game-product-forge`（source_files: `SKILL.md`/`agents/`/`references/`），因为插件注册和跨 Agent 安装档案用途不同。`validate.sh` 断言 `skills` 包含且仅包含根入口 `./`、根名一致、默认 `skills/` 每个目录均有 `SKILL.md`。反转需新 superseding ADR。

## 2026-07-26 补充

自 3.2.0 起，正式文档不再维护第二个独立的“Skill 版本”硬编码字段；根 `SKILL.md` 只保留“当前 Skill 版本”，正式文档在文末使用一行紧凑生成记录。`package.json` 仍是唯一版本源，`validate.sh` 校验 package、plugin 和根 Skill 当前版本一致。
