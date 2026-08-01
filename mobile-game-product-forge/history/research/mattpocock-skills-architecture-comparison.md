# mobile-game-product-forge 与 mattpocock/skills 架构对比

更新时间：2026-07-24

## 实施进度

更新时间：2026-07-24

| 优先级 | 优化项 | 状态 | 落地结果 |
|---|---|---|---|
| P0 | 通用Skill与项目知识解耦 | 已完成 | Life Reboots 已迁移为 `knowledge-packs/life-reboots` 可选知识包 |
| P0 | 项目初始化Skill | 已完成 | 新增 `setup-mobile-game-product-forge`，支持 `core` 与 `core + life-reboots` |
| P0 | 安装边界 | 已完成 | 新增两套 `install-profiles`，core不包含项目知识 |
| P0 | 防覆盖与只读边界 | 已完成 | 初始化和知识包升级均不得覆盖项目已有知识 |
| P1 | 子Skill拆分 | 已完成 | 拆出 6 个可独立调用子 Skill，主 Skill 精简为轻量编排器 |
| P1 | 插件和统一安装器 | 已完成 | 新增 `.claude-plugin/plugin.json` 与 `scripts/install.sh` 跨 Agent 安装脚本 |
| P1 | 单一版本源与CI | 已完成 | `package.json` 唯一版本源、`CHANGELOG.md`、`scripts/validate.sh` 与 CI 工作流 |

## 结论

当前方案适合“一个强约束、端到端的移动游戏产品流程”，优势是业务规则集中、确认门完整、项目背景和埋点可直接使用。`mattpocock/skills` 更像“可组合的 Skill 产品线”，优势是独立 Skill 粒度、路由与初始化分离、跨 Agent 安装、版本发布和成熟度治理。

最佳方向不是照搬其多 Skill 数量，而是保留现有 Skill 作为兼容入口，逐步升级为“轻量编排器 + 少量可独立调用的子 Skill + 外置项目知识包”。

## 架构对比

| 维度 | 当前方案 | mattpocock/skills | 建议 |
|---|---|---|---|
| Skill 粒度 | 1个210行的端到端 Skill | 41个 Skill，按 engineering/productivity 等分桶；22个为推广集合 | 保留现入口，先拆4–6个真正有独立调用价值的子 Skill |
| 调用模型 | 一个 Skill 内部完成模式和阶段路由 | 区分 user-invoked 与 model-invoked，并用 `ask-matt` 做人工路由 | 明确编排器与自动触发子 Skill 的调用边界 |
| 项目初始化 | 安装后直接携带知识与默认约定 | 独立 `setup-matt-pocock-skills` 探测项目并写入项目级配置 | 新增一次性 setup Skill，选择知识包和文档目录 |
| 项目知识 | `knowledge/` 随 Skill 一起安装 | Skill 与项目的 `CONTEXT.md`、ADR、`docs/agents/` 分离 | 通用 Skill 与项目知识解耦，Life Reboots 作为可选知识包 |
| 安装升级 | Git源目录 + Agent软链接 | `skills.sh`复制安装、Claude插件订阅、维护者软链接脚本 | 提供统一安装脚本；再增加Claude插件和可选复制安装 |
| 发布版本 | Skill正文手工记录 `2.0.0` | package、插件清单、Changesets、GitHub Actions发布 | 建立单一版本源和自动一致性校验 |
| 成熟度 | 无正式draft/deprecated分层 | promoted、in-progress、deprecated、personal等分桶 | 增加stable/experimental/deprecated状态，但不要过度分桶 |
| 校验 | 当前以人工静态与行为回归为主 | 仓库规则约束清单、插件验证、发布工作流 | 建立CI：结构、链接、版本、元数据、行为场景 |

## 优先优化

### P0：拆开通用 Skill 与项目知识（已完成）

建议形成：

```text
skills/mobile-game-product-forge/
knowledge-packs/life-reboots/
```

默认安装通用 Skill；项目初始化时显式选择是否安装 Life Reboots 知识包。项目根目录自己的 `knowledge/` 始终优先。这样可以避免把项目敏感知识无条件分发给所有使用者。

### P0：增加 setup Skill（已完成）

新增一个仅人工触发的 `setup-mobile-game-product-forge`，负责：

- 识别 Codex、Claude、Cursor 和项目根目录
- 选择是否启用项目知识
- 创建或关联 `knowledge/INDEX.md`
- 确定 `docs/prd/`、`history/` 输出位置
- 写入 AGENTS.md 或 CLAUDE.md 的消费规则
- 验证 Skill 和知识版本

### P1：保留入口，拆少量子 Skill

保持 `mobile-game-product-forge` 为兼容编排器，优先拆分：

- `game-requirement-discovery`
- `game-prototype`
- `game-prd-writing`
- `game-prd-review`
- `game-analytics-design`
- `game-knowledge-maintenance-proposal`

只有能够被独立调用或被其他流程复用的能力才拆，不按章节机械拆分。

### P1：建立发布与安装层

- 增加 `package.json` 或独立版本清单作为唯一版本源
- 增加跨 Codex/Claude 的链接安装脚本
- 增加Claude插件清单
- 公开仓库时支持 `npx skills add <repo>`
- 区分“可编辑复制安装”和“只读订阅安装”

### P1：建立自动校验

至少检查：

- 每个已发布 Skill 都有 `SKILL.md` 和 `agents/openai.yaml`
- user/model invocation 配置跨 Agent 一致
- 所有相对引用存在
- 版本字段一致
- 项目知识默认只读
- 模式1、模式2、模式3行为回归
- 埋点去重和配置输出格式不回退

## 不建议直接照搬

- 不需要现在就拆成几十个 Skill；当前领域比通用工程流程更集中。
- 不要复制其“多份目录清单靠人工同步”的做法，应通过脚本生成或CI校验。
- 不要把项目知识写进通用插件包；应做可选知识包。
- 不要依赖正文中的手工版本号；应由发布清单生成。
- 对方仓库当前 `package.json` 为 `1.1.0`、Claude插件清单为 `1.2.0`，与其文档要求的同步约束不一致，说明仅写规则不足以防漂移，应使用自动检查。

## 一手来源

- 仓库总体结构、安装方式和设计理念：<https://github.com/mattpocock/skills>
- Claude插件清单：<https://github.com/mattpocock/skills/blob/main/.claude-plugin/plugin.json>
- 插件与Codex分发决策：<https://github.com/mattpocock/skills/blob/main/.agents/adr/0002-ship-as-a-claude-code-plugin.md>
- 调用类型规范：<https://github.com/mattpocock/skills/blob/main/.agents/invocation.md>
- 项目初始化Skill：<https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/SKILL.md>
- Skill编写原则：<https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-great-skills/SKILL.md>
- 本地链接脚本：<https://github.com/mattpocock/skills/blob/main/scripts/link-skills.sh>
- 发布工作流：<https://github.com/mattpocock/skills/blob/main/.github/workflows/release.yml>
