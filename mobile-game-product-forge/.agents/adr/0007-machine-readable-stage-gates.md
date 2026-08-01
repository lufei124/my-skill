# ADR-0007：使用项目级阶段状态文件和机器门禁

> 格式部分已被 [ADR-0009](0009-separate-prd-completion-from-delivery.md) 取代：机器门禁决策仍有效，但新需求由 YAML 迁移为 JSON 1.1。

- 状态：已采纳
- 日期：2026-07-25

## 背景

仅靠自然语言确认门无法完全防止直接调用下游子 Skill，例如在原型未确认时直接生成正式 PRD。跨会话、多 Agent 和多人协作时，聊天记忆也不足以作为权威状态。

## 决定

1. 正式需求在独立工作目录维护 `00-stage-state.yaml`。
2. 根编排器是唯一状态写入者；子 Skill 只读并校验，不持有或修改跨阶段状态。
3. 下游阶段进入前运行 `scripts/check-stage-gate.py`；失败只输出 `BLOCKED`，不得生成下游产物。
4. 用户明确标记的窄任务可绕过完整流程，但必须标注 `narrow_task`，不得冒充正式终稿。
5. 原型到 PRD 的门禁同时检查状态、文件存在和 `prototype-meta.prototypeStatus=Confirmed`，避免仅靠文件名或散文声明。

## 备选

- 只靠提示词：实现简单，但无法跨 Agent 稳定执行，否决。
- 每个子 Skill 自己维护状态：会造成多写者和状态漂移，否决。
- 引入外部工作流服务或数据库：对单仓库 Skill 过重，暂不采用。

## 影响

- `references/stage-gates.md` 成为共享门禁合同。
- `references/templates.md` 提供机器可读状态模板。
- setup 把用户操作指南写入目标项目；根编排器在用户询问时返回指南位置和启动方式。
