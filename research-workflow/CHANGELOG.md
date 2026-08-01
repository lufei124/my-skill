# Changelog

All notable changes to `research-workflow`. The single version source is `package.json`; every other version field must match it and is checked by `scripts/validate.sh`.

## [Unreleased]

## [1.0.0] - 2026-08-01

### Added

- **升级基础设施（镜像 mobile-game-product-forge 成熟度）**：
  - `package.json` 唯一版本源 + `npm run validate`。
  - `.claude-plugin/plugin.json`（根注册 `skills:["./"]`）+ `.claude-plugin/marketplace.json`（同仓自托单插件，`source:"./"`，不写 version）。
  - `agents/openai.yaml` 跨平台 adapter（interface + policy.allow_implicit_invocation）。
  - `AGENTS.md` 维护者手册（15 节：职责/优先级/边界/修改流程/原则/Skill 开发/参考与预设维护/同步清单/文档同步机制/检查表/一致性/验证矩阵/版本发布/多 Agent 协作/禁止/完成定义）。
  - `.agents/adr/` 追加式 ADR（README + 0001-0006：grilling 强制不可跳过 / 编号主题目录+6 层 / 三阶段 Workflow / 通用核心+可插拔预设 / 从 subsystem-research-workflow 通用化 / 插件形态发布+package.json 唯一版本源）。
  - `scripts/validate.sh` 校验器（结构/版本一致/插件清单/marketplace/YAML 结构/引用解析/脚本存在/install-profiles/文档漂移/升级 SOP/ADR 索引/通用参考完整/预设配对/PRESETS 一致/evals.json 可解析+断言名登记/skeleton + grader self-test/shell 语法）。
  - `scripts/install.sh` + `scripts/install.ps1` 跨 Agent 安装器（codex/claude/cursor/all，整包软链，依赖体检）。
  - `scripts/release.sh` 发版入口（同步三处版本 + 断言 CHANGELOG + 全量校验）。
  - `scripts/githooks/pre-push` 推送门禁。
  - `scripts/doc-impact-check.sh` 文档影响预检（非阻断）。
  - `install-profiles/core.yaml` source_files 校验清单。
  - `operation-guide.md` 用户日常操作文档 + `install-guide.md` 安装升级指南。
  - `create_research_skeleton.py --self-test` 回归（每个 preset 骨架生成 + 6 层 + brief + 序号递增 + 不覆盖 + 无残留占位符）。
  - `grade_research_init.py --self-test` 回归（构造假 eval 目录跑全部断言检查器）。

### Changed

- SKILL.md 标题后加「当前 Skill 版本」行（由 `validate.sh` 校验与 `package.json` 一致）。
- README.md 加「安装」「升级」小节，内容表登记新增文件。

### Notes

- 本 skill 在 1.0.0 之前为无版本号的通用化版本（由 `subsystem-research-workflow` 通用化而来，见 [ADR-0005](.agents/adr/0005-generalized-from-subsystem-research.md)）。1.0.0 是首个带升级基础设施与版本校验的发布。
