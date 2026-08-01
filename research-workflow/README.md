# Research Workflow Skill

> 当前 Skill 版本：v1.0.0（唯一版本源 `package.json`，由 `scripts/validate.sh` 校验）。安装与升级见 [install-guide.md](install-guide.md)，日常操作见 [operation-guide.md](operation-guide.md)，维护者手册见 [AGENTS.md](AGENTS.md)。

一个可移植、领域无关的 skill，用于对项目中的某个子系统、模块或流程进行深度调研与设计批判。先强制对齐目标，再组织多 Agent 虚拟团队并行产出结构化文档。

## 内容

- `SKILL.md`：Agent 行为守则（何时使用 + 阶段 0-4 执行流程）
- `agents/openai.yaml`：跨平台 adapter（interface 元数据 + 调用策略）
- `scripts/create_research_skeleton.py`：创建 `.scratch/research/NN-topic/` 骨架，支持 `--preset` 注入领域专属内容；含 `--self-test` 回归
- `scripts/grade_research_init.py`：评分脚本，检查初始化输出是否满足断言；含 `--self-test` 回归
- `scripts/aggregate_benchmark.py`：汇总 benchmark 结果
- `scripts/validate.sh`：统一校验器（结构/版本/插件清单/引用/预设配对/PRESETS 一致/evals 断言登记/self-test/语法）
- `scripts/install.sh` / `scripts/install.ps1`：跨 Agent 安装器（codex/claude/cursor/all，整包软链）
- `scripts/release.sh`：发版入口（同步三处版本 + 断言 CHANGELOG + 全量校验）
- `scripts/doc-impact-check.sh`：文档影响预检（非阻断）
- `scripts/githooks/pre-push`：推送门禁
- `references/grilling-questions.md`：通用 grilling 问题清单
- `references/team-roles.md`：通用默认角色原型
- `references/output-structure.md`：通用产出目录结构与各层语义
- `references/workflow-template.md`：多 Agent Workflow 脚本模板
- `references/domain-presets/`：领域预设（game-mud / software-system，每个含 `.md` + `.brief.md` 成对）
- `evals/evals.json`：eval 定义（prompt / 断言 / 期望产出）
- `install-profiles/core.yaml`：source_files 校验清单
- `operation-guide.md` / `install-guide.md`：用户操作 / 安装升级指南
- `AGENTS.md` / `CHANGELOG.md`：维护者手册 / 变更记录
- `.agents/adr/`：架构决策记录

## 安装

见 [install-guide.md](install-guide.md)。简要：

```bash
# Claude Code / Codex（脚本软链，整包链接保留相对引用）
bash scripts/install.sh --agent claude
bash scripts/install.sh --agent codex
# Cursor（写当前项目的 .cursor/rules 规则）
bash scripts/install.sh --agent cursor --target .
# 全部
bash scripts/install.sh --agent all
```

Windows 原生用 `scripts/install.ps1`。前置：Python 3（初始化器依赖）。

## 快速开始

```bash
python research-workflow/scripts/create_research_skeleton.py auth-module --preset software-system
```

该命令会在当前项目的 `.scratch/research/` 下创建带序号主题目录：

```text
.scratch/research/01-auth-module/
├── 00-brief/brief.md       # 总则（已按 preset 注入领域增量）
├── 01-raw-findings/
├── 02-perspectives/
├── 03-design-options/
├── 04-redteam-review/
└── 05-synthesis/
```

可用的 `--preset` 值：`game-mud`、`software-system`、`none`（默认，纯通用）。

## 执行流程概览

1. **阶段 0 Grilling 对齐**（强制，不可跳过）：逐一确认范围、目标、领域预设、团队、产出、对抗机制、执行方式、是否 commit。
2. **阶段 1 初始化**：创建编号主题目录与 6 层子目录 + brief 总则。
3. **阶段 2 三阶段 Workflow**：并行初稿 -> 红队对抗 -> 评审委员会汇总。
4. **阶段 3 补全失败产出**：重跑失败 agent。
5. **阶段 4 最终检查与汇报**：默认不自动 commit。

完整行为守则见 [`SKILL.md`](SKILL.md)，日常操作见 [`operation-guide.md`](operation-guide.md)。

## 升级

### 脚本轨（git）

`--agent codex|claude` 把整个 skill 目录软链到 skills 目录，目录本身就是安装源：

```bash
cd <skill-目录>
git pull                      # 升级完成，无需重跑 install.sh
bash scripts/validate.sh      # 自检
```

只有 skill 目录被移动、或软链被删时才需要 `bash scripts/install.sh --agent all --force` 重新指向。

### 插件轨（Claude Code）

维护者推送并 bump `plugin.json` 版本后，Claude Code 启动时后台刷新 marketplace 并自动升级到新版，重启会话生效。手动触发：`claude plugin update research-workflow@research-workflow-marketplace`。**不 bump `plugin.json` 版本的推送对已安装用户不可见**--发版必须走 `bash scripts/release.sh <新版本>`。

### 用户数据边界

升级只动 skill 目录，**不动目标项目**：目标项目里的 `.scratch/research/`、调研产出、代码都在你的项目里，安装脚本从不删除它们（`--unlink` 只移除软链和 Cursor 规则）。

### 升级后自检

1. `bash scripts/validate.sh` 全绿（需要 Python 3）。
2. 版本对齐：`package.json`、`.claude-plugin/plugin.json` 与 `SKILL.md`「当前 Skill 版本」三者一致（`validate.sh` 已断言）。
3. `python3 scripts/create_research_skeleton.py --self-test` 全绿。
4. `python3 scripts/grade_research_init.py --self-test` 全绿。

## 设计原理

- **grilling 强制不可跳过**：未对齐就并行 Workflow 会导致整轮返工，见 [ADR-0001](.agents/adr/0001-grilling-first-mandatory.md)。
- **编号主题目录 + 6 层结构**：机械可校验的产出约定，见 [ADR-0002](.agents/adr/0002-numbered-topic-six-layer-dir.md)。
- **三阶段 Workflow**（并行初稿 -> 红队 -> 评审委员会）：兼顾覆盖广、可信、收敛，见 [ADR-0003](.agents/adr/0003-three-phase-workflow.md)。
- **通用核心 + 可插拔领域预设**：领域差异只落在 `references/domain-presets/`，见 [ADR-0004](.agents/adr/0004-pluggable-domain-presets.md)。
- **从 subsystem-research-workflow 通用化而来**：原游戏专用 skill 保留，精华迁入 game-mud 预设，见 [ADR-0005](.agents/adr/0005-generalized-from-subsystem-research.md)。
- **插件形态发布 + package.json 唯一版本源**：见 [ADR-0006](.agents/adr/0006-ship-as-plugin-and-version-sot.md)。

## 版本与校验

- 唯一版本源：`package.json` `version`。`plugin.json` 与 `SKILL.md`「当前 Skill 版本」须与之一致，由 `scripts/validate.sh` 校验。
- 校验：`bash scripts/validate.sh`（结构 / 版本一致 / 插件清单 / marketplace / YAML / 引用解析 / 脚本存在 / install-profiles / 文档漂移 / 升级 SOP / ADR 索引 / 通用参考完整 / 预设配对 / PRESETS 一致 / evals 断言登记 / skeleton + grader self-test / shell 语法）。
- 发版：`bash scripts/release.sh <新版本>`（同步三处版本 + 断言 CHANGELOG + 全量校验）。

## 与 subsystem-research-workflow 的关系

本 skill 是 `subsystem-research-workflow` 的**通用化版本**：抽取其"grilling 对齐 + 编号目录 + 三阶段多 Agent Workflow + 红队 + 评审委员会汇总"方法论，去除游戏/MUD 硬编码，改为通用核心 + 领域预设包。

- 原 `subsystem-research-workflow/` 保留不动，仍可作为游戏/MUD 专用 skill 直接使用。
- 其精华（11 人游戏团队、user-stories/engine-insights 分层、现代/玩家心理/商业化视角）已迁入 [`references/domain-presets/game-mud.md`](references/domain-presets/game-mud.md)，通过 `--preset game-mud` 复用。
- 调研通用软件模块/系统/流程时，直接用本 skill（选 `software-system` 或 `none`）。

## 许可

MIT。
