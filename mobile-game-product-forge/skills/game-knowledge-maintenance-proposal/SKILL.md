---
name: game-knowledge-maintenance-proposal
description: Use only after a finalized PRD when the root mobile-game-product-forge orchestrator delegates knowledge-maintenance evaluation, or when the user explicitly asks only for a knowledge-base update proposal. Proposes long-term facts worth saving and never writes to the knowledge base directly. Do not route active feature design, requirement research, or PRD creation here.
---

# 游戏知识维护提案

负责正式 PRD 完成后的独立「知识维护提案」分支。比较当前背景、最终 PRD、确认原型或豁免记录和决策记录，只提出值得长期保存的建议；与飞书交付没有固定先后或依赖关系。L1 默认不生成，L2 按长期价值决定，L3 必须评估是否需要提案（结论可以是不需要）。

本子 Skill 是 `mobile-game-product-forge` 的能力拆分。跨阶段状态所有权（需求处理模式、确认门、信息优先级、版本号、共享工作目录、多 Agent 协议）由编排器持有；本子 Skill 只输出提案，不写入知识库。

## 前置条件

1. PRD 已完成并通过校验，或用户明确要求维护项目知识库。
2. 编排器已持有项目知识库只读边界与信息优先级，本子 Skill 不重复其规则。
3. 共享工作目录中存在最终 PRD、确认原型或豁免记录和决策记录，作为差异比较的输入。

## 铁律

1. 项目知识库默认只读。本子 Skill 不得直接写入 `knowledge/`。
2. 只输出目标文件、依据、拟变更内容、冲突和待人工确认项。
3. 用户确认后，由人工通过独立知识维护流程落库。

## 值得保存

只建议保存：

- 新增正式功能
- 核心规则变化
- 长期配置能力
- 商业化变化
- 项目阶段变化
- 会影响后续需求的决定

## 不保存

- 页面间距、临时文案
- 单次评审建议
- 未确认方案
- 详细测试用例
- 完整 PRD 正文
- 临时开发任务

## 输出格式

提案格式以 [../references/project-knowledge.md](../../references/project-knowledge.md) 第 5 节为唯一权威，本子 Skill 不得缩减字段。每个提案须含全部 12 字段：提案编号（`KP-<模块>-NNN`，如 `KP-analytics-001`）、目标知识模块、目标文件、变更类型（新增/修订/废弃/替代）、触发来源、现有知识、拟变更内容、证据、影响范围、冲突与风险、需要人工确认、建议负责人。

lazy-create 规则：目标知识模块在 `knowledge/INDEX.md` 无对应行时，提案须额外含一条「新增模块」子提案（新增 INDEX 行状态为「待补充」+ 创建空模块目录），先挂号后填内容。

提案持久化：每个提案须写入共享工作目录的 `09-knowledge-proposals.md`（结构见 [../references/templates.md](../../references/templates.md) 第 11 节），按状态词追踪：`待确认` / `已采纳待写入` / `已落库` / `已驳回`；落库由人工回填落库时间与落库人，AI 不写 `knowledge/`。

先展示全部建议，等待用户逐项确认后再在 `09-knowledge-proposals.md` 中把状态由「待确认」改为「已采纳待写入」。未确认项不得标记为已采纳。

## 参考

- 项目知识库维护边界：[../references/project-knowledge.md](../../references/project-knowledge.md)
