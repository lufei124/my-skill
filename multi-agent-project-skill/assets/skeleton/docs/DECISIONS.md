# Decisions

状态使用 Accepted、Superseded、Proposed。日期来自已验证的实现或提交；无法证明的动机不写成事实。

## D-001 - 引入多 Agent 协作骨架

- 状态：Accepted
- 日期：{{INIT_DATE}}
- 背景：本项目需要被多个 AI Agent 并行编辑或在任意时刻交接，必须有持久化的事实来源替代易失的聊天上下文。
- 候选方案：仅依赖聊天记录；仅用 Git 分支无簿记；铺设 `.agent/` 协作簿记 + 文档体系骨架。
- 最终选择：通过 `multi-agent-project-skill` 的 `init_workspace.py` 生成完整骨架（入口层 + docs + skills + `.agent/` + 技术栈基线）。
- 选择原因：仓库是持久事实来源；簿记层让无聊天记录的 Agent 也能接手；文档体系让规则与代码不漂移。
- 影响范围：项目根、`docs/`、`skills/`、`.agent/`、`.github/workflows/ci.yml`、`.gitignore`。
- 后续注意：`.agent/` 必须提交到仓库；平台适配文件只指向 AGENTS.md，不复制规则。

---

> 后续决策按 `D-XXX - 标题` 格式追加。模板见 [.agent/decisions/ADR-0000-template.md](../.agent/decisions/ADR-0000-template.md)。重要技术取舍（架构、API、数据、依赖、跨模块规则）须记录于此。
