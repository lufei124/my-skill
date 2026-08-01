# ADR-0002: PRD 经 lark-cli/飞书云文档发布，非本地 PDF

- 状态：已采纳（2.4.1 反转先前本地 PDF 方案）
- 日期：2026-07-25
- 影响：发布链路（难逆）
- 关系：发布渠道决策（lark-cli/飞书、非本地 PDF）不变；正文「发布非确认门」论断被 [ADR-0008](0008-feishu-publish-as-fourth-confirmation-gate.md) 增补为第四道确认门

## 背景

2.4.1 之前 PRD 终稿通过本地脚本渲染 PDF 交付。本地渲染依赖易腐烂（字体/库/平台差异），且 PDF 为静态产物，不支持实时协作、评论与版本回溯。飞书已是团队既有协作平台。

## 决策

PRD 终稿经 `lark-cli` 发布为飞书云文档。`lark-cli` 在 OS keychain 管理 app_secret/token，本 Skill 不读取、不存储任何凭证。

## 备选方案

- **本地 PDF 渲染**：渲染工具链腐烂（已在 2.4.1 移除 `render_pdf.py`），产物静态不可协作。被否。
- **本地 markdown 终稿**：缺协作/评论/版本能力，且与飞书既有工作流割裂。被否。
- **Skill 自管飞书凭证**：违反「Skill 不触密」边界，凭证泄露面扩大。被否。

## 后果

- 发布产物支持实时协作、评论与版本回溯；凭证由 `lark-cli` 在 OS keychain 管理。
- 发布前置飞书已绑定（`lark-cli auth check` 通过），未绑定时回退请用户粘贴正文；发布非确认门，终稿前不得发布。可变规则见 `skills/game-prd-publish/SKILL.md` 与 `references/feishu-publish.md`。
