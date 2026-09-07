# 参考来源与适用边界

## v1.0.0 附带的仓库核对记录（本轮沿用）

原包记录的核对日期：2026-09-07；参考分支：`main`。以下 S1–S15 沿用 v1.0.0 的来源说明，本轮 v1.1.0 没有重新审计这些源码。原包记录为读取官方文档、插件设计说明及关键源码，未完成整仓库克隆、未锁定 commit SHA、未执行原仓库测试。因此不应理解为本轮重新完成了源码核验或可复现构建锁定。

来源根地址：

```text
https://github.com/anthropics/commerce-agents
```

| 编号 | 已读取的参考文件 | 主要支持的内容 |
|---|---|---|
| S1 | [README.md](https://github.com/anthropics/commerce-agents/blob/main/README.md) | 双角色、运行路径、能力开关、参考实现边界 |
| S2 | [CLAUDE.md](https://github.com/anthropics/commerce-agents/blob/main/CLAUDE.md) | 单模型拥有对话、规则分层、领域中立核心 |
| S3 | [commerce-architecture/SKILL.md](https://github.com/anthropics/commerce-agents/blob/main/plugins/commerce-builder/skills/commerce-architecture/SKILL.md) | 主循环、Backend、Skills、委托边界 |
| S4 | [execution.py](https://github.com/anthropics/commerce-agents/blob/main/commerce-common/commerce_common/execution.py) | `BaseToolExecutor`、分发、异常处理与委托结果校验 |
| S5 | [docs/safety.md](https://github.com/anthropics/commerce-agents/blob/main/docs/safety.md) | 代码安全门、运行时差异、部署方责任 |
| S6 | [docs/backends.md](https://github.com/anthropics/commerce-agents/blob/main/docs/backends.md) | 身份凭证、流程顺序、幂等提示、缺失数据 |
| S7 | [commerce-trust-safety/SKILL.md](https://github.com/anthropics/commerce-agents/blob/main/plugins/commerce-builder/skills/commerce-trust-safety/SKILL.md) | 来源与所有权区别、记忆边界、拒绝状态 |
| S8 | [commerce-ui-tools/SKILL.md](https://github.com/anthropics/commerce-agents/blob/main/plugins/commerce-builder/skills/commerce-ui-tools/SKILL.md) | 呈现工具、模型解释、事实字段、服务端填充 |
| S9 | [commerce-prompt-caching/SKILL.md](https://github.com/anthropics/commerce-agents/blob/main/plugins/commerce-builder/skills/commerce-prompt-caching/SKILL.md) | 静态/动态分离与缓存稳定性 |
| S10 | [fencing.py](https://github.com/anthropics/commerce-agents/blob/main/commerce-common/commerce_common/fencing.py) | 输入清洗与固定围栏 |
| S11 | [grounding.py](https://github.com/anthropics/commerce-agents/blob/main/commerce-common/commerce_common/grounding.py) | `GroundingRule`、预取条件、首个匹配规则 |
| S12 | [commerce-evals/SKILL.md](https://github.com/anthropics/commerce-agents/blob/main/plugins/commerce-builder/skills/commerce-evals/SKILL.md) | 夹具、结果断言、对抗/正常对照与回归策略 |
| S13 | [merchant_agent/gates.py](https://github.com/anthropics/commerce-agents/blob/main/merchant-agent/core/merchant_agent/gates.py) | `check_apply_change` 的来源、护栏和审批检查 |
| S14 | [scaffold-commerce-agent.md](https://github.com/anthropics/commerce-agents/blob/main/plugins/commerce-builder/commands/scaffold-commerce-agent.md) | 先调研、回放方案、接入状态、决策记录 |
| S15 | [review-commerce-agent.md](https://github.com/anthropics/commerce-agents/blob/main/plugins/commerce-builder/commands/review-commerce-agent.md) | 现有 Agent 证据定位与逐项差距评审 |

用户提供的《AI Agent 架构复用指南——基于 Anthropic Claude Commerce Agents 的拆解与跨产品套用方法论》作为二次解读参考，采用其 P1–P10 分类；未将原文打包，使用本 Skill 不依赖该附件。

## 与二次解读保持区分的地方

- 双角色是这个参考项目的组织方式，不是所有产品必须拥有两个 Agent。
- “壳和桥 100% 复用”不作为工程承诺；接口、类型、授权、运行时和测试都需按项目适配。
- 统一工具执行器不代表 Grounding、分析和记忆提取在三条路径完全等价。
- Fencing、来源门和 Grounding 不能推出“杜绝所有注入/幻觉/越权”。
- UI 中事实字段由服务端填充，但模型可提供选择、顺序、理由和备注。
- “所有规则都不该在 Prompt”“每产品必有两个角色”“固定 8–15 个接口”“固定代码行数”“零成本迁移”等不设为本 Skill 的约束。
- 可信审批绑定摘要、失效重批、持久幂等、未知结果核验，以及通用状态机等属于本 Skill 的生产加固建议；没有宣称参考仓库已完整实现。
- 参考仓库提供评测设计指导和单元测试，不等于随仓库提供了可直接覆盖所有项目的通用 eval harness。[S12]

## 本 Skill 的改写范围

从原仓库“面向电商角色进行搭建/改造”改为“读取任意当前项目并生成方案”；不自动实施，不默认写入项目的 `CLAUDE.md`，不强制导入原包，也不自动拷贝原流程 Skills。

本包是重新编写的说明、模式摘要和模板，不包含原仓库源码或原始 Skill 文件，不是 Anthropic 官方插件。原仓库 README 标示 Apache-2.0，且声明其为不维护的参考实现；采用其代码时另行处理依赖版本与许可要求。[S1]

## Skill 格式与本地发现位置

以下仅用于本包的结构和安装说明，不是 Agent 业务方案的依据：

- [Agent Skills specification](https://agentskills.io/specification)：`SKILL.md` 元数据与按需参考文件。
- [Claude Code skills](https://code.claude.com/docs/en/skills)：项目级 `.claude/skills/` 与用户级 `~/.claude/skills/`。
- [Codex skills](https://developers.openai.com/codex/skills/)：项目级 `.agents/skills/` 与用户级 `~/.agents/skills/`；核对时此地址跳转至官方 Build skills 文档。

安装位置取决于宿主及版本；本包没有执行安装、注册或实际项目行为测试。


## v1.1.0 新增约束与文档核验

修订日期：2026-09-07。用户本次明确要求：“优化下skill 要求用Claude Agent SDK 除非用户明确要求不用”。默认必须 SDK 是据此制定的 Skill 规则，不宣称来自 commerce-agents。原仓库保留三条运行路径的历史描述，不作为本 Skill 的无约束选型菜单。

新增文档来源：

| 编号 | 来源 | 本轮核对范围 |
|---|---|---|
| S16 | [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) | SDK 与 Client SDK/CLI 的区别；循环、上下文、Python/TypeScript、会话与子 Agent |
| S17 | [Agent SDK quickstart](https://code.claude.com/docs/en/agent-sdk/quickstart) | 包名、基本入口、二进制/运行依赖说明；不锁定安装版本 |
| S18 | [Give Claude custom tools](https://code.claude.com/docs/en/agent-sdk/custom-tools) | 进程内 MCP、自定义工具注册、工具集与自动批准列表的区别 |
| S19 | [Configure permissions](https://code.claude.com/docs/en/agent-sdk/permissions) | SDK 工具权限机制；不将它替代业务授权 |
| S20 | [Other LLM gateways](https://code.claude.com/docs/en/llm-gateway) | 网关协议要求；不据此宣称任意非 Claude 模型均受支持 |
| S21 | [Hosting the Agent SDK](https://code.claude.com/docs/en/agent-sdk/hosting) | 官方检索片段中的子进程、凭证与并发部署要求；无容量实测 |
| S22 | [DeepSeek Anthropic API](https://api-docs.deepseek.com/guides/anthropic_api/) | Anthropic 格式兼容文档及字段差异；未实测 SDK 闭环 |
| S23 | [阿里云百炼 Anthropic 兼容 Messages](https://help.aliyun.com/zh/model-studio/anthropic-api-messages) | 兼容接口、地域/业务空间、模型与鉴权差异；未实测 SDK 闭环 |
| S24 | [火山方舟：其他工具](https://www.volcengine.com/docs/82379/2374473) | 官方检索摘要显示特定 Agent Plan 产品支持 Anthropic/OpenAI 协议；动态正文未完整读取，不确定其具体端点、全部模型和生产用途 |

TypeScript 完整 API 参考整页读取失败，未据此锁定 API 签名、选项组合或 SDK 版本。需要精确参数时，以目标项目依赖版本及当时官方文档为准。包内 `providerProfile` 是设计草案，不是 SDK 原生配置接口，也不是可运行代码。

本次没有安装或运行 Claude Agent SDK，没有调用付费模型、验证三家供应商接入、测量成本或部署真实业务。兼容性测试条目是后续实施的验收设计。
