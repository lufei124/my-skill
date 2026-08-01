# UI 与 HTML 原型设计规范

状态：有效  
更新时间：2026-07-26  
适用范围：Life Reboots / NeoEpoch / S计划的移动端交互原型

## 读取入口

- [`prototype-html-design-spec.md`](prototype-html-design-spec.md)：把当前项目视觉基线转成单文件 HTML 原型可执行的颜色、布局、组件、状态和适配规则。
- [`reference-images/`](reference-images/)：用户确认的视觉参考图，统一使用 WebP 降低知识包体积，供原型 Agent 按需核对样式，不作为运行时依赖。

## 使用规则

1. 生成或迭代 Life Reboots 原型时，先读本索引和 `prototype-html-design-spec.md`，再只查看与本次页面相关的参考图。
2. 原型的交互、状态和业务规则仍以已确认需求摘要、决策账本及 `game-prototype` 契约为准；本模块只约束项目视觉和组件表达。
3. 参考图优先用于还原视觉语言，不要求逐像素复制。图中占位文本、人物、数值、图标和示例业务不得被当作正式需求。
4. 生成的 `02-prototype/index.html` 必须保持自包含；不得依赖本目录图片路径、网络图片、CDN 或构建工具才能运行。
5. 若用户为某次需求提供更新的 UI 稿或明确要求其他风格，本次需求以用户最新确认内容为准，并提出知识维护更新。

