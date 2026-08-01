# ADR-0005：以 Claude Code plugin 形态发布

状态：已采纳

## 背景

本 skill 需要能被 Claude Code、Codex、Cursor 等多种 Agent 安装使用。需要确定分发形态与安装方式。

## 决策

以 **Claude Code plugin** 形态发布：`.claude-plugin/plugin.json` 用 `skills: ["./"]` 显式注册根编排器（仓库根即主编排器 Skill）；`.claude-plugin/marketplace.json` 同仓自托单插件条目，`source: "./"`，刻意不写 `version`（版本解析统一落到 `plugin.json`）。脚本轨用 `scripts/install.sh` / `install.ps1` 整包软链到 `~/.claude/skills/` 或 `~/.codex/skills/`，保留仓库结构使相对引用（`references/`、`scripts/`）在 skill 目录内仍生效。

## 备选方案

- 只提供脚本软链安装，不做插件清单：被否，无插件清单则无法走 Claude Code 插件自动升级轨，且 `validate.sh` 无法校验注册策略。
- 在 `plugin.json` 逐项登记每个子目录：被否，本 skill 是单编排器（无子 skill），`skills: ["./"]` 已足够，逐项登记会造成注册漂移。

## 后果

- 安装双轨：Claude Code 用户走插件轨（自动升级），Codex/Cursor 用户走脚本软链轨。
- 发版必须 bump `plugin.json` 版本（经 `release.sh` 同步三处），否则已安装用户不会升级。
- `validate.sh` 校验 `plugin.json` 根注册策略与 `marketplace.json` 自托条目结构。
