# ADR-0006：以 Claude Code plugin 形态发布 + package.json 唯一版本源

状态：已采纳

## 背景

本 skill 需要能被 Claude Code、Codex、Cursor 等多种 Agent 安装使用，需要确定分发形态、安装方式与版本管理。skill 有多处需要版本字段（插件清单、`SKILL.md` 末尾版本声明），若各处独立维护，发版时手工改多处易漏改或不一致。

## 决策

以 **Claude Code plugin** 形态发布：`.claude-plugin/plugin.json` 用 `skills: ["./"]` 显式注册根编排器（仓库根即本 Skill）；`.claude-plugin/marketplace.json` 同仓自托单插件条目，`source: "./"`，刻意不写 `version`（版本解析统一落到 `plugin.json`）。脚本轨用 `scripts/install.sh` / `install.ps1` 整包软链到 `~/.claude/skills/` 或 `~/.codex/skills/`，保留仓库结构使相对引用（`references/`、`scripts/`）在 skill 目录内仍生效。

**`package.json` 的 `version` 是唯一版本源**。`plugin.json` 的 `version` 与 `SKILL.md` 的「当前 Skill 版本」必须与之一致，由 `scripts/validate.sh` 校验。发版一律走 `scripts/release.sh <新版本>`：同步三处版本、断言 `CHANGELOG.md` 已有对应条目、跑全量校验，不手工在多处改。

## 备选方案

- 只提供脚本软链安装，不做插件清单：被否，无插件清单则无法走 Claude Code 插件自动升级轨，且 `validate.sh` 无法校验注册策略。
- 在 `plugin.json` 逐项登记每个子目录：被否，本 skill 是单编排器（无子 skill），`skills: ["./"]` 已足够，逐项登记会造成注册漂移。
- 各文件独立写版本：被否，多处漂移、易漏改。
- 以 `plugin.json` 为版本源：被否，`package.json` 是更通用的版本载体（`npm` 生态、`git archive` 命名均可消费），且 `npm run validate` 入口天然挂在这里。

## 后果

- 安装双轨：Claude Code 用户走插件轨（自动升级），Codex/Cursor 用户走脚本软链轨。
- 发版必须 bump `plugin.json` 版本（经 `release.sh` 同步三处），否则已安装用户不会升级。
- `validate.sh` 校验 `plugin.json` 根注册策略、`marketplace.json` 自托条目结构与三处版本一致。
- 未明确发布任务不自动升版本；`CHANGELOG.md` 顶部 `[Unreleased]` 段积累未发布变更。
