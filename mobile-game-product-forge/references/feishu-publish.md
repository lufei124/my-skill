# 飞书发布参考

飞书发布是项目交付能力，不是 PRD 内容确认门。仅当 `delivery.required=true` 或用户显式要求发布时执行；发布成功/失败只更新 `delivery`，不得改变或回退 `prd.status=final`。PRD 完成与交付的阶段契约见 [stage-gates.md](stage-gates.md)。

本文件说明 `game-prd-publish` 与 `setup-mobile-game-product-forge` 飞书绑定环节使用的 `lark-cli` 命令与故障排查。所有飞书凭证由 `lark-cli` 在操作系统 keychain（macOS Keychain / Windows Credential Manager / Linux secret service）中管理，本 Skill 不读取、不存储任何 app_secret 或 token。

飞书 CLI 与配套 Skill 总览见 [larksuite/cli](https://github.com/larksuite/cli/blob/main/README.zh.md)：`lark-cli` 负责飞书云文档、云空间与画板操作；配套 skills（`lark-doc`、`lark-whiteboard` 等）在边缘场景按需用 `lark-cli skills read <name>` 读取当前 CLI 版本的指引，不要 grep 本地 SKILL.md 推断流程。

## 1. 安装飞书 CLI

```bash
npx @larksuite/cli@latest install
```

推荐同时安装配套 skills，便于 Agent 处理文档/云空间/知识库的边缘场景：

```bash
npx skills add larksuite/cli -y -g
```

源码安装（需 Go 1.23+ 与 Python 3）：克隆 [larksuite/cli](https://github.com/larksuite/cli) 后 `make install`。

## 2. 授权绑定

配置自建应用凭证（仅需一次）：

```bash
lark-cli config init
# Agent 模式新建配置
lark-cli config init --new
```

登录授权：

```bash
# 交互式登录，TUI 引导选择业务域与权限级别
lark-cli auth login

# 推荐的自动审批 scopes（发布常用）
lark-cli auth login --recommend

# Agent 模式：立即返回验证 URL，不阻塞
lark-cli auth login --domain drive,docs --no-wait
# 用户浏览器授权后恢复轮询
lark-cli auth login --device-code <DEVICE_CODE>
```

够用判定与增量授权见下文「状态与维护」：先用 `auth check` 判定本次动作所需 scope 是否齐全，够用就不重发授权；不足时按 `suggestion` 用 `auth login --scope "<缺失scope>"` 只补缺失 scope。

状态与维护：

```bash
lark-cli auth status     # 查看登录状态与已授权 scope
lark-cli auth check --scope "docx:document:create docx:document:write_only docx:document:readonly drive:file:upload space:folder:create" --json   # 结构化够用判定
lark-cli auth scopes     # 列出应用所有可用 scope
lark-cli auth list       # 列出所有已认证用户
lark-cli auth logout     # 登出并删除凭证
```

够用判定与增量授权：`auth status` 的 `user.scope` 是空格连成的超长串且可能 needs_refresh，**不要做字符串包含判定**，统一用 `auth check` 的结构化结果。`auth check` 返回示例：

```json
// 够用：
{"ok":true,"granted":["docx:document:create", ...],"missing":null}
// 不足：
{"ok":false,"granted":[...],"missing":["docx:document:create"],"suggestion":"lark-cli auth login --scope \"docx:document:create\""}
```

- 够用（`ok: true`）→ 不重复发起授权，直接进入业务动作。
- 不足（`ok: false`）→ 按 `suggestion` 执行 **仅补缺失 scope 的增量授权**，不重跑全量授权：

```bash
lark-cli auth login --scope "<缺失scope，空格分隔>"   # 可叠加 --recommend / --domain
```

凭证存储：OS 原生 keychain，不在文件系统中落地。

## 4. 项目配置文件

`<项目根目录>/.feishu-publish.json`（非密钥，建议加入 `.gitignore`）：

```json
{
  "target_folder_token": "可选，飞书云空间文件夹 token；留空建在 My Space",
  "title_prefix": "可选，文档标题前缀"
}
```

不得在此文件写入任何 token 或 secret。

## 5. 读取既有飞书文档（模式1 需求发现）

模式1（已有模块迭代）下，需求调研环节可请用户提供该模块现状飞书文档的 URL 或 token，用 `lark-cli docs +fetch` 读取正文，作为文档定义与历史证据；仍须按复杂度核验当前实际实现，不把文档直接当线上事实或目标规则。读取前同样先运行 `lark-cli skills read lark-doc`（不要 grep 本地 SKILL.md 推断流程）。

```bash
# 先读 lark-cli 自带的文档操作指引（与当前 CLI 版本匹配）
lark-cli skills read lark-doc

# 读全文，输出 Markdown
lark-cli docs +fetch \
  --doc "<飞书文档 URL 或 document_id>" \
  --doc-format markdown \
  --scope full \
  --format json
```

关键 flag（以 `lark-cli docs +fetch --help` 为准）：

- `--doc`：文档 URL 或 `document_id` / `node_token`。
- `--doc-format`：`markdown`（纯导出，便于阅读与归档）或 `xml`（保留 DocxXML 结构与 block id，默认）。
- `--scope`：`full`（全文，默认）、`outline`（仅标题大纲）、`section`（按标题锚点展开，需 `--start-block-id`）、`keyword`（按关键词搜文本，需 `--keyword`）、`range`（按 block id 区间）。
- `--detail`：`simple`（阅读，默认）、`with-ids`（便于 block 引用）、`full`（含样式与编辑元数据）。
- `--format json`：返回结构化结果，可用 `--jq` 精简；`--dry-run` 预览请求不执行。
- Risk: `read`（只读，不改动文档）。

找不到文档 URL 时先搜索：

```bash
lark-cli docs +search --query "模块名 关键词" --format json
```

未绑定 lark-cli 或未授权时不得静默跳过：先按第 1、2 节提示安装授权，或回退请用户直接粘贴文档正文。抓取到的文档若与知识库 `knowledge/requirements/<module>.md` 不重复，按「知识维护提案」归档（见 [project-knowledge.md](project-knowledge.md)），AI 不直接写入 `knowledge/`。

## 6. 发布命令

### 创建飞书云文档（Docx）

> 发布前先运行 `lark-cli skills read lark-doc` 读取与当前 CLI 版本匹配的文档操作指引（lark-cli 自带嵌入式 skill，含 XML/Markdown 格式与示例）。不要 grep 本地 SKILL.md 推断流程，以 `--help` 与 `lark-cli skills read lark-doc` 为准。

```bash
lark-cli docs +create \
  --doc-format markdown \
  --title "<PRD 标题>" \
  --content "$(cat <prd.md>)" \
  --parent-token "<folder_token，可省略>" \
  --format json
```

关键 flag（以 `lark-cli docs +create --help` 为准）：

- `--title`：文档标题；CLI 自动以 `<title>…</title>` 内嵌，无需手动内嵌。
- `--content`：文档正文；`--doc-format markdown` 时为 Markdown，默认 `xml` 支持更丰富的 DocxXML 块。
- `--parent-token`：父文件夹 token 或知识库节点 token，决定文档落在哪。
- `--parent-position`：如 `my_library`（我的空间），与 `--parent-token` 互斥；两者都不传则建在默认位置。
- `--format json`：返回结果含文档 URL 与 `document_id` / `node_token`；可用 `--jq` 精简输出。
- `--dry-run`：只打印请求不执行，用于预览。

查看所有 docs 快捷命令：`lark-cli docs --help`（含 `+create`、`+update`、`+fetch`、`+media-insert`、`+search` 等）。

### 在文档中插入画板/流程图

PRD 中的业务流程图、页面流转图、时序图、状态机图、模块关系图、数据流图等图示，用飞书原生画板能力写入文档，不本地渲染。先运行 `lark-cli skills read lark-doc` 读取画板协同指引（`<whiteboard>` 块、支持的图表类型与格式），以 `--help` 与该指引为准。

在 `docs +create` / `docs +update` 的正文里内联画板块即可，CLI 写入时自动展开：

```text
<whiteboard type="mermaid">
flowchart TD
    A[触发] --> B[操作]
    B --> C{校验}
</whiteboard>
```

- 可用 `type`：`mermaid`、`svg`、`plantuml`；代码已在本文件时用 `path="@diagram.mmd"` 引用。
- 思维导图、时序图、类图、饼图、甘特图优先 `mermaid`；其余自定义图形用 `svg`；复杂时序/架构用 `plantuml`。
- 复杂或已有画板需精细绘制/更新时，用 `lark-cli skills read lark-whiteboard` 读取画板 skill 指引，按其 `+query` / `+update` 流程操作（支持 Mermaid/PlantUML/SVG 与原生格式）；主 Agent 不直接创作复杂画板内容，按指引在需要时调度子代理或 `lark-whiteboard`。

### 嵌入用户提供的截图到飞书文档

原型截图等本地图片由用户提供，用 `lark-cli docs +media-insert` 插入已创建的飞书文档（先 `+create` 拿到 `document_id`，再逐张插入）：

```bash
lark-cli docs +media-insert \
  --doc "<document_id 或 URL>" \
  --file <screenshot.png> \
  --type image \
  --width 600 \
  --caption "商城页-默认状态" \
  --format json
```

关键 flag（以 `lark-cli docs +media-insert --help` 为准）：

- `--doc`：目标文档 URL 或 `document_id`。
- `--file`：本地图片/文件路径；>20MB 自动分片上传。
- `--type`：`image`（默认）或 `file`；`file` 可用 `--file-view card|preview|inline`。
- `--width` / `--height`：图片显示像素；只给一边则按原图比例自动算另一边。
- `--caption`：图片说明文字；`--align`：`left` / `center` / `right`。
- `--selection-with-ellipsis`：用正文文本（或 `start...end` 去歧义）定位插入位置；默认追加到文档末尾。`--before` 在匹配块之前插入。
- `--from-clipboard`：直接从系统剪贴板读图（macOS/Windows 自带，Linux 需 xclip/xsel/wl-paste）。
- Risk: `write`（改动文档，需已授权）；非高风险写，无需 `--yes`。

### 通用 API（兜底）

```bash
lark-cli api GET /open-apis/drive/v1/files
```

三层调用架构：快捷命令（`+` 前缀）、API 命令（自动生成）、通用 `api` 调用。输出格式：`--format json|pretty|table|ndjson|csv`。支持 `--dry-run` 预览。

## 7. 绑定探测与手动重绑

发布前探测（`game-prd-publish` 自动执行）：

```bash
# 1. 确认已登录
lark-cli auth status --json
# 2. 按本次发布动作所需 scope 判定够用
lark-cli auth check --scope "docx:document:create docx:document:write_only docx:document:readonly drive:file:upload space:folder:create" --json
```

`ok: true` → 直接发布，不重复发起授权；`ok: false` → 按 `suggestion` 执行 `auth login --scope "<缺失scope>"` 增量补授权后再发布。读既有飞书文档或搜文档时，把 scope 换成对应动作所需集（见 setup 第 6 节「动作所需 scope」）。

手动重绑（用户随时可操作，无需重跑 setup）：

- 重新授权：`lark-cli auth login`
- 切换应用：`lark-cli config init --new`
- 清除凭证：`lark-cli auth logout`

## 8. 故障排查

| 现象 | 处理 |
|---|---|
| `lark-cli: command not found` | 运行 `npx @larksuite/cli@latest install` |
| 未授权 / scope 不足 | 先 `lark-cli auth check --scope "<本次动作scope>" --json` 看缺失项；按 `suggestion` 执行 `lark-cli auth login --scope "<缺失scope>"` 增量补授权；仍不足时 `lark-cli auth login --recommend` 全量补授 |
| token 过期 | `lark-cli auth login` 重新授权 |
| `docs +create` 参数不确定 | `lark-cli docs +create --help` / `lark-cli schema` |
| 读取既有飞书文档失败 | 先 `lark-cli skills read lark-doc`；确认已授权 docs 读 scope；或回退请用户粘贴正文 |
| 图片插入文档失败 | `--doc` 用 `+create` 返回的 `document_id`；确认图片路径；不阻塞 PRD 终稿 |
