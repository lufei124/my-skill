# 平台与基础体验模块

更新时间：2026-07-26  
状态：目标架构；部分基础能力已上线  
负责人：纪伟 / 李荣洋

## 1. 账号注销

- 入口归入“设置 → 账户与服务 → 账户注销”。
- 状态机为“正常 → 注销冷静期 → 已注销”。
- 当前需求定义 14 天冷静期；冷静期内重新登录可取消注销并恢复正常。
- 冷静期结束后的清理、新账号创建和第三方授权处理由服务端负责。
- 14 天属于当前需求规则，但实际发行时必须复核目标市场合规要求。

## 2. 首页侧边栏

- 侧边栏由配置控制开关、地区、排序、标题、图标、横幅和路由。
- 可见入口按优先级降序、ID 升序排列。
- 社媒关注/领奖类入口完成全部奖励后永久隐藏。
- 地区来源“GeoIP 或注册地”尚未统一，新需求必须明确权威来源。

## 3. 资源下载

- 首包资源下载支持统一总进度。
- 移动网络下载前需要流量确认。
- 下载过程可使用背景轮播，但图片数量、停留时长和资源内容属于运营配置。
- 下载失败、完成和确认弹窗复用现有埋点基线。

## 4. PV

- 所有 PV 都允许用户跳过，不区分首次播放或具体 PV。
- 播放开始时展示跳过入口。
- 长时间无操作可自动隐藏，点击屏幕再次唤起。
- 跳过保留二次确认，避免误触。

## 5. 公告、邮件、震动

公告/邮件样式优化和剧情震动开关已进入 v1.0.5 需求范围，但当前总览未提供完整最终规则。后续需求可将其视为已确认方向，不得假设具体 UI、文案或默认开关状态。

## 6. 公共网络层

网络异常统一由客户端公共网络层处理，业务模块不得各自实现一套网络态 UI。详细规则见 [`../decisions/network-state-prompts.md`](../decisions/network-state-prompts.md)。

## 7. 新需求检查

- 是否涉及账号状态、登录、注销、订阅或恢复购买。
- 是否复用侧边栏、资源中心、PV 和公共网络层。
- 是否需要地区/平台配置、多语言和埋点。
- 是否影响冷启动、首包下载和新手流失。
- 是否存在目标市场合规差异。

## 8. 来源

- [账号注销](https://uvidumfqwzk.feishu.cn/wiki/X8xvwRNT4iDEdbkB0bzc8OkCntc)，抓取 revision 460
- [首页侧边栏](https://uvidumfqwzk.feishu.cn/wiki/UAa3w8yxxiHl5XkbI8ocVB5WnEd)，抓取 revision 128
- [资源下载](https://uvidumfqwzk.feishu.cn/wiki/WLJGw9atyiLxlpkhu6BcmsqXnkg)，抓取 revision 36
- [PV 跳过](https://uvidumfqwzk.feishu.cn/wiki/WIJBwaAO0i8YCckegufcphq1nBf)，抓取 revision 220
- [v1.0.5 当前版本总览](https://uvidumfqwzk.feishu.cn/wiki/W2GTwbPf8iYNqZkgKV8cb3Bzn8d)，抓取 revision 241
