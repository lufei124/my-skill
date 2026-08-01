# 操作指南

面向在本项目里使用 `research-workflow` skill 的产品经理、开发与调研 Agent。覆盖调研发起、grilling 对齐、骨架生成、Workflow 执行、补全与汇报六件日常事。安装与升级见 [install-guide.md](install-guide.md)；完整协议见 [SKILL.md](SKILL.md)。

> 注：本文件是 skill 仓库内的操作文档。调研产物落在目标项目的 `.scratch/research/` 下，本文件不写入目标项目；需要时直接读本 skill 仓库的此文件。

## 1. 发起一次调研

用户表达调研意图（「调研 X」「全面分析 X」「对 X 做源码考古」「组织团队评审 X」等）时触发本 skill。

**先做 Grilling 对齐（阶段 0，强制不可跳过）**：逐一向用户确认 `references/grilling-questions.md` 的决策点--范围 / 目标 / 领域预设 / 团队 / 产出结构 / stories 视角 / 保存位置 / 对抗机制 / 执行方式 / 批判视角范围 / 资料来源 / 是否 commit。每个问题等用户回答后再继续；用户已明确的可跳过但须记进总则。选定领域预设后，预设文档（`references/domain-presets/<preset>.md`）的「追加问题」也要一并确认。

> 永不在 grilling 完成前深入源码或给结论。

## 2. 生成调研骨架（阶段 1）

grilling 对齐后，在目标项目根目录创建编号主题目录与 6 层子目录 + brief 总则：

```bash
# 默认纯通用（none 预设）
python <skill-path>/scripts/create_research_skeleton.py <topic-name>
# 按领域预设注入 brief 增量
python <skill-path>/scripts/create_research_skeleton.py auth-module --preset software-system
python <skill-path>/scripts/create_research_skeleton.py combat-system --preset game-mud
# 指定研究根目录（默认 .scratch/research）
python <skill-path>/scripts/create_research_skeleton.py <topic> --root <research-root>
```

脚本自动：扫描 `.scratch/research/` 取下一个序号 NN，创建 `NN-<topic>/` 与 6 层子目录（`00-brief` / `01-raw-findings` / `02-perspectives` / `03-design-options` / `04-redteam-review` / `05-synthesis`），写入 `00-brief/brief.md` 总则（按 preset 注入领域 brief 增量）。各层语义见 `references/output-structure.md`。

生成后：把 grilling 确认的范围/目标/团队/方法/约束补进 `00-brief/brief.md` 对应章节（模板已留占位提示）。

## 3. 执行三阶段 Workflow（阶段 2）

按 `references/workflow-template.md` 改编 Workflow 脚本并启动：

- **Phase 1 并行初稿**：资料考古组 / 抽象与方案组 / 批判性外部视角组并行产出各自章节，落到对应层目录。
- **Phase 2 红队对抗**：横向对比验证、现代实践挑战、体验风险挑战、价值风险挑战，记录到 `04-redteam-review/`。
- **Phase 3 评审委员会汇总**：审阅全部初稿与红队报告，统一文风、消除矛盾、裁决分歧，生成最终报告到 `05-synthesis/`。

## 4. 补全失败产出（阶段 3）

Workflow 完成后检查是否有 agent 失败。如有：单独用 Agent 工具重跑失败角色；若最终报告已在失败前生成，在报告中补说明或加附录引用补全文件。不因单个 agent 失败丢弃整轮。

## 5. 最终检查与汇报（阶段 4）

1. 检查所有预期文件存在且非空。
2. 检查最终报告引用所有关键产出。
3. 向用户汇报：产出结构、文件清单、核心摘要、执行中的问题。
4. **仅在用户明确要求时才执行 commit & push**（默认否）。

## 6. 评分与 benchmark（可选）

对调研初始化产出做断言评分（用于 eval 回归，非日常必跑）：

```bash
# 对一个含 with_skill/ 或 without_skill/ 的 eval 目录评分
python <skill-path>/scripts/grade_research_init.py <eval-dir>
```

评分器读 `evals/evals.json` 的断言定义（目录结构 / brief 存在 / grilling 对齐 / 多 Agent Workflow / 批判视角 / 不过早深入源码），输出 `grading.json`。断言名与检查器映射见 `grade_research_init.py` 的 `ASSERTION_CHECKS`。

汇总多轮 benchmark：

```bash
python <skill-path>/scripts/aggregate_benchmark.py <workspace/iteration-N> --skill-name research-workflow
```

## 不可妥协规则（速查）

1. grilling 对齐强制不可跳过；对齐完成前不深入源码、不给结论。2. 所有结论基于当前仓库一手资料；二手资料显式标注。3. 不做行为等价验证。4. 全局与细节兼顾。5. 批判性外部视角对过时/不可持续设计显式标注。6. 编号主题目录 + 6 层结构（`.scratch/research/NN-topic/`）。7. 除非用户明确要求，不提交或推送。
