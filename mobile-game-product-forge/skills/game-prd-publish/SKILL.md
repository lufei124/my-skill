---
name: game-prd-publish
description: Use explicitly only when the root mobile-game-product-forge orchestrator delegates required delivery of a finalized PRD, or when the user explicitly asks only to publish an already-final PRD to Feishu. Never use for drafting, reviewing, or deciding whether a PRD is final.
---

# 游戏 PRD 发布与交付

负责移动游戏需求工坊的「PRD 发布与交付」环节。把已终稿的 PRD 发布为飞书云文档（Docx），写入交付记录。

本子 Skill 是 `mobile-game-product-forge` 的能力拆分。需求处理模式、确认门、版本号和共享工作目录由编排器持有；正式编排时本子 Skill 只读阶段状态并验证门禁，不修改跨阶段状态。

## 前置条件

1. PRD 状态=`final` 且校验状态=`passed`（`07-prd-final.md` 或编排器指定的终稿文件）。
2. 飞书已绑定：`lark-cli` 已安装、已登录，且 `lark-cli auth check` 对发布所需 scope 返回 `ok: true`。未绑定时不得擅自发布，先输出绑定指引（见 [../references/feishu-publish.md](../../references/feishu-publish.md)）并停止。
3. 终稿不含未确认的占位符：读 `06-lint-report.md`「占位符」节，或重跑 `scripts/lint-prd.py <终稿>`。仍有「待补充截图」时**停止发布**，逐条列出页面-状态，请产品负责人选择补图后再发或显式确认「按现状发布」；确认内容与时间写入交付记录。不得静默发布带占位符的终稿，也不得因占位符改写或回退 `prd.status=final` 与校验结论——占位符只拦交付，不改 PRD 状态。

本 Skill 只负责项目交付，不确认 PRD 内容，也不是第四个产品确认门。`delivery.required=false` 时正式编排不调用本 Skill；`required=true` 时发布成功/失败只更新 `delivery`，不得修改或回退 `prd.status=final`。

## 正式流程门禁

正式编排调用时，发布前读取 `00-stage-state.json` 并执行 `check-stage-gate.py --target publish`。该门禁继承正式需求的调研、需求摘要、原型确认或豁免、评审和校验证据；`NOT_REQUIRED` 时停止且明确项目无需飞书交付，`BLOCKED/INVALID_STATE` 时只输出门禁结果，`PASS` 才执行发布。

用户明确“只发布”时可作为 `narrow_task` 独立调用，但仍必须直接验证 PRD 确为终稿、存在通过的校验证据和真实终稿文件；无法验证时停止，不得以文件名含 `final` 代替门禁证据。

## 输入

```text
PRD 终稿文件（markdown）
+
项目交付偏好（<项目>/.feishu-publish.json，可选：目标文件夹 token、标题前缀）
+
创建人信息（Git user.name 或当前用户）
```

## 发布流程

### 1. 绑定探测

按「探测 → 够用不发 → 不够增量授权 → 未绑定重申请」四态判定，不得用 `auth status` 的 `user.scope` 长串做字符串包含判定（口径漂、可能 needs_refresh），以 `auth check` 的结构化 `ok` / `missing` 为唯一够用依据。

- `lark-cli` 未安装或 `lark-cli auth status --json` 显示未登录：停止发布，输出对应安装/配置/授权命令（见 [../references/feishu-publish.md](../../references/feishu-publish.md)），列为待确认项，不静默跳过。
- 已登录：按本次「发布」动作所需 scope（`docx:document:create docx:document:write_only docx:document:readonly drive:file:upload space:folder:create`）跑
  `lark-cli auth check --scope "<发布scope>" --json`：
  - `ok: true`（`missing` 为空）→ 够用，**不重复发起授权**，直接进入第 2 步。
  - `ok: false`（`missing` 非空）→ 读 `suggestion` 输出 **仅补缺失 scope 的增量授权命令** `lark-cli auth login --scope "<missing>"`，停止发布并列为待确认项，不要求用户重跑全量授权。

### 2. 发布飞书云文档（Docx）

- 先运行 `lark-cli skills read lark-doc` 读取与当前 CLI 版本匹配的文档操作指引（不要 grep 本地 SKILL.md）。
- 若 PRD 含流程/状态/架构等图示，按 [../references/feishu-publish.md](../../references/feishu-publish.md)「在文档中插入画板/流程图」用飞书原生画板块写入（Mermaid/SVG/PlantUML），不本地渲染；图片（原型截图等）用 `docs +media-insert` 插入。
- 执行（标题用 `--title`，CLI 自动内嵌 `<title>`；文件夹用 `--parent-token`）：

```bash
lark-cli docs +create \
  --doc-format markdown \
  --title "<PRD 标题>" \
  --content "$(cat <prd.md>)" \
  --parent-token "<folder_token，可省略>" \
  --format json
```

- 从 JSON 结果解析文档 URL 与 `document_id` / `node_token`。
- `.feishu-publish.json` 的 `target_folder_token` 映射到 `--parent-token`；留空则建在默认位置（或用 `--parent-position my_library`）。
- 具体参数以 `lark-cli docs +create --help` 为准。

### 3. 写入交付记录

在共享工作目录写 `08-delivery-record.md`，包含发布审计字段与结果：

```text
飞书文档 URL：
飞书 node_token：
发布时间：（带时区 ISO 8601）
使用的 Skill：mobile-game-product-forge
Skill 版本：（随包发布，见 package.json）
需求处理模式：
发布状态：成功 / 部分成功 / 失败
待确认项：
```

随后交由编排器更新 `delivery.status`：成功=`published`，失败=`failed`；需求目录中的变更记录按需更新。不得把单次需求记录误写到 Skill 仓库根 `CHANGELOG.md`，不得改变 PRD 终稿状态。

## 文档来源信息

交付记录是独立审计产物，可保留创建时间、Skill 版本、模式和发布结果等详细字段；PRD 正文仍按主 `SKILL.md` 使用文末一行紧凑生成记录。

## 完成与交接

- 发布成功：输出飞书文档 URL 与 `node_token`。
- 部分成功：明确哪一步失败、已完成的产物、待确认项，记录 `delivery.status=failed` 或 `in_progress`；PRD 保持 `final`。
- 全部失败：输出失败原因与重试命令，记录 `delivery.status=failed`，不写入“成功”的交付记录，不回退 PRD。
- 密钥零经手：本 Skill 不读取、不存储任何飞书 app_secret 或 token；所有凭证由 lark-cli 在 OS keychain 中管理。
- 独立调用（窄任务）：只发布到飞书时直接输出发布结果与交付记录，不修改正式 PRD 状态或 Skill 仓库根 `CHANGELOG.md`。

## 参考

- 阶段状态与硬门禁：[../references/stage-gates.md](../../references/stage-gates.md)

- 飞书 CLI 安装、授权、发布命令与故障排查：[../references/feishu-publish.md](../../references/feishu-publish.md)
- 交付文件模板：[../references/templates.md](../../references/templates.md)
