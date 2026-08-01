#!/usr/bin/env bash
# release.sh - 标准发版入口：同步三处版本 + 断言 CHANGELOG + 全量校验。
#
# 用法: bash scripts/release.sh <x.y.z>
#
# 插件用户的自动升级只认 plugin.json 的 version（版本解析：plugin.json ->
# marketplace 条目 -> commit SHA；本仓 marketplace 条目刻意不写 version）。
# 只推 commit 不 bump 版本，已安装用户永远不会升级——发版必须走本脚本。
# 本脚本不自动 commit/push。
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
new="${1:-}"

if ! [[ "$new" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "用法: bash scripts/release.sh <x.y.z>" >&2
  exit 1
fi

old="$(grep -m1 '"version"' "$repo/package.json" | sed -E 's/.*"version"[^"]*"([^"]+)".*/\1/')"
if [ "$new" = "$old" ]; then
  echo "新版本与当前版本相同（${old}），无需发版" >&2
  exit 1
fi

if ! grep -q "^## \[$new\]" "$repo/CHANGELOG.md"; then
  echo "CHANGELOG.md 缺少 '## [$new]' 条目。" >&2
  echo "先把 [Unreleased] 内容转正为：## [${new}] - $(date +%F)，再重跑本脚本。" >&2
  exit 1
fi

py="$(command -v python3 || command -v python || true)"
[ -n "$py" ] || { echo "python3/python is required" >&2; exit 1; }

"$py" - "$repo" "$old" "$new" <<'PY'
import json
import re
import sys
from pathlib import Path

repo, old, new = Path(sys.argv[1]), sys.argv[2], sys.argv[3]

for rel in ("package.json", ".claude-plugin/plugin.json"):
    p = repo / rel
    text = p.read_text(encoding="utf-8")
    if json.loads(text).get("version") != old:
        raise SystemExit(f"{rel} 当前版本不是 {old}，先跑 validate.sh 排查版本漂移")
    p.write_text(text.replace(f'"version": "{old}"', f'"version": "{new}"', 1),
                 encoding="utf-8")

skill = repo / "SKILL.md"
text = skill.read_text(encoding="utf-8")
updated, n = re.subn(r"当前 Skill 版本：`[^`]+`", f"当前 Skill 版本：`{new}`", text, count=1)
if n != 1:
    raise SystemExit("SKILL.md 未找到「当前 Skill 版本」行")
skill.write_text(updated, encoding="utf-8")
print(f"synced: package.json / plugin.json / SKILL.md -> {new}")
PY

bash "$repo/scripts/validate.sh"
if command -v claude >/dev/null 2>&1; then
  (cd "$repo" && claude plugin validate .)
fi

echo ""
echo "版本 $old -> $new 已同步并通过校验。下一步："
echo "  git add -A && git commit -m \"release: v$new\" && git push"
echo "推送后，已安装插件的同事会在 Claude Code 后台刷新时自动升级。"
