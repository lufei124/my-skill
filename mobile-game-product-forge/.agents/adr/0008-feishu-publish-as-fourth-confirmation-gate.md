# ADR-0008：飞书发布升为第四道确认门

- 状态：已被取代
- 被 [ADR-0009](0009-separate-prd-completion-from-delivery.md) 取代：飞书改为项目交付策略，不再是产品确认门或 PRD 完成条件。
- 日期：2026-07-26
- 关系：增补 [ADR-0004](0004-confirmation-gates-ironclad.md)（确认门为铁律不变；门数由 3 扩到 4）

## 背景

ADR-0004 确立三个确认门（需求理解、交互原型、评审争议）为铁律。ADR-0002 确立 PRD 经 lark-cli/飞书云文档发布、非本地 PDF。

发布动作在机制层早就是硬门：`stage-gates.md` 门矩阵含 `publish`、`check-stage-gate.py` 有 `target=publish` 且退出码 0/2/3、`game-prd-publish` 在正式编排下执行 `check-stage-gate.py --target publish`、其 `openai.yaml` default_prompt 写"require the publish gate to pass"。

但叙事层长期把发布定为「可选、非确认门」（根 `SKILL.md`、`README.md`、`workflow.md` §10、`operation-guide.md`、`game-prd-publish` 前置条件段），与机制层自相矛盾，且与「最终 PRD 需在飞书呈现」的产品定位冲突：飞书是最终呈现处（流程/状态/架构图用飞书原生画板写入，不本地渲染，见 `references/feishu-publish.md`「在文档中插入画板/流程图」），若发布可选，则「最终呈现」无强制保证。

## 决定

1. 飞书发布升为**第四道强制确认门**（PRD 发布确认门），与 ADR-0004 三门并列，共为铁律。
2. 门契约：`check-stage-gate.py --target publish` 保持「可发布前置」语义（PRD=已终稿 + 校验=通过 + 终稿文件存在）；发布成功且用户确认后，根编排器把 `prd.status` 由「已终稿」推到「已发布」。
3. 流程完成以 `prd.status=已发布` 为准；未发布不算流程完成。**不新增额外完成门**（状态词已足够表达，避免过度门禁）。
4. `docs/prd/` 本地同步在终稿后、发布前完成（本地权威源，校验通过即同步），与飞书发布并存、不互替。
5. 窄任务「只发布」仍可独立调用 `game-prd-publish`，但不冒充完整流程完成。
6. 未绑飞书或发布失败时停止，输出绑定/重试指引，不静默跳过。

## 备选

- 加独立「完成门」（publish 之后再一道 done 门）：被否。`prd.status=已发布` 已是机器可读完成标志，再加门属冗余、增加状态机复杂度。
- 发布门含交付记录文件校验（`08-delivery-record.md` 存在 + 发布状态字段）：被否为本门硬契约。交付记录由 `game-prd-publish` 流程内保证、`stage-gates.md` §7 一致性检查覆盖；门禁脚本只判前置状态，不解析交付记录内容，保持脚本零依赖与职责单一。
- 维持「可选」定位：被否。与「飞书是最终呈现处」的产品定位矛盾，且机制层已是硬门，叙事层不对齐会持续误导。

## 影响

- 根 `SKILL.md`、`AGENTS.md`、`README.md`、`operation-guide.md`、`references/workflow.md` §10、`game-prd-publish/SKILL.md` 的「可选/非确认门」叙事统一改为「第四确认门」。
- `references/templates.md` §4 `prd.status` 词表「已发布」补语义说明；`references/stage-gates.md` §3/§7/§8 补第四门与「已发布」一致性。
- `scripts/check-stage-gate.py` self-test 补 publish 用例（PASS + BLOCKED）。
- 未绑飞书的项目无法走完正式流程；这是预期行为（飞书是最终呈现处），`game-prd-publish` 已有绑定探测与停止逻辑。
- ADR-0004 结论「确认门为铁律」不变；本 ADR 仅扩门数 3->4，不取代 0004。
