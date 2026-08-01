# Life Reboots HTML 原型设计规范

状态：有效  
更新时间：2026-07-26  
来源：用户确认的 6 张 UI 参考图  
用途：Life Reboots / NeoEpoch / S计划的单文件、可点击移动端 HTML 原型

## 1. 规范边界

本规范描述项目的原型视觉语言和常用组件。它不替代需求摘要、决策账本、交互原型确认门或正式 UI 设计稿。

执行优先级：

```text
已确认业务规则与交互
> 主流程和异常状态完整
> 本规范的组件语义
> 视觉接近参考图
> 装饰细节
```

- 参考图中的英文/中文占位文案、头像、NPC、属性名、数值、阵营徽章、Apple 登录和注销示例均不是默认业务需求。
- 参考图未标注的尺寸、渐变色和阴影只能做近似还原，不得伪装成精确设计参数。
- 本规范只约束 Life Reboots 项目原型，不得作为其他游戏的默认主题。

## 2. 视觉基调

- 类型：明亮、游戏化、轻卡通的高对比 UI，不使用通用后台、SaaS 或纯 Material 风格。
- 背景：页面外层以纯黑或深色场景承托；主要内容使用深海军蓝面板。
- 层级：浅蓝高光边框包住深蓝内容区；重要弹窗可使用顶部蓝色缎带标题。
- 强调：主操作以亮蓝渐变配金黄色描边；阵营或特殊强调使用黄橙色；危险操作使用红色。
- 质感：允许渐变、高光、双描边、内阴影和轻量粒子点缀，但装饰不能影响文字和状态辨识。
- 文字：标题粗体、正文清晰；主按钮文字可使用深蓝描边或阴影增强可读性。

## 3. 颜色令牌

参考图明确标注的颜色必须优先使用：

| 语义 | CSS 变量 | 色值 |
|---|---|---|
| 主色 / 亮蓝 | `--lr-primary` | `#02BCFF` |
| 紫色辅助 | `--lr-secondary-purple` | `#6210FF` |
| 深蓝辅助 | `--lr-secondary-blue` | `#0774D0` |
| 成功 | `--lr-success` | `#67C23A` |
| 警告 | `--lr-warning` | `#E6A23C` |
| 危险 | `--lr-danger` | `#FF4E4E` |
| 底部弹出层背景 | `--lr-sheet` | `#2C2C2E` |
| 黑底内容框 | `--lr-panel` | `#1A1C2B` |
| 二级页主内容框 | `--lr-surface-primary` | `#283856` |
| 二级页次内容框 | `--lr-surface-secondary` | `#202D45` |
| 基础黑 | `--lr-black` | `#000000` |
| 基础白 / 主文字 | `--lr-white` / `--lr-text-primary` | `#FFFFFF` |
| 次要文字 | `--lr-text-secondary` | `#B5B5B5` |
| 禁用按钮文字 | `--lr-text-disabled` | `#B2B2B2` |

可在单文件 HTML 顶部使用以下起始令牌。金色描边、浅蓝框和禁用面来自参考图近似值，可按页面整体观感微调：

```css
:root {
  --lr-primary: #02bcff;
  --lr-secondary-purple: #6210ff;
  --lr-secondary-blue: #0774d0;
  --lr-success: #67c23a;
  --lr-warning: #e6a23c;
  --lr-danger: #ff4e4e;
  --lr-sheet: #2c2c2e;
  --lr-panel: #1a1c2b;
  --lr-surface-primary: #283856;
  --lr-surface-secondary: #202d45;
  --lr-black: #000;
  --lr-white: #fff;
  --lr-text-primary: #fff;
  --lr-text-secondary: #b5b5b5;
  --lr-text-disabled: #b2b2b2;

  /* 从参考图近似提取，非精确交付值 */
  --lr-outline-gold: #ffd51f;
  --lr-outline-cyan: #8ee8ff;
  --lr-disabled-top: #85878d;
  --lr-disabled-bottom: #4c4e55;
  --lr-focus: #9beaff;
}
```

## 4. 页面与弹窗骨架

### 4.1 移动端基线

- 默认逻辑视口为 `393 × 852`、竖屏，同时适配较窄 Android 设备。
- 内容宽度使用 `min(100% - 24px, 560px)`；不得按参考图原始像素尺寸固定页面。
- 页面必须尊重安全区：顶部和底部使用 `env(safe-area-inset-*)` 回退值。
- 桌面浏览器可展示手机外框，但外框与评审工具栏不得混入正式游戏 UI。

### 4.2 主弹窗

- 内容区：深蓝面板，可使用细密棋盘格或径向渐变模拟纹理；纹理对比度必须低。
- 外框：浅蓝粗边框 + 内侧高光；圆角明显，避免普通白色卡片。
- 顶部缎带：用于选择、重要结果或高关注弹窗；标题置中，蓝色渐变、黄色细描边。
- 普通弹窗无需机械添加缎带；信息层级较低时使用深蓝标题区即可。
- 弹窗内部按“标题 → 说明/媒体占位 → 表单或列表 → 主操作”排列，主操作靠近底部。

推荐骨架：

```css
.lr-panel {
  width: min(calc(100% - 24px), 560px);
  color: var(--lr-text-primary);
  background:
    radial-gradient(circle at 25% 20%, rgb(255 255 255 / 4%) 0 1px, transparent 2px),
    linear-gradient(180deg, #121c4a, #11183f);
  border: 4px solid var(--lr-outline-cyan);
  border-radius: 28px;
  box-shadow: inset 0 0 0 2px rgb(255 255 255 / 35%), 0 16px 40px rgb(0 0 0 / 45%);
}
```

## 5. 按钮系统

### 5.1 语义

| 类型 | 用途 | 视觉 |
|---|---|---|
| 主按钮 | 当前页面最主要的前进/确认操作 | 亮蓝渐变 + 金色描边 |
| 阵营/特殊强调 | 阵营选择、特殊资源或强强调操作 | 黄橙渐变 + 金色描边 |
| 危险按钮 | 注销、删除等不可逆或高风险动作 | 红色渐变 + 金色描边 |
| 次按钮 | 取消、返回、并列的次要选择 | 蓝色或深色描边样式 |
| 弱化但可点 | 视觉降权但仍可操作 | 深色填充 + 亮青描边；不得伪装成禁用 |
| 禁用 | 条件不满足、处理中不可操作 | 灰色渐变 + 灰色描边 + 禁用文字 |

同一操作区通常只有一个主按钮。红色不得用于普通确认；灰色可点击按钮必须有亮青或金色边界，和真正禁用态明显区分。

### 5.2 尺寸与状态

- 长按钮：页面主操作，宽度占容器 `100%`，可限制最大宽度。
- 中/短按钮：并列操作或弹窗双按钮；窄屏时允许等宽换行。
- 列表小按钮：仅用于行内操作；视觉高度可较小，但可点击热区至少 `44 × 44px`。
- 主操作视觉高度建议 `48–56px`；圆角取高度的一半形成胶囊形。
- 正常态有明显顶部高光和底部深色压边。
- `:active` 下压 `1–2px` 并轻微降低高光，不改变布局尺寸。
- `:focus-visible` 必须显示清晰焦点环。
- Loading 保持按钮原尺寸，阻止重复点击并显示处理中反馈。
- 禁用必须同时设置原生 `disabled` 或 `aria-disabled="true"` 和事件拦截，不能只变灰。

推荐基础类：

```css
.lr-button {
  min-height: 48px;
  padding: 0 24px;
  border: 3px solid var(--lr-outline-gold);
  border-radius: 999px;
  color: #fff;
  font: 800 18px/1 system-ui, sans-serif;
  letter-spacing: .02em;
  text-shadow: 0 2px 0 #0751a5;
  background: linear-gradient(180deg, #43d4ff 0 38%, #079fe7 42%, #0074d5 100%);
  box-shadow: inset 0 2px 0 rgb(255 255 255 / 45%), 0 4px 0 #b76400;
  cursor: pointer;
}

.lr-button:active { transform: translateY(2px); box-shadow: inset 0 2px 4px rgb(0 0 0 / 25%); }
.lr-button:focus-visible { outline: 3px solid var(--lr-focus); outline-offset: 3px; }
.lr-button--warning { background: linear-gradient(#ffe754, #ff9d00); text-shadow: 0 2px 0 #b34200; }
.lr-button--danger { background: linear-gradient(#ff7868, #ef1717); text-shadow: 0 2px 0 #8f160d; }
.lr-button--quiet { border-color: var(--lr-primary); background: #06080d; color: #fff; }
.lr-button:disabled,
.lr-button[aria-disabled="true"] {
  border-color: #c3c4c7;
  color: var(--lr-text-disabled);
  background: linear-gradient(var(--lr-disabled-top), var(--lr-disabled-bottom));
  box-shadow: inset 0 2px 0 rgb(255 255 255 / 22%), 0 3px 0 #777;
  text-shadow: 0 1px 0 #333;
  cursor: not-allowed;
}
```

## 6. 标题、头像与关闭按钮

- 弹窗主标题居中、粗体、高对比；角色名可与圆形头像同一行。
- 头像为圆形裁切，使用浅色描边；头像只是身份辅助，名称必须保留文本。
- 选择类弹窗可使用“头像 + 角色/关系名 + 情境描述 + 问题 + 选项”结构。
- 关闭按钮位于弹窗右上方，红色圆形、金色双环、白色 `×`，热区至少 `44 × 44px`。
- 关闭按钮必须有 `aria-label="关闭"`，不得只依赖图形。
- 关闭前是否二次确认由业务规则决定，不因视觉样式自动增加。

## 7. 表单、列表与信息行

### 7.1 表单

- 标签使用白色粗体；输入框、下拉框使用 `--lr-surface-primary`。
- 边框使用低饱和蓝紫色，聚焦时改用亮青色。
- 占位文字使用次要文字色并保持足够对比。
- 下拉展开层与字段同宽；长选项换行，不横向溢出。
- 输入错误、禁用、Loading 和提交失败必须有文本或图标反馈，不能只换颜色。

### 7.2 NPC/角色列表

- 行结构优先为“圆形头像 + 名称/身份 + 右侧内容或操作”。
- 当前玩家或选中行可用 `--lr-surface-primary` 高亮；普通行保持深蓝底。
- 行间可使用低对比金色或蓝色分割线。
- 名称、身份和右侧内容须在窄屏下可换行或截断，禁止重叠。

### 7.3 键值信息

- 使用左右对齐的键值行；标签在左、值在右。
- 可用 `--lr-surface-primary` 与透明/深蓝交替分行，提高扫描性。
- 金额、时间和属性等必须保留单位；长值允许换行。

## 8. 属性条

### 8.1 通用属性条

- 左侧标签使用浅蓝标签块；中间为彩色进度/变化条；右侧黑底显示 `+65`、`−65` 等变化值。
- 轨道外层使用浅蓝和金色双重强调；填充值使用渐变和少量高光点。
- 不同属性允许使用蓝、紫、橙粉、灰蓝、靛蓝、粉、绿等稳定色系；同一属性跨页面必须保持同色。

### 8.2 阵营属性条

- 左侧标签改用浅黄色；填充使用黄橙、红橙或亮绿。
- 阵营徽章可压在进度边界附近，徽章仅作辅助；阵营名和数值仍须以文本呈现。
- 正负变化使用明确 `+` / `−`；多段变化时展示当前值、上限和变化量，避免只靠条长判断。

### 8.3 实现要求

- 使用真实数值驱动 `width` 或 CSS 自定义属性，不把条做成静态图片。
- `role="progressbar"` 时提供 `aria-valuemin`、`aria-valuemax`、`aria-valuenow`。
- 颜色不能成为唯一语义；标签、数值、符号或图标至少提供一种冗余表达。
- 动画控制在 `200–400ms`，并支持 `prefers-reduced-motion: reduce`。

## 9. 自包含 HTML 实现合同

1. HTML、CSS、JavaScript 全部内嵌到一个 `index.html`。
2. 参考图只用于设计核对；运行时不得引用本知识库路径。
3. 不依赖 CDN、网络字体、外部图标库或远程图片。
4. 组件样式集中定义并复用，推荐类名：`.lr-panel`、`.lr-ribbon`、`.lr-button`、`.lr-field`、`.lr-list-row`、`.lr-stat-bar`、`.lr-close`。
5. 人物图、徽章等正式素材未提供时，使用清楚标注的本地占位（首字母、CSS 图形或内嵌 SVG），不得擅自生成并冒充正式资产。
6. 评审工具栏使用中性深灰视觉，与正式游戏 UI 保持边界；不得套用蓝金游戏按钮造成混淆。
7. 所有可点击控件必须有实际模拟反馈；主流程不能停留在视觉稿。
8. 竖屏窄设备不得产生横向滚动，文字缩放后仍能完成核心操作。

## 10. 禁止模式

- 直接使用 Bootstrap/Material 默认组件或普通白色卡片代替项目视觉。
- 把所有按钮都做成同一颜色，导致主操作、危险、弱化和禁用无法区分。
- 仅靠降低透明度表达禁用，或让灰色可点击态与禁用态混淆。
- 为模仿参考图固定 `750px` / `1560px` 等原图宽度。
- 把参考图中的示例人物、文案、数值或 Apple 登录当作每个需求的默认内容。
- 为装饰加入过强霓虹、玻璃拟态、频繁闪烁或大面积粒子动画。
- 原型依赖知识库图片相对路径，导致复制 `index.html` 后失效。

## 11. 参考图索引

参考图以 WebP 保存以减少知识包体积；只影响存储格式，不改变其作为视觉核对证据的语义。

| 文件 | 主要用途 |
|---|---|
| [`reference-images/buttons-and-colors.webp`](reference-images/buttons-and-colors.webp) | 基础按钮语义、双按钮、阵营按钮和明确色值 |
| [`reference-images/button-states.webp`](reference-images/button-states.webp) | 长/中/短/列表按钮的蓝、黄、红、弱化、禁用状态 |
| [`reference-images/choice-dialog.webp`](reference-images/choice-dialog.webp) | 选择弹窗、缎带标题、头像关系名和多选项布局 |
| [`reference-images/modal-components.webp`](reference-images/modal-components.webp) | 弹窗骨架、媒体位、表单、NPC 列表、键值行和属性条组合 |
| [`reference-images/attribute-bars.webp`](reference-images/attribute-bars.webp) | 通用属性条与阵营属性条颜色和结构 |
| [`reference-images/close-button-dialog.webp`](reference-images/close-button-dialog.webp) | 详情弹窗、角色信息和右上关闭按钮 |

