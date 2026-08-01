#!/usr/bin/env bash
#
# Release entry point for multi-agent-project-skill.
#
# Bumps the single version source (package.json) and syncs it to
# .claude-plugin/plugin.json and SKILL.md, asserts CHANGELOG.md already has a
# released entry for the new version (no [Unreleased]-only release), then runs
# the full validator. Exits non-zero on any failure.
#
# Usage: bash scripts/release.sh <new-version>   e.g. bash scripts/release.sh 1.1.0
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo"

new_ver="${1:-}"
if [ -z "$new_ver" ]; then
  echo "usage: bash scripts/release.sh <new-version>" >&2
  exit 1
fi
if ! echo "$new_ver" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "version must be semver x.y.z, got: $new_ver" >&2
  exit 1
fi

echo "== sync version to $new_ver =="

# package.json (single "version" field at top level; sed preserves formatting)
sed -i.bak -E "s/\"version\": *\"[^\"]+\"/\"version\": \"$new_ver\"/" "$repo/package.json"
rm -f "$repo/package.json.bak"

# plugin.json
sed -i.bak -E "s/\"version\": *\"[^\"]+\"/\"version\": \"$new_ver\"/" "$repo/.claude-plugin/plugin.json"
rm -f "$repo/.claude-plugin/plugin.json.bak"

# SKILL.md 当前 Skill 版本
sed -i.bak -E "s/当前 Skill 版本：.{0,1}[0-9]+\.[0-9]+\.[0-9]+/当前 Skill 版本：v$new_ver/" "$repo/SKILL.md"
rm -f "$repo/SKILL.md.bak"

echo "  package.json / plugin.json / SKILL.md synced"

echo "== assert CHANGELOG entry =="
if ! grep -qE "^## \[$new_ver\]" "$repo/CHANGELOG.md"; then
  echo "CHANGELOG.md 没有 [$new_ver] 的已发布条目（## [$new_ver] - 日期）。" >&2
  echo "先把 [Unreleased] 段的变更转正为 ## [$new_ver] - <日期> 再发版。" >&2
  exit 1
fi
echo "  CHANGELOG [$new_ver] entry present"

echo "== full validation =="
bash "$repo/scripts/validate.sh"

if command -v claude >/dev/null 2>&1; then
  echo "== claude plugin validate =="
  claude plugin validate "$repo" || echo "  (claude plugin validate 非零，仅提示，不阻断)"
fi

echo
echo "PASS: release $new_ver prepared. 现在可 commit 并推送（需用户明确授权）。"
echo "  已安装用户只在 plugin.json version bump 后才会自动升级。"
