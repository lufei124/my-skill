#!/usr/bin/env bash
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
core="$repo"
setup="$repo/skills/setup-mobile-game-product-forge"
pack="$repo/knowledge-packs/life-reboots"
profiles="$repo/install-profiles"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

test -f "$core/SKILL.md" || fail "core SKILL.md missing"
test -f "$pack/PACK.md" || fail "Life Reboots pack manifest missing"
test -f "$pack/knowledge/INDEX.md" || fail "Life Reboots knowledge index missing"
test -f "$profiles/core.yaml" || fail "core install profile missing"
test -f "$profiles/core-life-reboots.yaml" || fail "Life Reboots install profile missing"
if grep -Eq 'knowledge-packs' "$profiles/core.yaml"; then
  fail "core profile includes a project knowledge pack"
fi
grep -Eq 'knowledge-packs/life-reboots' "$profiles/core-life-reboots.yaml" ||
  fail "Life Reboots profile does not select its knowledge pack"
test ! -e "$repo/knowledge/INDEX.md" || fail "project knowledge is still bundled at core knowledge/"
if [ -d "$repo/knowledge" ]; then
  fail "core repo carries a root knowledge/ dir; project knowledge must live in knowledge-packs/ only"
fi
test ! -e "$repo/references/project-context-life-reboots.md" || fail "project context is still inside core references/"
test ! -e "$repo/references/analytics-life-reboots.md" || fail "project analytics is still inside core references/"

test -f "$setup/SKILL.md" || fail "setup skill missing"
test -f "$setup/agents/openai.yaml" || fail "setup Codex metadata missing"
grep -Eq '^disable-model-invocation: true$' "$setup/SKILL.md" ||
  fail "setup skill is not user-invoked for Claude"
grep -Eq 'allow_implicit_invocation: false' "$setup/agents/openai.yaml" ||
  fail "setup skill is not user-invoked for Codex"
grep -Eq 'core' "$setup/SKILL.md" || fail "setup skill does not offer core profile"
grep -Eq 'core \+ life-reboots' "$setup/SKILL.md" ||
  fail "setup skill does not offer Life Reboots profile"
grep -Eq '不得覆盖|不覆盖' "$setup/SKILL.md" ||
  fail "setup skill lacks non-overwrite protection"
grep -Eq 'knowledge/\.installed-packs/life-reboots\.md' "$setup/SKILL.md" ||
  fail "setup skill lacks a non-invasive knowledge-pack receipt"
if grep -Eq '知识包版本记录在项目 `knowledge/INDEX\.md`' "$setup/SKILL.md"; then
  fail "setup skill still modifies the project knowledge index for version receipt"
fi
grep -Eq '未解决冲突.*部分完成' "$setup/SKILL.md" ||
  fail "setup skill does not downgrade unresolved conflicts to partial completion"

grep -Eq '项目根目录.*knowledge/INDEX.md' "$core/SKILL.md" ||
  fail "core skill does not prioritize project knowledge"
if grep -Eq 'references/(project-context-life-reboots|analytics-life-reboots)\.md' "$core/SKILL.md"; then
  fail "core skill still hardcodes Life Reboots reference files"
fi

# Self-test: the Life Reboots reference guard above must actually match a real
# .md path. A previous double-escape (\\.) made rg match "backslash + any
# char" instead of a literal dot, so the guard never fired and leaked project
# knowledge into core undetected. Fail loudly if the regex ever regresses.
printf 'see references/project-context-life-reboots.md\n' \
  | grep -Eq 'references/(project-context-life-reboots|analytics-life-reboots)\.md' \
  || fail "life-reboots guard regex no longer matches a real .md path (regression)"

echo "PASS: P0 architecture is separated and setup is discoverable"
