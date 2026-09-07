# project-agent-planner · v1.1.0

根据当前项目生成 Agent 架构与落地方案，不限电商。参考 `anthropics/commerce-agents` 的设计模式，先理解业务和代码，再决定用不用 Agent、如何拆分、如何接工具，以及如何控制写操作。

## 默认运行框架

**生成的 Agent 方案默认必须采用 Claude Agent SDK，只有用户明确要求不用才例外。**保留现有模型服务商、现有业务栈或旧接口，不构成豁免。SDK 负责 Agent 主循环，业务服务继续复用；多模型兼容性单独核验，不自动换成自研循环。

此要求约束生成的项目方案，不要求运行本 Skill 的宿主必须是 Claude Code；也不意味着现在就安装 SDK 或修改项目依赖。

## 安装

将整个 `project-agent-planner` 文件夹复制到以下位置之一，不要只复制 `SKILL.md`：

| 使用范围 | Claude Code | Codex |
|---|---|---|
| 当前项目 | `<项目>/.claude/skills/project-agent-planner/` | `<项目>/.agents/skills/project-agent-planner/` |
| 所有项目 | `~/.claude/skills/project-agent-planner/` | `~/.agents/skills/project-agent-planner/` |

`~` 表示当前用户主目录；Windows 对应用户目录下的相同文件夹。升级时备份旧版，再替换整个同名 Skill 文件夹，不能只换 SKILL.md。这里只是放置位置，没有要求运行安装脚本。宿主未发现新增 Skill 时，重新启动会话。

位置依据见 [references/sources.md](references/sources.md) 的官方文档。本包未替你安装到本机。

## 使用

在目标项目中调用：

Claude Code：

```text
/project-agent-planner 根据当前项目生成 Agent 方案，先给方案，不修改业务代码。
```

Codex：

```text
$project-agent-planner 根据当前项目生成 Agent 方案，先给方案，不修改业务代码。
```

也可以补充本次范围：

```text
使用 project-agent-planner 分析当前项目，只考虑用户侧助手。
优先复用现有接口，第一版只读，给出最小可行方案。
```

没有代码时，可以提供产品描述或 PRD；输出会标为概念方案，不伪造现有模块。若宿主不能发现 Skill，可明确让它读取本目录的 SKILL.md 及其中引用的参考文件；这不等于已完成安装。

## 输出

默认生成 `docs/agent-plan.md`；已有文件不静默覆盖。用户只要对话输出或宿主不可写时，直接输出 Markdown。

方案覆盖：项目事实与证据、优先场景、Claude Agent SDK 接入与职责分工、模型配置与兼容验证、工具/Backend 映射、规则分层、安全边界、实施顺序、验收与待确认事项。

不会强制双 Agent，不把每个工作流或画布节点做成 Agent，不为 SDK 重写整个业务栈，不默认建设长期记忆或三套运行时。现有 Agent 优先做增量接入方案；确实不需要 Agent 时保留确定性流程。

## 文件

```text
project-agent-planner/
├── SKILL.md
├── README.md
└── references/
    ├── commerce-patterns.md
    ├── sdk-runtime.md
    ├── plan-template.md
    ├── evaluation.md
    └── sources.md
```

`SKILL.md` 管流程，推荐 Agent 时读取 `sdk-runtime.md`，其余参考文件按需读取。Skill 包无执行依赖与安装脚本；具体 SDK/API 或模型支持范围需要按项目版本核验，不要求克隆整个参考仓库。

## 边界与检查状态

这是一份方案生成 Skill，不是可运行的 Agent 框架，也不是官方 commerce-builder 插件。默认不会修改业务代码、项目指令文件或线上系统。

本次同步更新主 Skill、模式库 P6、方案模板、验收表和来源说明，新增 `sdk-runtime.md`。已检查 YAML 元数据、本地引用、约束同步和压缩包结构；未在 Claude Code、Codex 或真实项目中行为试跑，也未实测模型接入。验收表中的用例不是已通过的测试报告。
