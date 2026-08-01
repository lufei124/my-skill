# mobile-game-product-forge 真实能力回归基线

本基线用于验证 Skill 质量是否提升，而不只是验证文件、字段和门禁结构。它不新增流程状态、确认门或运行时依赖。

## 夹具

- `fixtures/routing-regression-cases.json`：24 条自然语言路由基线，覆盖根编排器、8 个子 Skill、正式流程、窄任务、显式入口、需用户澄清的场景，以及口语与中英混合输入。
- `fixtures/capability-regression-cases.json`：11 类真实需求，覆盖 L1 配置、L2 UI、L2 无 UI、L3 支付、历史迭代、来源冲突、独立评审、旧原型复用、多模块结构、图形选择和纯配置需求。
- `scripts/validate-regression-fixtures.py`：只校验夹具结构、覆盖和关键期望，不宣称自动评估模型生成质量。

### 路由夹具的输入风格约定

真实用户很少说教科书式的完整句。全是规范书面句的夹具即使全绿，也只证明「说明书式表达」能被正确路由，掩盖窄任务与正式流程的边界判定——而判错边界的代价正是写错需求目录或凭空发起状态源。

每条路由用例必须声明 `style`：

| style | 含义 | 例 |
|---|---|---|
| `textbook` | 规范书面句，通常自带「只…」等限定词 | 「只评审这份现有 PRD，不进入正式需求流程。」 |
| `colloquial` | 口语省略式：无完整主谓宾、无限定词、靠语境表达边界 | 「这份 prd 帮我挑挑毛病，别的先别动」 |
| `mixed_language` | 中英混合，含英文功能名或动词 | 「新做个 daily login reward，帮我把需求做完整」 |
| `explicit_invocation` | 显式调用（`$skill` / `/skill`），不经模型路由判断 | `$setup-mobile-game-product-forge` |

约定：

1. **新增路由用例时，口语类不少于三分之一**；只补规范书面句不算扩充覆盖。
2. 非 `textbook` 样本占比的**长期目标是 1/3**；每次运行 `validate-regression-fixtures.py` 会打印当前占比与目标，占比只允许升不允许降。
3. 脚本对 `colloquial`、`mixed_language` 和 `ambiguous_reference` 各有下限断言；提高覆盖后同步上调 `MIN_*` 常量，把已达成的水平锁住。
4. `ambiguous_reference` 类用例的期望是**请用户点选**（`executionMode=user_action_required` + `expectedBehavior`），不是路由到某个 Skill；这类用例守的是澄清行为本身。

## 执行方式

1. 使用同一 Agent、模型、项目知识版本和初始上下文，逐条执行 11 个能力场景。
2. 每个场景保存实际入口、读取文件、调研产物、原型/豁免、PRD、评审与校验结果。
3. 按下列指标记录结果；对比版本时不得只比较 Token 或耗时。
4. 路由基线可在 Claude Code、Codex 或 Cursor 中逐条人工冒烟，记录实际触发 Skill 与执行模式。

## 指标

| 指标 | 记录方式 | 硬性要求 |
|---|---|---|
| `criticalRuleOmissions` | 漏掉的支付、奖励、权限、幂等、补偿、异常或验收关键规则数 | 必须为 0 |
| `unsupportedInferences` | 无证据却写成已确认事实的结论数 | 必须为 0 |
| `clarifyingQuestionQuality` | 是否只询问会改变方案的关键问题 | 不得重复询问已确认事实 |
| `decisionRuleAcceptanceCoverage` | D-### → R-### → AC-### 的覆盖率 | 核心规则 100% |
| `prototypePrdDrift` | 已确认原型决策在 PRD 中遗漏或改变的数量 | required 路径必须为 0 |
| `reviewP0P1Findings` | 评审识别的有效 P0/P1 及漏检 | 不得漏掉预置重大风险 |
| `inputTokens` | Agent 实际输入 Token | 仅作效率对比，不得压过质量 |
| `elapsedSeconds` | 完成时间 | 仅作效率对比 |
| `filesRead` | 实际读取文件数 | 检查是否按需读取 |
| `fullHtmlReads` | 完整 HTML 读取次数 | 优先定向读取；证据不足时允许完整读取 |

## 硬失败条件

任一场景出现以下情况即判回归失败：

- 宽泛正式需求绕过根编排器；
- 正式需求跳过调研；
- required / not_applicable 判断错误，或取消产品负责人豁免证据；
- 使用“最新”但与当前/目标版本、地区或发布日期不匹配的外部资料；
- 把历史 PRD 当当前事实，或把当前缺陷当目标规则；
- 来源冲突时静默选边；
- required 历史最小 metadata 未回读证据就进入 PRD；
- 独立窄任务修改正式状态或宣称完整流程已完成；
- 多模块 PRD 按客户端/服务端/数据库/配置/埋点拆成技术层章节；
- 为形式完整机械生成全部图形，或用图替代规则和验收；
- 纯配置需求虚构运营后台页面、权限或发布流程；
- 关键规则遗漏、无依据推断或 D/R/AC 核心覆盖不完整。

## 回归记录模板

```text
版本：
模型 / Agent：
项目知识版本：
场景 ID：
实际入口 Skill：
执行模式：
复杂度：
原型适用性：
读取文件：
完整 HTML 读取次数：
关键遗漏：
无依据推断：
D/R/AC 覆盖：
原型与 PRD 漂移：
评审 P0/P1：
输入 Token：
耗时：
结论：PASS / FAIL
失败原因：
```
