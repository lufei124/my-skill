# ADR-0006：package.json 为唯一版本源

状态：已采纳

## 背景

skill 有多处需要版本字段：插件清单 `plugin.json`、`SKILL.md` 文末版本声明、可能的分发 ZIP 命名。若各处独立维护，发版时手工改多处易漏改或不一致，导致插件用户看到的版本与实际不符。

## 决策

`package.json` 的 `version` 是**唯一版本源**。`plugin.json` 的 `version` 与 `SKILL.md` 的「当前 Skill 版本」必须与之一致，由 `scripts/validate.sh` 校验。发版一律走 `scripts/release.sh <新版本>`：同步三处版本、断言 `CHANGELOG.md` 已有对应条目、跑全量校验，不手工在多处改。

## 备选方案

- 各文件独立写版本：被否，多处漂移、易漏改。
- 以 `plugin.json` 为源：被否，`package.json` 是更通用的版本载体（`npm` 生态、`git archive` 命名均可消费），且 `npm run validate` 入口天然挂在这里。
- 子 skill 携带独立版本：本 skill 无子 skill，不适用；即便有，也应「随包发布，见 package.json」。

## 后果

- 发版只改一处（经 `release.sh`），三处自动同步。
- `validate.sh` 断言三处一致，不一致即校验失败。
- 未明确发布任务不自动升版本；`CHANGELOG.md` 顶部 `[Unreleased]` 段积累未发布变更。
