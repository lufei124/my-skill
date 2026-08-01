# ADR-0001: 以 Claude Code plugin 形态发布

- 状态：已采纳
- 日期：2026-07-25
- 影响：发布形态（难逆）

## 背景

本仓库是一套移动游戏需求工坊方法论（访谈 -> 原型 -> PRD -> 评审 -> 校验 -> 发布）。早期可表现为纯 markdown 提示库、IDE 专属扩展或通用文档。需选择最贴合「多子 Skill 路由 + 安装配置 + 不变量校验」的发布形态。

## 决策

以 Claude Code plugin 形态发布：根 `SKILL.md` 作编排器，`skills/` 拆能力子 Skill，`.claude-plugin/plugin.json` 登记，`install-profiles/` 控制安装配置，`scripts/validate.sh` 守不变量。

## 备选方案

- **纯 markdown 提示库**：无 model-invoked 路由、无安装配置、无结构校验，漂移无防线。被否。
- **IDE 专属扩展**：绑定单一编辑器，丢失跨 CLI/IDE/Web 的可达性。被否。
- **通用文档站**：只读不可执行，无法承载子 Skill 编排与 fan-out。被否。

## 后果

- 获得模型自动路由子 Skill、安装配置分层、CI 不变量脊柱。
- 须遵守 plugin 结构约束（每个 skill 有 `SKILL.md` + `agents/openai.yaml`、调用配置由 manifest 标志切分），见 `AGENTS.md`「校验」与 `scripts/validate.sh`。
