# 安装与升级指南

本指南面向产品经理，覆盖装、升、排查三件事，全部命令可直接复制执行。日常怎么用（起需求、确认、评审）不在本文，见项目内 `docs/mobile-game-product-forge/operation-guide.md`。

使用 Codex 或 Cursor 的同事不走本文的插件方式，见仓库 `README.md`「方式二：安装脚本」。

## 1. 一次性配置（每台电脑只做一次）

### 1.1 前置：Python 3

流程中的机器门禁和 PRD 校验需要 Python 3。打开终端执行：

```bash
python3 --version
```

能输出版本号即可跳过。装不上时：macOS 执行 `xcode-select --install`；Windows 用 `winget install Python.Python.3` 或到 python.org 下载。

### 1.2 前置：Gitee SSH 访问

插件仓库是 Gitee 私有仓，安装和自动升级都走 SSH。逐条执行：

```bash
# ① 生成密钥（一路回车即可；已有 ~/.ssh/id_ed25519 则跳过本条）
ssh-keygen -t ed25519 -C "你的邮箱"

# ② 显示公钥，整行复制
cat ~/.ssh/id_ed25519.pub
```

③ 打开 Gitee 网页 → 头像 → 设置 → SSH 公钥 → 粘贴 → 确定。

```bash
# ④ 验证（第一次会问 yes/no，输 yes）
ssh -T git@gitee.com
```

看到 "Hi <你的用户名>" 即成功。

### 1.3 安装插件（两条命令）

```bash
claude plugin marketplace add git@gitee.com:xianlan---shanghai-g/mobile-game-product-forge.git
claude plugin install mobile-game-product-forge@fairyland-forge
```

验证：

```bash
claude plugin list
```

看到 `mobile-game-product-forge@fairyland-forge` 且 `Status: enabled` 即装好。重启 Claude Code 会话后生效。

### 1.4 项目初始化（每个游戏项目做一次）

在你的游戏项目根目录打开 Claude Code，输入：

```text
$setup-mobile-game-product-forge 初始化本项目
```

按提示选择知识档案、确认 `docs/prd/` 与 `history/` 位置、决定飞书是否为强制交付。需要飞书发布的，setup 会引导完成 lark-cli 安装与扫码授权（凭据存在系统钥匙串，不落文件）。

初始化完成后，日常操作说明就在你项目里：`docs/mobile-game-product-forge/operation-guide.md`。

## 2. 升级

**通常你什么都不用做。** 维护者发版后，Claude Code 启动时会后台刷新并自动升级，重启会话即用上新版。

想立即升级或确认版本时：

```bash
claude plugin update mobile-game-product-forge@fairyland-forge   # 手动升级（更新后重启会话生效）
claude plugin list                                               # 看当前版本号
```

升级只覆盖插件自身的缓存目录（`~/.claude/plugins/cache/` 下），**绝不会碰你项目里的 `knowledge/`、`history/`、`docs/prd/` 和飞书配置**——那些都在你的项目目录中，插件升级与它们无关。

## 3. 常见故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `marketplace add` 报权限/认证错误 | SSH 未配置或公钥没加到 Gitee | 走 1.2 节；`ssh -T git@gitee.com` 必须先通 |
| 装完没反应、技能不出现 | 未重启会话 | 重启 Claude Code 会话；仍无则 `claude plugin list` 确认已 enabled |
| 同事说升级了，我这版本没变 | ① 维护者未 bump 版本（推 commit ≠ 发版）② 本地未重启 | `claude plugin update mobile-game-product-forge@fairyland-forge` 手动拉一次再重启；仍旧版则找维护者确认是否已发版 |
| 流程中报"找不到 check-stage-gate.py"或门禁脚本路径错误 | 定位链四级全部落空（罕见） | 设置逃生舱环境变量指向插件目录后重试：`export MOBILE_GAME_PRODUCT_FORGE="$(ls -dt ~/.claude/plugins/cache/*/mobile-game-product-forge/*/ | head -1)"` |
| 门禁执行时报 python 相关错误 | Python 3 缺失 | 走 1.1 节 |
| 飞书发布报未授权 | lark-cli 未绑定或授权过期 | 在项目里重跑 `$setup-mobile-game-product-forge`，走飞书绑定环节 |

以上都解决不了时，把完整报错文本发给维护者，附上 `claude plugin list` 的输出。

## 4. 维护者视角（发版）

同事的自动升级只认版本号：发版必须 `bash scripts/release.sh <新版本>`（同步三处版本 + 断言 CHANGELOG + 全量校验），然后 commit 并推送。只推 commit 不 bump 版本，已安装用户永远不会升级。推送门禁用 `git config core.hooksPath scripts/githooks` 启用。
