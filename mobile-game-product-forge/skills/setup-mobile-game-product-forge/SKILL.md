---
name: setup-mobile-game-product-forge
description: Use when the user explicitly wants to initialize or reconfigure a project for mobile-game-product-forge, choose a knowledge profile, or connect project-level PRD and knowledge directories.
disable-model-invocation: true
---

# 初始化移动游戏产品需求工坊

这是一次性、由用户主动触发的项目初始化流程。先探测、再展示、再确认、最后写入；不得在用户确认前修改项目。

## 目标

为目标项目配置两种安装档案之一：

- `core`：只使用通用 `mobile-game-product-forge`，不安装任何项目知识包。
- `core + life-reboots`：使用通用 Skill，并将 Life Reboots 知识包初始化到目标项目。

## 1. 探测

确定并展示：

- 目标项目根目录和 Git 仓库状态
- 当前 Agent：Codex、Claude Code、Cursor 或其他
- `AGENTS.md`、`CLAUDE.md`、`.cursor/rules/` 是否存在
- `knowledge/INDEX.md`、`docs/prd/`、`history/` 是否存在
- `docs/mobile-game-product-forge/operation-guide.md` 是否存在，是否与当前 Skill 指南一致
- 已安装的 `mobile-game-product-forge` 路径和版本
- 源仓库中是否存在 `knowledge-packs/life-reboots/PACK.md`
- 目标项目是否已存在同名知识文件或人工修改

不得把 Skill 仓库自身误认成目标游戏项目。无法确定目标根目录时必须询问。

## 2. 选择档案

一次只问一个问题，推荐项放在前面：

1. 选择 `core` 或 `core + life-reboots`。
2. 若项目已有知识库，确认是保留现状、只补缺失文件，还是仅建立引用。
3. 确认 `docs/prd/` 与 `history/` 交付位置（默认在项目根目录新建）。
4. 确认把当前 Skill 的 `operation-guide.md` 写入项目 `docs/mobile-game-product-forge/operation-guide.md`。
5. 确认飞书是否为项目强制交付策略：默认否；选择“否”不影响正式 PRD 流程完成，选择“是”才要求终稿后完成飞书交付。

## 3. 预览

写入前列出：

- 将创建的目录
- 将新增的文件
- 将修改的现有文件及具体区块
- 操作指南将新增、保持、更新还是因差异等待用户决定
- 检测到的冲突
- 明确不会修改的文件

等待用户明确确认。

## 4. 初始化

### core

- 保持通用 Skill 安装。
- 不复制 `knowledge-packs/`。
- 若用户需要空知识库，只创建项目级 `knowledge/INDEX.md` 和必要模块入口，并全部标为“待补充”。
- 建立或确认 `docs/prd/`、`history/` 交付位置。
- 将源仓库 `operation-guide.md` 复制到 `<项目根目录>/docs/mobile-game-product-forge/operation-guide.md`：缺失时新增；内容一致时跳过；内容不同时不静默覆盖，在预览中展示差异并由用户选择保留或更新。

### core + life-reboots

- 从源仓库 `knowledge-packs/life-reboots/knowledge/` 初始化到 `<项目根目录>/knowledge/`。
- 只新增缺失文件，不得覆盖已有文件。
- 同路径文件存在时先比较；内容不同则输出冲突清单和建议，不复制、不合并、不替换。
- 知识包版本与已装文件 manifest（相对路径 + sha256 前 8 位）写入独立安装回执 `knowledge/.installed-packs/life-reboots.md`，不得为了记录版本修改人工维护的 `knowledge/INDEX.md`。
- 知识包升级时读旧回执 manifest 区分 provenance：identical（未变）/ pack 改（包升级、目标自上次安装未变 -> 更新）/ 人工新增（目标有、包无 -> 不动）/ 人工改（目标与包及旧 manifest 都不同 -> 保留不覆盖）；旧回执无 manifest 时向后兼容逐文件比对。
- 安装回执已存在且内容不同时，同样只报告差异，不覆盖。
- 项目后续人工修改不自动回写知识包或安装回执。
- 知识包升级同样只生成差异，不得覆盖项目知识。

### 操作指南与项目规则文件

操作指南是面向产品经理和协作角色的项目文档，不是 Agent 规则。初始化完成后必须告诉用户指南路径，并给出“如何启动第一个正式需求”的提示词。用户后续询问怎么开始或继续时，优先引导其读取该项目内指南。

不在目标项目写入 `AGENTS.md`、`CLAUDE.md` 或 `.cursor/` 等 Agent 规则文件。项目的 `mobile-game-product-forge` 使用入口由通用 Skill 的可发现性与全局注册承担；知识库、`docs/prd/`、`history/` 位置通过目录结构与安装回执体现，不依赖项目级规则文件。

## 5. 验证

完成标准：

- 通用 Skill 的 `SKILL.md` 可被目标 Agent 发现
- 选择 `core` 时，项目没有因本次初始化获得 Life Reboots 知识
- 选择 `core + life-reboots` 时，项目存在 `knowledge/INDEX.md`，且无已有文件被覆盖
- 项目内未新增或修改 `AGENTS.md`、`CLAUDE.md`、`.cursor/` 等规则文件
- `docs/prd/` 和 `history/` 位置明确
- 项目内存在 `docs/mobile-game-product-forge/operation-guide.md`，或差异冲突已明确等待用户处理
- 初始化结果明确告诉用户操作指南路径和启动第一个正式需求的命令
- 输出安装档案、Skill版本、知识包版本、创建/修改/跳过/冲突文件清单

存在任何未解决冲突时，结果必须标为“部分完成，待人工处理”，不得称为完整初始化。

任一条件未满足时报告实际状态，不得称为初始化完成。

## 6. 飞书交付策略与绑定

先记录用户选择的项目交付策略。`delivery_required=false` 时可以不绑定飞书，正式 PRD 在终稿且校验通过后完整结束；`delivery_required=true` 时再运行绑定探测。所有飞书凭证由 `lark-cli` 在操作系统 keychain 中管理，本 Skill 不读取、不存储任何 app_secret 或 token。

绑定判定遵循「探测 → 够用不发 → 不够增量授权 → 未绑定重申请」四态：以 `lark-cli auth check --scope "<本次动作所需 scope>" --json` 的结构化 `ok` / `missing` 为唯一够用判定依据，不得解析 `auth status` 的 `user.scope` 长串做字符串包含判定（该字段可能 needs_refresh、口径漂）。

### 动作所需 scope

按用户目标能力集（可多选）取并集，setup 时按用户打算启用的能力判定：

- 发布发布物（`docs +create` / `docs +media-insert`）：`docx:document:create docx:document:write_only docx:document:readonly drive:file:upload space:folder:create`
- 读既有飞书文档（`docs +fetch`）：`docx:document:readonly`
- 搜文档（`docs +search`）：`search:docs:read`

### 探测

- `lark-cli` 是否安装（命令是否可调用）。
- `lark-cli auth status --json`：是否已登录（`identities.user.available` 为真；`tokenStatus` 即便 `needs_refresh` 也视为已绑定，下次调用会自动刷新）。
- 已登录时按用户目标能力集所需 scope 跑 `lark-cli auth check --scope "<动作scope>" --json`，读 `ok` / `missing` / `suggestion` 判定够用。

### 绑定流程（四态）

1. **未安装 `lark-cli`**：提示用户执行 `npx @larksuite/cli@latest install`，并推荐 `npx skills add larksuite/cli -y -g`。
2. **已安装但未配置应用**：提示执行 `lark-cli config init`；Agent 上下文内需 `--force-init` 或改用 `lark-cli config bind`。
3. **已配置应用但未登录**：走首次扫码授权（流程见下方「扫码授权」）。
4. **已登录且 scope 够用**（`auth check` 返回 `ok: true`，`missing` 为空）：**不重复发起授权**，直接进入 `.feishu-publish.json` 写入与后续步骤。
5. **已登录但 scope 不足**（`auth check` 返回 `ok: false`，`missing` 非空）：按 `suggestion` 执行 **仅补缺失 scope 的增量授权** `lark-cli auth login --scope "<missing>"`（可叠加 `--recommend` / `--domain`），不要求用户重跑全量授权；扫码流程见下方。
6. **沙箱或 CI 环境下 keychain 不可访问**：提示用户在自有交互终端运行 `lark-cli config keychain-downgrade`（将主密钥物化为本地文件，安全折损：同用户的其他进程可读该文件），再重试上述扫码流程，不擅自执行。
7. 写入非密钥项目配置 `<项目根目录>/.feishu-publish.json`（见下方格式），并提示用户将其加入 `.gitignore`。

### 扫码授权

首次授权与增量补授权统一走同一扫码流程：

```bash
# 取 verification_url 与 device_code（不阻塞）
lark-cli auth login --no-wait --json --scope "<所需或缺失 scope>"
# 终端输出 ASCII 二维码
lark-cli auth qrcode "<verification_url>" --ascii
# 或生成 PNG 图片
lark-cli auth qrcode "<verification_url>" --output feishu-login.png
# 用户扫码后完成授权轮询
lark-cli auth login --device-code <DEVICE_CODE> --scope "<所需或缺失 scope>"
```

向用户展示二维码（ASCII 或 PNG），提示用飞书 App 扫码完成授权。首次全量授权可省略 `--scope`（用 `--recommend`），增量补授权须带 `auth check` 返回的缺失 scope。

### 项目配置文件格式

```json
{
 "delivery_required": false,
 "target_folder_token": "可选，飞书云空间文件夹 token；留空则建在 My Space",
 "title_prefix": "可选，文档标题前缀"
}
```

该文件只存非密钥偏好，不得写入任何 token 或 secret。

### 手动重绑

用户可随时自行操作，无需重跑完整 setup：

- 重新授权：`lark-cli auth login`
- 切换应用：`lark-cli config init --new`
- 清除凭证：`lark-cli auth logout`
- 查看状态：`lark-cli auth status`

### 完成标准

- 项目交付策略已明确为必需或非必需，并记录在非密钥项目配置；非必需时允许不创建配置文件，正式需求状态默认 `delivery.required=false`。
- 策略为必需时，`lark-cli auth status` 显示已登录，且 `auth check` 对用户目标能力集所需 scope 返回 `ok: true`；否则结果标为部分完成并给出补齐指引。
- 已登录且 scope 够用时**未重复发起授权**；scope 不足时**仅申请缺失 scope**（按 `auth check` 的 `suggestion` 增量补授权），不重跑全量授权。
- 扫码授权流程已向用户展示二维码（ASCII 或 PNG），用户已扫码或明确选择跳过。
- keychain 不可访问时已提示用户在交互终端执行 `keychain-downgrade`，未擅自执行安全降级。
- `.feishu-publish.json` 已写入或用户明确选择不写入。
- 未在任何文件中写入飞书密钥。

## 7. 初始化完成后的用户提示

完成后必须用可直接执行的形式告诉用户：

```text
初始化状态：完整完成 / 部分完成
操作指南：docs/mobile-game-product-forge/operation-guide.md
正式 PRD：docs/prd/
过程材料：history/

开始第一个正式需求：
使用 $mobile-game-product-forge 开始一个正式需求。
需求名称：…
初始想法：…
已有材料：…
负责人：…
```

若用户只询问“以后怎么用”，不要重复初始化；直接指向项目内操作指南，并给出新需求启动或中断恢复提示词。
