#!/usr/bin/env bash
#
# Unified validator for multi-agent-project-skill.
# Runs P1 structure / version / link / metadata / invocation-config checks,
# plus skill-specific invariants (assets single-source, placeholder set,
# stacks .gitignore must not ignore .agent/, init self-test). Exits non-zero
# on any failure.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo"

fail() { echo "FAIL: $1" >&2; exit 1; }
py="$(command -v python3 || command -v python || true)"
[ -n "$py" ] || fail "python3/python is required for validation"

root_name="multi-agent-project-skill"

echo "== structure =="

# 1. Published skill has SKILL.md + agents/openai.yaml.
test -f "$repo/SKILL.md" || fail "root SKILL.md missing"
test -f "$repo/agents/openai.yaml" || fail "agents/openai.yaml missing"

echo "== version consistency =="

# 2. Single version source: package.json drives plugin.json and SKILL.md.
pkg_ver="$(grep -m1 '"version"' "$repo/package.json" | sed -E 's/.*"version": *"([^"]+)".*/\1/')"
[ -n "$pkg_ver" ] || fail "package.json has no version"

plugin_ver="$(grep -m1 '"version"' "$repo/.claude-plugin/plugin.json" | sed -E 's/.*"version": *"([^"]+)".*/\1/')"
[ "$plugin_ver" = "$pkg_ver" ] \
  || fail "plugin.json version '$plugin_ver' != package.json '$pkg_ver'"

skill_ver="$(grep -oE '当前 Skill 版本：.{0,1}([0-9]+\.[0-9]+\.[0-9]+)' "$repo/SKILL.md" | sed -E 's/.*当前 Skill 版本：.{0,1}([0-9]+\.[0-9]+\.[0-9]+).*/\1/' | head -1)"
[ "$skill_ver" = "$pkg_ver" ] \
  || fail "SKILL.md 当前 Skill 版本 '$skill_ver' != package.json '$pkg_ver'"

echo "  version: $pkg_ver (package.json = plugin.json = SKILL.md) OK"

echo "== plugin manifest =="

# 3. plugin.json must explicitly register the root SKILL.md with "./".
"$py" - "$repo/.claude-plugin/plugin.json" "$repo" "$root_name" <<'PY'
import json
import sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
repo = Path(sys.argv[2])
root_name = sys.argv[3]
data = json.loads(manifest_path.read_text(encoding="utf-8"))
if data.get("name") != root_name:
    raise SystemExit(f"plugin.json name '{data.get('name')}' != expected '{root_name}'")
skills = data.get("skills")
if isinstance(skills, str):
    skills = [skills]
if skills != ["./"]:
    raise SystemExit('plugin.json skills must be exactly ["./"]: explicit root registration')
if not (repo / "SKILL.md").is_file():
    raise SystemExit("root SKILL.md missing")
PY
echo "  plugin.json root registration OK"

# 3b. marketplace.json（同仓自托）：必须存在、可解析，且唯一插件条目
#     指向仓库自身（source "./"）、不写 version（版本解析统一落到 plugin.json）。
"$py" - "$repo/.claude-plugin/marketplace.json" "$root_name" <<'PY'
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if not data.get("name"):
    raise SystemExit("marketplace.json must declare a marketplace name")
plugins = data.get("plugins")
if not isinstance(plugins, list) or len(plugins) != 1:
    raise SystemExit("marketplace.json must list exactly the one plugin in this repo")
entry = plugins[0]
if entry.get("name") != sys.argv[2]:
    raise SystemExit(f"marketplace plugin entry name must be {sys.argv[2]}")
if entry.get("source") != "./":
    raise SystemExit('marketplace plugin entry source must be "./" (same-repo self-hosting)')
if "version" in entry:
    raise SystemExit("marketplace plugin entry must not pin version: resolution falls back to plugin.json")
PY
echo "  marketplace.json self-hosted entry OK"

echo "== invocation + yaml structure =="

# 4. agents/openai.yaml: top keys exactly {interface, policy}; three non-empty
#    interface leaves; allow_implicit_invocation is true|false.
f="$repo/agents/openai.yaml"
minInd=$(awk '{
  if (match($0, /^[[:space:]]*[a-z_]+:[[:space:]]*$/)) {
    pre=$0; sub(/[a-z_]+:[[:space:]]*$/, "", pre); ind=length(pre)
    if (m=="" || ind<m) m=ind
  }
} END{ print (m=="" ? -1 : m) }' "$f")
[ "$minInd" -ge 0 ] 2>/dev/null || fail "agents/openai.yaml: 无顶级父键（缺 interface: / policy:）"
topkeys=$(awk -v ind="$minInd" '{
  if (match($0, /^[[:space:]]*[a-z_]+:[[:space:]]*$/)) {
    pre=$0; sub(/[a-z_]+:[[:space:]]*$/, "", pre)
    if (length(pre)==ind) { s=$0; sub(/^[[:space:]]*/,"",s); sub(/:.*/,"",s); print s }
  }
}' "$f" | sort | paste -sd, -)
[ "$topkeys" = "interface,policy" ] || [ "$topkeys" = "policy,interface" ] \
  || fail "agents/openai.yaml: 顶级父键须恰好为 {interface, policy}，实际: {$topkeys}"
grep -Eq '^[[:space:]]*display_name:[[:space:]]*[^[:space:]]' "$f" \
  || fail "agents/openai.yaml: interface 段缺非空 display_name"
grep -Eq '^[[:space:]]*short_description:[[:space:]]*[^[:space:]]' "$f" \
  || fail "agents/openai.yaml: interface 段缺非空 short_description"
grep -Eq '^[[:space:]]*default_prompt:[[:space:]]*[^[:space:]]' "$f" \
  || fail "agents/openai.yaml: interface 段缺非空 default_prompt"
grep -Eq '^[[:space:]]*allow_implicit_invocation:[[:space:]]*(true|false)[[:space:]]*$' "$f" \
  || fail "agents/openai.yaml: policy 段 allow_implicit_invocation 须为 true 或 false"
echo "  agents/openai.yaml structure OK"

# 4b. Root SKILL.md name == plugin.json name == expected root name.
skill_name="$(grep -E '^name:' "$repo/SKILL.md" | head -1 | sed -E 's/^name:[[:space:]]*//')"
[ "$skill_name" = "$root_name" ] || fail "root SKILL.md name '$skill_name' != expected '$root_name'"
echo "  root name consistency OK"

echo "== references & scripts resolve =="

# 5. Root SKILL.md references/*.md links must resolve to real files.
root_refs="$(grep -oE '\]\((references/[^)]+)\)' "$repo/SKILL.md" | sed -E 's/.*\]\(([^)]+)\).*/\1/' | sort -u || true)"
while IFS= read -r p; do
  [ -n "$p" ] || continue
  [ -e "$repo/$p" ] || fail "SKILL.md: broken reference '$p'"
done <<< "$root_refs"
echo "  root SKILL.md references resolve OK"

# 6. SKILL-referenced scripts/* must exist.
while IFS= read -r scr; do
  [ -n "$scr" ] || continue
  [ -e "$repo/$scr" ] || fail "SKILL.md: 引用的脚本不存在: $scr"
done <<< "$(grep -oE 'scripts/[A-Za-z0-9_]+\.(py|sh)' "$repo/SKILL.md" | sort -u || true)"
echo "  SKILL-referenced scripts exist OK"

echo "== install profiles =="

# 7. install-profiles/core.yaml source_files paths must exist + declare it is a
#    validation checklist, not install config.
f="$repo/install-profiles/core.yaml"
test -f "$f" || fail "install-profiles/core.yaml missing"
grep -qF '校验清单，不驱动安装' "$f" \
  || fail "install-profiles/core.yaml: 缺少「校验清单，不驱动安装」声明"
srcs="$(grep -oE '^[[:space:]]*-[[:space:]]*"([^"]+)"' "$f" | sed -E 's/^[[:space:]]*-[[:space:]]*"([^"]+)".*/\1/' || true)"
while IFS= read -r p; do
  [ -n "$p" ] || continue
  [ -e "$repo/$p" ] || fail "install-profiles/core.yaml: source_files 路径不存在: $p"
done <<< "$srcs"
echo "  install-profiles source_files paths exist OK"

echo "== doc drift =="

# 8. README.md and AGENTS.md must mention each references/*.md and each key
#    script (prevent doc drift).
for f in "$repo"/references/*.md; do
  b="$(basename "$f")"
  grep -qF -e "$b" "$repo/README.md" || fail "README.md does not mention reference: $b"
  grep -qF -e "$b" "$repo/AGENTS.md" || fail "AGENTS.md does not mention reference: $b"
done
for s in scripts/validate.sh scripts/install.sh scripts/init_workspace.py scripts/release.sh scripts/doc-impact-check.sh; do
  grep -qF -e "$s" "$repo/README.md" || fail "README.md does not mention script: $s"
  grep -qF -e "$s" "$repo/AGENTS.md" || fail "AGENTS.md does not mention script: $s"
done
echo "  README.md and AGENTS.md mention all references and key scripts OK"

# 9. README.md must have an upgrade SOP section (prevents version fragmentation).
grep -qxF -e '## 升级' "$repo/README.md" \
  || fail "README.md: 缺少「## 升级」小节（无升级 SOP 会导致版本碎片化）"
for term in 'git pull' 'validate.sh' '用户数据边界'; do
  grep -qF -e "$term" "$repo/README.md" \
    || fail "README.md 升级小节缺少关键口径：$term"
done
echo "  README upgrade SOP OK"

echo "== ADR index =="

# 10. ADR README index must match actual .agents/adr/*.md files.
"$py" - "$repo/.agents/adr/README.md" "$repo/.agents/adr" <<'PY'
import re
import sys
from pathlib import Path

readme = Path(sys.argv[1]).read_text(encoding="utf-8")
adr_dir = Path(sys.argv[2])
indexed = set(re.findall(r'(\d{4}-[a-z0-9-]+)\.md', readme))
actual = {p.stem for p in adr_dir.glob("????-*.md")}
if not actual:
    raise SystemExit("no ADR files found in .agents/adr/")
missing_files = indexed - actual
if missing_files:
    raise SystemExit(f"ADR README indexes files that do not exist: {sorted(missing_files)}")
unindexed = actual - indexed
if unindexed:
    raise SystemExit(f"ADR files not indexed in README: {sorted(unindexed)}")
PY
echo "  ADR README index matches files OK"

echo "== assets single-source invariants =="

# 11. assets/skeleton/ must contain the key skeleton files.
for rel in \
  AGENTS.md CLAUDE.md README.md \
  docs/PROJECT_CONTEXT.md docs/ARCHITECTURE.md docs/DEVELOPMENT_RULES.md \
  docs/TESTING.md docs/DECISIONS.md docs/GLOSSARY.md \
  .agent/PROJECT_STATE.md .agent/TASK_BOARD.md .agent/FILE_LOCKS.md \
  .agent/TASK_HANDOFF.md .agent/AGENTS_REGISTRY.md \
  .agent/decisions/ADR-0000-template.md .agent/handoffs/HANDOFF-template.md \
  .agent/task-ids/.gitkeep; do
  test -e "$repo/assets/skeleton/$rel" \
    || fail "assets/skeleton/$rel missing (骨架不完整)"
done
echo "  assets/skeleton complete OK"

# 12. No stack .gitignore may ignore .agent/ (bookkeeping must be committed).
for stack in node python generic; do
  gi="$repo/assets/stacks/$stack/.gitignore"
  test -f "$gi" || fail "assets/stacks/$stack/.gitignore missing"
  if grep -nE '^[[:space:]]*\.agent/?[[:space:]]*$' "$gi" >/dev/null; then
    fail "assets/stacks/$stack/.gitignore 忽略了 .agent/（协作簿记必须入库）"
  fi
done
echo "  stacks .gitignore do not ignore .agent/ OK"

# 13. Placeholder set consistency: every {{VAR}} in assets/ must be provided by
#     init_workspace.py build_context (catches template typos / unsupplied vars).
"$py" - "$repo/assets" "$repo/scripts/init_workspace.py" <<'PY'
import re
import sys
from pathlib import Path

assets = Path(sys.argv[1])
script = Path(sys.argv[2]).read_text(encoding="utf-8")

# Vars provided by build_context: ctx["KEY"] = ... assignments.
provided = set(re.findall(r'ctx\["([A-Z_]+)"\s*\]', script))
# PROJECT_NAME / INIT_DATE / STACK are also set via dict literal or assignment;
# fall back to a known superset if regex misses the dict-literal form.
provided |= {"STACK", "PROJECT_NAME", "INIT_DATE"}

found = {}
for p in assets.rglob("*"):
    if not p.is_file():
        continue
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        continue
    for m in re.finditer(r"\{\{([A-Z_]+)\}\}", text):
        found.setdefault(m.group(1), set()).add(str(p.relative_to(assets)))

unknown = {v: files for v, files in found.items() if v not in provided}
if unknown:
    lines = []
    for v, files in sorted(unknown.items()):
        lines.append(f"  {{{{{v}}}}} in: {sorted(files)}")
    raise SystemExit(
        "assets/ contains placeholders not provided by build_context:\n"
        + "\n".join(lines)
        + "\n请在 init_workspace.py 的 build_context 补齐，或修正模板中的占位符拼写。"
    )
PY
echo "  placeholder set matches build_context OK"

echo "== python scripts =="

# 14. Python scripts compile and self-test passes.
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/ma-skill-pycache" \
  "$py" -m py_compile "$repo/scripts/init_workspace.py"
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/ma-skill-pycache" \
  "$py" "$repo/scripts/init_workspace.py" --self-test >/dev/null
echo "  init_workspace.py py_compile + self-test OK"

echo "== shell scripts =="

# 15. Shell scripts pass syntax check.
for s in scripts/validate.sh scripts/install.sh scripts/release.sh scripts/doc-impact-check.sh; do
  bash -n "$repo/$s" || fail "$s: 语法错误"
done
test -f "$repo/scripts/githooks/pre-push" && bash -n "$repo/scripts/githooks/pre-push" \
  || fail "scripts/githooks/pre-push missing or syntax error"
echo "  shell scripts syntax OK"

echo
echo "PASS: validation complete"
