---
id: life-reboots
name: Life Reboots Project Knowledge
version: 1.3.0
updated_at: 2026-07-26
---

# Life Reboots 知识包

适用项目：`Life Reboots`、`NeoEpoch`、`S计划`

本知识包与通用 `mobile-game-product-forge` Skill 分离。只有用户在项目初始化时选择 `core + life-reboots`，才将 `knowledge/` 内容安装到目标项目。

1.2.0 起，知识入口采用“项目整体背景 → 模块索引 → 模块知识/配置/数据/决策/需求来源”的结构。未上线但已经确认的后续需求标记为“目标架构”，后续新需求必须检查对齐和迁移影响，不得误写为已上线能力。

1.3.0 起，新增项目级 `ui/` 模块，保存用户确认的视觉参考图，并提供单文件 HTML 原型可执行的颜色、组件、状态和移动端适配规范。参考图只作为设计核对来源，不成为原型运行时依赖。

安装规则：

- 目标：`<项目根目录>/knowledge/`
- 默认不覆盖已有文件
- 发生同路径冲突时生成差异并等待人工决定
- 安装完成后，目标项目知识库保持只读消费、人工维护
- 知识包升级不得直接覆盖项目已维护内容

知识入口：`knowledge/INDEX.md`
