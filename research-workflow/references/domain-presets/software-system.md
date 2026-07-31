# 领域预设：software-system（通用软件模块/系统/流程）

本预设适用于对软件项目中的模块、子系统或数据流程进行深度调研与设计批判 —— 例如认证鉴权模块、计费系统、ETL/数据管道、缓存层、消息总线、配置中心等。

使用方式：`create_research_skeleton.py <topic> --preset software-system`，或在 grilling 阶段 0 选定本预设。

## 角色特化

通用角色原型（见 `team-roles.md`）在本预设中特化为以下团队：

| 通用原型 | software-system 特化角色 | 产出文件 |
|---|---|---|
| 资料考古员 | 源码考古员 | `01-raw-findings/source-inventory.md` |
| 场景切片员 | 用例切片员 | `01-raw-findings/usage-slices.md`、`02-perspectives/actor-stories.md`（终端用户/调用方视角） |
| 机制抽象师 | 机制抽象师 | `01-raw-findings/mechanisms.md`、`02-perspectives/system-stories.md` |
| 方案设计师 | 架构/方案设计师 | `03-design-options/abstraction-options.md`、`03-design-options/extension-surface.md`（插件/配置扩展面） |
| 创作者视角评审员 | 可扩展性评审员 | `03-design-options/creator-perspective.md`、`02-perspectives/operator-stories.md`（运维/SRE/集成方视角） |
| 横向验证员 | 横向验证员 | `04-redteam-review/cross-check-report.md` |
| 现代实践评审员 | 现代工程实践评审员 | `03-design-options/modern-practice-review.md`、`04-redteam-review/modern-challenges.md` |
| 体验与留存评审员 | 开发者/运维体验评审员 | `03-design-options/experience-review.md`、`04-redteam-review/experience-risks.md` |
| 价值与增长评审员 | 成本与可持续性评审员 | `03-design-options/value-review.md`、`04-redteam-review/value-risks.md` |

> 额外建议角色（按需在 grilling 中启用）：安全评审员（涉鉴权/数据）、性能评审员（涉吞吐/延迟）、数值/容量评审员（涉配额/限流）。

终审组（评审委员会 5 人）：用例切片员、架构/方案设计师 1 人、可扩展性评审员、现代工程实践评审员、成本与可持续性评审员 → `05-synthesis/final-report.md`。

## 产出层级

直接使用通用 6 层，文件命名按上表。无需重命名层级。

- `02-perspectives/`：`actor-stories.md` = 终端用户/调用方视角；`system-stories.md` = 系统内部自动触发视角；`operator-stories.md` = 运维/SRE/集成方视角。
- `03-design-options/`：承载重写/重构/抽象的设计输入与风险。

## grilling 追加问题

选定本预设后，在通用 grilling 问题基础上追加确认：

- **技术维度权重**：是否需要安全 / 性能 / 容量 / 可维护性 / 可观测性 等技术视角？哪些最重要？
- **重构边界**：如果目标是为重写/重构做输入，本次是否只产出设计输入、不直接输出接口契约或可落地代码？（推荐是）
- **调用方范围**：actor 视角覆盖哪些调用方（终端用户、上游服务、内部任务、运维操作）？
- **遗留约束**：是否有必须保留的对外契约、数据格式或部署形态约束？

## brief 增量

`--preset software-system` 时，`create_research_skeleton.py` 会把 `references/domain-presets/software-system.brief.md` 的内容注入到 `00-brief/brief.md` 的目标与范围章节，强调：基于当前仓库一手源码、引入现代工程实践/开发者体验/成本可持续性视角、本次止步于设计输入层不输出可直接落地的接口契约。

## 批判性视角建议

- 现代实践对照：对标当前主流开源方案与工程实践（设计模式、协议、可观测性标准等）。
- 开发者/运维体验：API 易用性、错误诊断、部署与配置负担、文档完备度。
- 成本与可持续性：运行成本、维护成本、技术债、社区/生态可持续性。
- 安全（按需）：鉴权、授权、数据保护、注入与越权风险。
- 性能（按需）：吞吐、延迟、资源占用、瓶颈与扩容路径。
