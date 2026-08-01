#!/usr/bin/env bash
#
# Unified validator for research-workflow.
# Runs P1 structure / version / link / metadata / invocation-config checks,
# plus skill-specific invariants (domain-presets paired + PRESETS consistent,
# evals.json valid + assertion names registered, references complete,
# skeleton + grader self-tests). Exits non-zero on any failure.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo"

fail() { echo "FAIL: $1" >&2; exit 1; }
py="$(command -v python3 || command -v python || true)"
[ -n "$py" ] || fail "python3/python is required for validation"

root_name="research-workflow"

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

# 5. Root SKILL.md references/*.md links must resolve to real files (or dirs).
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

# 8. README.md and AGENTS.md must mention each generic reference, the
#    domain-presets directory, and each key script (prevent doc drift).
for f in "$repo"/references/*.md; do
  b="$(basename "$f")"
  grep -qF -e "$b" "$repo/README.md" || fail "README.md does not mention reference: $b"
  grep -qF -e "$b" "$repo/AGENTS.md" || fail "AGENTS.md does not mention reference: $b"
done
grep -qF -e "domain-presets" "$repo/README.md" \
  || fail "README.md does not mention references/domain-presets/"
grep -qF -e "domain-presets" "$repo/AGENTS.md" \
  || fail "AGENTS.md does not mention references/domain-presets/"
for s in scripts/create_research_skeleton.py scripts/grade_research_init.py scripts/aggregate_benchmark.py scripts/validate.sh scripts/install.sh scripts/release.sh scripts/doc-impact-check.sh; do
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

echo "== references single-source invariants =="

# 11. Generic references completeness: the four domain-agnostic references.
for rel in \
  references/grilling-questions.md \
  references/team-roles.md \
  references/output-structure.md \
  references/workflow-template.md; do
  test -f "$repo/$rel" || fail "$rel missing（通用参考不完整）"
done
echo "  generic references complete OK"

# 12. domain-presets paired: every <name>.md has a <name>.brief.md and vice
#     versa (the research-workflow analog of template completeness).
"$py" - "$repo/references/domain-presets" <<'PY'
import sys
from pathlib import Path

d = Path(sys.argv[1])
md = {p.stem for p in d.glob("*.md") if not p.name.endswith(".brief.md")}
brief = {p.stem[:-len(".brief")] for p in d.glob("*.brief.md")}
only_md = md - brief
only_brief = brief - md
if only_md:
    raise SystemExit(f"domain-presets 缺 brief 配对: {sorted(only_md)}（每个 <name>.md 须配 <name>.brief.md）")
if only_brief:
    raise SystemExit(f"domain-presets 缺说明配对: {sorted(only_brief)}（每个 <name>.brief.md 须配 <name>.md）")
if not md:
    raise SystemExit("domain-presets 无任何预设（至少应内置 game-mud / software-system）")
PY
echo "  domain-presets paired OK"

# 13. PRESETS consistency: PRESETS keys (minus 'none') == domain-presets .md
#     basenames; each preset's brief_include file must exist. Imports the module
#     to read the real runtime PRESETS (it references DEFAULT_SUBDIRS by name,
#     so ast.literal_eval cannot resolve it; the module guards on __main__).
"$py" - "$repo/scripts/create_research_skeleton.py" "$repo/references/domain-presets" <<'PY'
import importlib.util
import sys
from pathlib import Path

script = Path(sys.argv[1])
preset_dir = Path(sys.argv[2])

spec = importlib.util.spec_from_file_location("_rw_skeleton", script)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
presets = mod.PRESETS

keys = set(presets.keys())
if "none" not in keys:
    raise SystemExit("PRESETS 必须含 'none'（纯通用默认）")

actual_md = {p.stem for p in preset_dir.glob("*.md") if not p.name.endswith(".brief.md")}
declared = keys - {"none"}
if declared != actual_md:
    raise SystemExit(
        f"PRESETS 声明的预设 {sorted(declared)} != domain-presets 文件 {sorted(actual_md)}："
        f"新增预设须同时改 PRESETS 与 domain-presets/（成对）"
    )

# Each preset with brief_include must point to an existing fragment.
for name, spec_obj in presets.items():
    inc = spec_obj.get("brief_include")
    if not inc:
        continue
    if not (preset_dir / inc).is_file():
        raise SystemExit(f"PRESETS[{name!r}].brief_include 指向的文件不存在: {inc}")
PY
echo "  PRESETS consistent with domain-presets OK"

echo "== evals + grader invariants =="

# 14. evals/evals.json must be valid JSON with an evals array; each eval has
#     non-empty assertions; every assertion.name used must be registered in
#     grade_research_init.py ASSERTION_CHECKS (catches unregistered checkers).
#     ASSERTION_CHECKS values are function refs, so we extract only the keys
#     from the ast Dict node (no literal_eval).
"$py" - "$repo/evals/evals.json" "$repo/scripts/grade_research_init.py" <<'PY'
import ast
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
evals = data.get("evals")
if not isinstance(evals, list) or not evals:
    raise SystemExit("evals/evals.json: 缺非空 evals 数组")

names_used = set()
for i, ev in enumerate(evals):
    assertions = ev.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        raise SystemExit(f"evals/evals.json: eval[{i}] 缺非空 assertions")
    for a in assertions:
        n = a.get("name")
        if not n:
            raise SystemExit(f"evals/evals.json: eval[{i}] 有断言缺 name")
        names_used.add(n)

# Extract ASSERTION_CHECKS keys from the grader (values are function refs,
# unreachable by literal_eval; walk the Dict node for Constant keys only).
grader = Path(sys.argv[2]).read_text(encoding="utf-8")
tree = ast.parse(grader)
checker_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "ASSERTION_CHECKS":
                checker_node = node.value
                break
if checker_node is None or not isinstance(checker_node, ast.Dict):
    raise SystemExit("grade_research_init.py: 找不到 ASSERTION_CHECKS 字典")
registered = set()
for k in checker_node.keys:
    if isinstance(k, ast.Constant):
        registered.add(k.value)
    elif hasattr(ast, "Str") and isinstance(k, ast.Str):  # <3.8 compat
        registered.add(k.s)
if not registered:
    raise SystemExit("grade_research_init.py: ASSERTION_CHECKS 无任何键")

unregistered = names_used - registered
if unregistered:
    raise SystemExit(
        f"evals/evals.json 用了未在 ASSERTION_CHECKS 登记的断言: {sorted(unregistered)}"
        "（在 grade_research_init.py 的 ASSERTION_CHECKS 补登记）"
    )
PY
echo "  evals.json valid + assertion names registered OK"

echo "== python scripts =="

# 15. Python scripts compile; skeleton + grader self-tests pass.
for s in scripts/create_research_skeleton.py scripts/grade_research_init.py scripts/aggregate_benchmark.py; do
  PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/rw-skill-pycache" \
    "$py" -m py_compile "$repo/$s" || fail "$s: py_compile 失败"
done
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/rw-skill-pycache" \
  "$py" "$repo/scripts/create_research_skeleton.py" --self-test >/dev/null
echo "  create_research_skeleton.py py_compile + self-test OK"
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/rw-skill-pycache" \
  "$py" "$repo/scripts/grade_research_init.py" --self-test >/dev/null
echo "  grade_research_init.py py_compile + self-test OK"
echo "  aggregate_benchmark.py py_compile OK"

echo "== shell scripts =="

# 16. Shell scripts pass syntax check.
for s in scripts/validate.sh scripts/install.sh scripts/release.sh scripts/doc-impact-check.sh; do
  bash -n "$repo/$s" || fail "$s: 语法错误"
done
test -f "$repo/scripts/githooks/pre-push" && bash -n "$repo/scripts/githooks/pre-push" \
  || fail "scripts/githooks/pre-push missing or syntax error"
echo "  shell scripts syntax OK"

echo
echo "PASS: validation complete"
