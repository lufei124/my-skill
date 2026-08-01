# 安装与升级指南

本指南覆盖装、升、排查三件事，命令可直接复制执行。日常怎么用（发起调研、grilling、骨架生成、Workflow）见 [operation-guide.md](operation-guide.md)。

## 1. 一次性配置

### 1.1 前置：Python 3

初始化器需要 Python 3。打开终端执行：

```bash
python3 --version
```

能输出版本号即可跳过。装不上时：macOS 执行 `xcode-select --install` 或 `brew install python3`；Windows 用 `winget install Python.Python.3` 或到 python.org 下载。

### 1.2 方式一：Claude Code 插件

若本 skill 已作为独立 plugin 仓库发布（含 `.claude-plugin/marketplace.json`），用两条命令安装：

```bash
claude plugin marketplace add <plugin-repo-url>
claude plugin install research-workflow@research-workflow-marketplace
```

验证：`claude plugin list` 看到 `research-workflow` 且 `Status: enabled`。重启会话后生效。

> 注：当前本 skill 位于共享的 `my-skill/` 仓库下，尚未单独发布为 plugin 仓库。发布时把 skill 目录拆为独立 git 仓库并推送，marketplace.json 的 `source: "./"` 即指向该仓库自身。

### 1.3 方式二：安装脚本（Codex / Cursor / 兜底）

macOS / Linux / Windows Git Bash：

```bash
bash scripts/install.sh --agent codex              # 链接到 Codex
bash scripts/install.sh --agent claude             # 链接到 Claude Code
bash scripts/install.sh --agent cursor --target .  # 写入当前项目的 Cursor 规则
bash scripts/install.sh --agent all                # 全部
```

Windows 原生（PowerShell 5.1+，无需 Git Bash）：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent claude
powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent all
```

脚本把整个 skill 目录软链（Windows 优先软链、开发者模式不可用时回退复制）到 `~/.claude/skills/` 或 `~/.codex/skills/`，保留目录结构使相对引用（`references/`、`scripts/`、`evals/`）生效。`cursor` 在目标项目写 `.cursor/rules/research-workflow.mdc` 规则文件。可选：`--force` 替换已存在安装；`--unlink` 移除安装。

### 1.4 发起调研（每个项目按需）

在目标项目根目录，对要调研的对象生成骨架：

```bash
python <skill-path>/scripts/create_research_skeleton.py <topic-name> --preset software-system
```

然后按 [operation-guide.md](operation-guide.md) 走 grilling 对齐（若尚未对齐）与三阶段 Workflow。

## 2. 升级

### 插件安装（推荐轨）

维护者推送并 bump 版本后，Claude Code 启动时后台刷新 marketplace 并自动升级到新版，重启会话生效。手动触发：`claude plugin update research-workflow@research-workflow-marketplace`。**不 bump `plugin.json` 版本的推送对已安装用户不可见**--发版必须走 `bash scripts/release.sh <新版本>`。

插件升级覆盖的是 `~/.claude/plugins/cache/` 下的版本化目录，不会触碰你项目里的任何东西。

### 脚本安装（git 轨）

`--agent codex|claude` 把整个 skill 目录软链到 skills 目录，目录本身就是安装源：

```bash
cd <skill-目录>
git pull                      # 升级完成，无需重跑 install.sh
bash scripts/validate.sh      # 自检
```

只有 skill 目录被移动、或软链被删时才需要 `bash scripts/install.sh --agent all --force` 重新指向。

### 用户数据边界

升级只动 skill 目录，**不动目标项目**：目标项目里的 `.scratch/research/`、调研产出、代码都在你的项目里，安装脚本从不删除它们（`--unlink` / `-Unlink` 只移除软链和 Cursor 规则）。

### 升级后自检

1. `bash scripts/validate.sh` 全绿（需要 Python 3）。
2. 版本对齐：`package.json`、`.claude-plugin/plugin.json` 与 `SKILL.md`「当前 Skill 版本」三者一致（`validate.sh` 已断言）。
3. `python3 scripts/create_research_skeleton.py --self-test` 全绿。
4. `python3 scripts/grade_research_init.py --self-test` 全绿。

## 3. 常见故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `create_research_skeleton.py` 报找不到 `domain-presets/` | skill 安装不完整或软链悬空 | 重跑 `install.sh --agent <x> --force`；确认 skill 目录含 `references/domain-presets/` |
| 骨架生成后 brief 含 `<!-- 警告：预设增量片段缺失 -->` | 某预设的 `.brief.md` 被删或改名 | 补回 `references/domain-presets/<preset>.brief.md`；`validate.sh` 校验预设配对 |
| `validate.sh` 报版本不一致 | 三处版本（package.json/plugin.json/SKILL.md）不同步 | 走 `bash scripts/release.sh <新版本>` 统一同步，勿手工改多处 |
| `validate.sh` 报「PRESETS 声明的预设 != domain-presets 文件」 | 加了预设文件未登记 `PRESETS`，或反之 | 在 `create_research_skeleton.py` 的 `PRESETS` 与 `references/domain-presets/` 双向同步（`.md` + `.brief.md` 成对） |
| `validate.sh` 报「用了未在 ASSERTION_CHECKS 登记的断言」 | `evals/evals.json` 加了断言名但评分器未登记检查器 | 在 `grade_research_init.py` 的 `ASSERTION_CHECKS` 补 `name -> checker` 映射 |
| `validate.sh` 报预设缺 brief 配对 | 只加了 `<name>.md` 没加 `<name>.brief.md`（或反之） | 补齐成对文件 |
| 门禁/脚本报 python 相关错误 | Python 3 缺失 | 走 1.1 节 |

以上都解决不了时，把完整报错文本与 `bash scripts/validate.sh` 输出发给维护者。

## 4. 维护者视角（发版）

同事的自动升级只认版本号：发版必须 `bash scripts/release.sh <新版本>`（同步三处版本 + 断言 CHANGELOG + 全量校验），然后 commit 并推送。只推 commit 不 bump 版本，已安装用户永远不会升级。推送门禁用 `git config core.hooksPath scripts/githooks` 启用。
