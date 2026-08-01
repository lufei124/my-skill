# 移动游戏产品需求工坊架构进度

更新时间：2026-07-24
当前阶段：P1完成，等待P2排期

当前 Skill 版本：`2.2.0`（唯一版本源 `package.json`）

## 已完成

### P0

- 保留现有 `mobile-game-product-forge` 入口和原有 PRD 能力。
- Life Reboots 项目资料从通用 `references/` 和根 `knowledge/` 迁移到可选知识包。
- 建立 `core` 安装档案，不包含任何项目知识。
- 建立 `core + life-reboots` 安装档案，按需初始化项目知识。
- 新增用户主动调用的 `setup-mobile-game-product-forge`。
- 初始化前必须探测、预览并等待确认。
- 已有知识文件不得被初始化或升级覆盖。
- 无知识库时，通用 Skill 仍可运行，并明确报告知识缺口。
- 建立 P0 架构自动校验脚本。

### P1

- 主 Skill 精简为轻量编排器，按独立调用价值拆出 6 个子 Skill：
  - `game-requirement-discovery`（需求访谈 -> 需求理解确认）
  - `game-prototype`（交互原型）
  - `game-prd-writing`（PRD 生成）
  - `game-prd-review`（多角色评审 -> 校验）
  - `game-analytics-design`（埋点与指标）
  - `game-knowledge-maintenance-proposal`（知识维护提案）
- 编排器保留模式判断、三个确认门、信息优先级、多 Agent 协议与校验；子 Skill 只负责本环节执行，可独立调用做窄任务。
- 新增 `scripts/install.sh` 跨 Codex / Claude Code / Cursor 统一安装脚本，整包链接保留相对引用，支持知识包安装与 `--unlink`。
- 新增 `.claude-plugin/plugin.json` Claude Code 插件清单。
- 新增 `package.json` 作为单一版本源；`CHANGELOG.md` 记录变更。
- 新增 `scripts/validate.sh`，在 P0 基础上增加 P1 结构、相对链接、版本一致性、插件清单与安装档案校验。
- 新增 `.github/workflows/validate.yml` CI 工作流。
- 新增 `AGENTS.md`（维护者指引）与 `README.md`（使用说明）。
- `install-profiles` 两套档案均收录全部子 Skill。

## 验证结果

- P0 结构校验：通过
- P1 结构/链接/版本一致性/元数据/调用配置校验：通过（`scripts/validate.sh`）
- 安装脚本语法：通过；codex 链接、知识包安装（10 文件无冲突）、回执写入、`--unlink` 行为回归：通过
- 子 Skill 相对引用解析：通过

## 当前目录

```text
mobile-game-product-forge/
├── SKILL.md                        轻量编排器
├── AGENTS.md                       维护者指引
├── README.md                       使用说明
├── CHANGELOG.md                    变更记录
├── package.json                    唯一版本源
├── agents/
├── references/
├── skills/
│   ├── setup-mobile-game-product-forge/
│   ├── game-requirement-discovery/
│   ├── game-prototype/
│   ├── game-prd-writing/
│   ├── game-prd-review/
│   ├── game-analytics-design/
│   └── game-knowledge-maintenance-proposal/
├── install-profiles/
│   ├── core.yaml
│   └── core-life-reboots.yaml
├── knowledge-packs/
│   └── life-reboots/
├── scripts/
│   ├── install.sh
│   ├── validate.sh
│   └── validate-p0-architecture.sh
├── .claude-plugin/
│   └── plugin.json
├── .github/
│   └── workflows/
│       └── validate.yml
└── history/
    ├── research/
    └── progress/
```

## 待开始

### P2

- 建立更完整的行为评估集（模式1/2/3 回归、埋点去重、配置输出格式不回退）。
- 增加知识包差异、升级和冲突报告工具。
- 成熟度分层（stable / experimental / deprecated），不过度分桶。
