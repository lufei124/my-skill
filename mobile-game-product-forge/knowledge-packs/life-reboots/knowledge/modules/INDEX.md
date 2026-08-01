# 业务模块索引

更新时间：2026-07-26

本目录描述 Life Reboots 的业务模块边界、现状、目标架构、依赖和后续需求检查项。模块状态不等于版本需求状态；具体版本范围与来源见 [`../requirements/INDEX.md`](../requirements/INDEX.md)。

| 模块 | 状态 | 负责人 | 路径 | 核心依赖 |
|---|---|---|---|---|
| 剧本与核心玩法框架 | 迁移中 / 目标架构 | 李政融 | [`game-framework.md`](game-framework.md) | 事件、配置、NPC、数据 |
| 商业化 | 目标架构（部分能力已有埋点基线） | 纪伟 | [`commercialization.md`](commercialization.md) | 商品配置、支付平台、广告、账号、数据 |
| NPC 系统 | 目标架构 | 吴正伟 | [`npc-system.md`](npc-system.md) | 事件、资产、关系、AI、配置、日志 |
| 平台体验 | 目标架构（部分能力已存在） | 纪伟 / 李荣洋 | [`platform-experience.md`](platform-experience.md) | 账号、资源、首页、PV、网络、数据 |

## 新需求读取规则

1. 先读取需求所属模块。
2. 再读取模块引用的 `config/`、`analytics/` 和 `decisions/`。
3. 模块标记为“迁移中”时，必须同时写出现行兼容方案和目标架构接入方案。
4. 模块标记为“目标架构”时，不得因为尚未上线而忽略；若新需求背离，必须说明原因、影响和补偿迁移方案。
