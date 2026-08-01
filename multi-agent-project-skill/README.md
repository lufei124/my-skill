# Multi-Agent Project Skill

一个可移植的 Claude Code skill，面向那些可能被多个 AI Agent 并行编辑、或在任意时刻被交接的项目。它既初始化一个可被 AI 协作开发的项目骨架，也定义多 Agent 并行编辑、交接、审查与集成的协作协议。

当前版本：见 `package.json`（唯一版本源）。变更记录见 `CHANGELOG.md`。

## 内容

- `SKILL.md`：Agent 行为与协作协议守则。
- `AGENTS.md`：仓库维护者手册（修改流程、验证矩阵、版本发布）。
- `agents/openai.yaml`：跨平台 adapter 元数据（interface + policy）。
- `scripts/init_workspace.py`：从 `assets/` 读取模板，为目标项目生成完整骨架（入口层 + docs + skills + `.agent/` + 技术栈基线）。默认不覆盖已有文件。支持 `--self-test` 回归。
- `scripts/validate.sh`：结构与不变量校验器（版本一致 / 引用解析 / 占位符集合 / 栈 `.gitignore` 不忽略 `.agent/` / Python self-test / shell 语法）。
- `scripts/install.sh` / `scripts/install.ps1`：跨 Agent 安装器（codex / claude / cursor / all，整包软链）。
- `scripts/release.sh`：发版入口（同步三处版本 + 断言 CHANGELOG + 全量校验）。
- `scripts/doc-impact-check.sh`：文档影响预检（非阻断）。
- `scripts/githooks/pre-push`：推送门禁（`git config core.hooksPath scripts/githooks` 启用）。
- `assets/`：**模板的唯一真相源**。修改模板直接改这里的文件，不要改脚本（脚本不含任何内嵌模板）。
  - `assets/skeleton/`：技术栈无关骨架，镜像目标项目路径。
  - `assets/stacks/{node,python,generic}/`：技术栈相关的 `.gitignore` 与 CI 模板。
- `references/WORKFLOW.md`：精简版操作流程。
- `references/EXAMPLES.md`：并行开发、接管、注册、撞号与陈旧锁判定示例。
- `operation-guide.md`：面向使用者的日常操作文档（初始化/认领/交接/接管/陈旧/集成）。
- `install-guide.md`：安装、升级与故障排查指南。
- `install-profiles/core.yaml`：source_files 校验清单（校验用，不驱动安装）。
- `.claude-plugin/plugin.json` + `marketplace.json`：Claude Code 插件清单与同仓自托 marketplace。
- `.agents/adr/`：架构决策记录（why + 备选）。

## 安装

详细步骤见 [install-guide.md](install-guide.md)。概览：

```bash
# 方式一：安装脚本（Codex / Cursor / 兜底）
bash scripts/install.sh --agent claude
bash scripts/install.sh --agent all

# 方式二：Claude Code 插件（skill 作为独立 plugin 仓库发布后）
claude plugin marketplace add <plugin-repo-url>
claude plugin install multi-agent-project-skill@multi-agent-project-marketplace
```

安装后依赖体检会提示 Python 3（init_workspace.py 必需）。

## 初始化一个项目

```bash
# 预览将生成的文件（不落盘）
python /path/to/skill/scripts/init_workspace.py /path/to/project --dry-run
# 实际生成
python /path/to/skill/scripts/init_workspace.py /path/to/project
```

技术栈自动探测：`package.json` -> node；`pyproject.toml`/`requirements.txt` -> python；否则 generic（生成占位骨架，由首个 Agent 补齐命令）。

### 常用选项

- `--dry-run`：只打印计划，不写入。
- `--stack {node,python,generic}`：手动指定技术栈，覆盖探测。
- `--force`：覆盖已有文件（慎用）。
- `--init-git`：非 Git 仓库时执行 `git init`。
- `--self-test`：跑回归自测后退出（不写目标项目）。

## 生成的骨架

```text
<project>/
├── AGENTS.md / CLAUDE.md / README.md      # 入口层（AGENTS.md 统一入口，平台文件只链接不复制规则）
├── .gitignore                              # 按技术栈生成
├── docs/                                   # 长期文档（PROJECT_CONTEXT / ARCHITECTURE / DEVELOPMENT_RULES / TESTING / DECISIONS / GLOSSARY）
├── skills/                                 # 5 个九段式 skill（requirement-review / feature-development / bug-fix / test-and-verify / task-handoff）
├── .agent/                                 # 多 Agent 协作簿记
│   ├── PROJECT_STATE.md / TASK_BOARD.md / FILE_LOCKS.md / TASK_HANDOFF.md / AGENTS_REGISTRY.md
│   ├── decisions/  handoffs/  task-ids/
└── .github/workflows/ci.yml                # 按技术栈生成
```

`.agent/` 必须提交到仓库（协作状态需共享）；三份 `.gitignore` 均不忽略它。

已有文件默认保留。仅在你确实打算替换内容时，才使用 `--force`。

## 升级

详细步骤见 [install-guide.md](install-guide.md)。概览：

### 脚本安装（git 轨）

```bash
cd <skill-目录>
git pull                      # 升级完成，无需重跑 install.sh
bash scripts/validate.sh      # 自检
```

只有 skill 目录被移动、或软链被删时才需要 `bash scripts/install.sh --agent all --force` 重新指向。

### 插件安装（推荐轨）

维护者推送并 bump 版本后，Claude Code 启动时后台刷新并自动升级，重启会话生效。手动：`claude plugin update multi-agent-project-skill@multi-agent-project-marketplace`。**不 bump `plugin.json` 版本的推送对已安装用户不可见**--发版必须走 `bash scripts/release.sh <新版本>`。

### 用户数据边界

升级只动 skill 目录，**不动目标项目**：目标项目里的 `.agent/`、`docs/`、`skills/`、代码都在你的项目里，安装脚本从不删除它们（`--unlink` / `-Unlink` 只移除软链和 Cursor 规则）。

### 升级后自检

1. `bash scripts/validate.sh` 全绿（需要 Python 3）。
2. 版本对齐：`package.json`、`.claude-plugin/plugin.json` 与 `SKILL.md`「当前 Skill 版本」三者一致（`validate.sh` 已断言）。
3. `python3 scripts/init_workspace.py --self-test` 全绿。

## 设计原理

- **仓库是持久的事实来源；聊天上下文是临时的**。所有协作状态落到磁盘文件，不依赖对话记录。
- **模板单一真相源**：`assets/` 是唯一模板来源，脚本零内嵌字符串，消除双份漂移。
- **AGENTS.md 统一入口**：平台适配文件（CLAUDE.md 等）只链接不复制规则，避免多处维护漂移。
- **Git 隔离优先**：并行任务用独立分支/worktree，文件锁只是建议性协调记录。
- **保守主义**：默认不覆盖、不提交、不推送；禁用破坏性 Git 命令。

## 版本与校验

- 唯一版本源：`package.json`。`SKILL.md` 与 `.claude-plugin/plugin.json` 的版本字段必须一致，由 `scripts/validate.sh` 校验。
- 提交前跑 `bash scripts/validate.sh`（或 `npm run validate`）。
- 发版：`bash scripts/release.sh <新版本>` 一键同步三处版本、断言 CHANGELOG、跑全量校验。
- 推送门禁：`git config core.hooksPath scripts/githooks` 启用，钩子跑 validate.sh + install.sh 语法检查。

## 许可

MIT。
