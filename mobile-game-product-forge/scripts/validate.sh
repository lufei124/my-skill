#!/usr/bin/env bash
#
# Unified validator for mobile-game-product-forge.
# Runs the P0 architecture checks, then P1 structure / link / version /
# metadata / invocation-config checks. Exits non-zero on any failure.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo"

fail() { echo "FAIL: $1" >&2; exit 1; }
py="$(command -v python3 || command -v python || true)"
[ -n "$py" ] || fail "python3/python is required for validation"

echo "== P0 architecture =="
bash "$repo/scripts/validate-p0-architecture.sh"

echo "== P1 structure =="

# 1. Every published skill has SKILL.md + agents/openai.yaml
check_skill_files() {
  local skill_dir="$1" label="$2"
  test -f "$skill_dir/SKILL.md" || fail "$label: SKILL.md missing"
  test -f "$skill_dir/agents/openai.yaml" || fail "$label: agents/openai.yaml missing"
}
check_skill_files "$repo" "mobile-game-product-forge (root)"
for d in "$repo"/skills/*/; do
  name="$(basename "$d")"
  check_skill_files "$d" "$name"
done

# 2. Invocation config: setup is user-invoked; formal PRD writing/publish
#    must be explicitly routed by the root orchestrator.
grep -Eq '^disable-model-invocation: true$' "$repo/skills/setup-mobile-game-product-forge/SKILL.md" \
  || fail "setup skill is not user-invoked (missing disable-model-invocation)"
grep -Eq 'allow_implicit_invocation: false' "$repo/skills/setup-mobile-game-product-forge/agents/openai.yaml" \
  || fail "setup skill agents/openai.yaml is not user-invoked"
if grep -Eq '^disable-model-invocation: true$' "$repo/SKILL.md"; then
  fail "main skill must be model-invoked, not user-invoked"
fi

echo "== P1 version consistency =="

# 3. Single version source: package.json drives plugin.json and SKILL.md.
pkg_ver="$(grep -m1 '"version"' "$repo/package.json" | sed -E 's/.*"version": *"([^"]+)".*/\1/')"
[ -n "$pkg_ver" ] || fail "package.json has no version"

plugin_ver="$(grep -m1 '"version"' "$repo/.claude-plugin/plugin.json" | sed -E 's/.*"version": *"([^"]+)".*/\1/')"
[ "$plugin_ver" = "$pkg_ver" ] \
  || fail "plugin.json version '$plugin_ver' != package.json '$pkg_ver'"

skill_ver="$(grep -oE '当前 Skill 版本：.{0,1}([0-9]+\.[0-9]+\.[0-9]+)' "$repo/SKILL.md" | sed -E 's/.*当前 Skill 版本：.{0,1}([0-9]+\.[0-9]+\.[0-9]+).*/\1/' | head -1)"
[ "$skill_ver" = "$pkg_ver" ] \
  || fail "SKILL.md 当前 Skill 版本 '$skill_ver' != package.json '$pkg_ver'"

echo "  version: $pkg_ver (package.json = plugin.json = SKILL.md) OK"

echo "== P1 relative links =="

# 4. Sub-skill relative references (../../references/...) must resolve.
for d in "$repo"/skills/*/; do
  name="$(basename "$d")"
  f="$d/SKILL.md"
  [ -f "$f" ] || continue
  refs="$(grep -oE '\]\((\.\./\.\./[^)]+)\)' "$f" | sed -E 's/.*\]\(([^)]+)\).*/\1/' || true)"
  while IFS= read -r p; do
    [ -n "$p" ] || continue
    if ! (cd "$d" && test -e "$p"); then
      fail "$name: broken relative reference '$p' in SKILL.md"
    fi
  done <<< "$refs"
done
echo "  sub-skill relative references OK"

echo "== P1 plugin manifest =="

# 5. plugin.json must explicitly register the root SKILL.md with "./".
#    Claude Code adds custom skill paths to the default skills/ scan, so the
#    manifest must not duplicate every default sub-skill directory.
"$py" - "$repo/.claude-plugin/plugin.json" "$repo" <<'PY'
import json
import sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
repo = Path(sys.argv[2])
data = json.loads(manifest_path.read_text(encoding="utf-8"))
skills = data.get("skills")
if isinstance(skills, str):
    skills = [skills]
if skills != ["./"]:
    raise SystemExit('plugin.json skills must be exactly ["./"]: explicit root registration; default skills/ is scanned automatically')
if not (repo / "SKILL.md").is_file():
    raise SystemExit("root SKILL.md missing")
for child in sorted((repo / "skills").iterdir()):
    if child.is_dir() and not (child / "SKILL.md").is_file():
        raise SystemExit(f"default skills/ child has no SKILL.md: {child.name}")
PY
echo "  plugin.json root registration and default skills/ layout OK"

# 5b. marketplace.json（同仓自托）：必须存在、可解析，且唯一插件条目
#     指向仓库自身（source "./"）、不写 version（版本解析统一落到 plugin.json）。
"$py" - "$repo/.claude-plugin/marketplace.json" <<'PY'
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
if entry.get("name") != "mobile-game-product-forge":
    raise SystemExit("marketplace plugin entry name must be mobile-game-product-forge")
if entry.get("source") != "./":
    raise SystemExit('marketplace plugin entry source must be "./" (same-repo self-hosting)')
if "version" in entry:
    raise SystemExit("marketplace plugin entry must not pin version: resolution falls back to plugin.json so releases only bump one place")
PY
echo "  marketplace.json self-hosted entry OK"

echo "== P1 install profiles =="

# 6. install profiles must reference each sub-skill directory.
for sub in "$repo"/skills/*/; do
  name="$(basename "$sub")"
  for prof in core core-life-reboots; do
    grep -q "skills/$name" "$repo/install-profiles/$prof.yaml" \
      || fail "install-profiles/$prof.yaml does not reference skills/$name"
  done
done
echo "  install profiles reference all sub-skills OK"

echo "== P1 reverse coverage =="

# 2b. Invocation policy must be explicit in every agents/openai.yaml.
#     setup, game-prd-writing and game-prd-publish are explicit-only;
#     root and the remaining narrow-task-capable sub-skills stay implicit.
check_invocation_policy() {
  f="$1"; expected="$2"; label="$3"
  grep -Eq "allow_implicit_invocation: $expected"'$' "$f" \
    || fail "$label: agents/openai.yaml must declare allow_implicit_invocation: $expected (intent must be explicit, not by omission)"
}
check_invocation_policy "$repo/agents/openai.yaml" true "root"
for d in "$repo"/skills/*/; do
  name="$(basename "$d")"
  if [ "$name" = "setup-mobile-game-product-forge" ]; then
    grep -Eq '^disable-model-invocation: true$' "$d/SKILL.md" \
      || fail "$name: setup SKILL.md must have disable-model-invocation: true"
    check_invocation_policy "$d/agents/openai.yaml" false "$name"
  elif [ "$name" = "game-prd-writing" ] || [ "$name" = "game-prd-publish" ]; then
    grep -Eq '^disable-model-invocation: true$' "$d/SKILL.md" \
      && fail "$name: explicit-only routing is controlled by openai.yaml, not disable-model-invocation"
    check_invocation_policy "$d/agents/openai.yaml" false "$name"
  else
    grep -Eq '^disable-model-invocation: true$' "$d/SKILL.md" \
      && fail "$name: sub-skill must be model-invoked, but SKILL.md has disable-model-invocation: true"
    check_invocation_policy "$d/agents/openai.yaml" true "$name"
  fi
done
echo "  invocation policy explicit on all skills OK"

# 3b. Sub-skills must not hardcode the Skill version (single source = package.json).
for d in "$repo"/skills/*/; do
  name="$(basename "$d")"
  f="$d/SKILL.md"
  [ -f "$f" ] || continue
  if grep -Eq 'Skill 版本：[0-9]' "$f"; then
    fail "$name: SKILL.md hardcodes 'Skill 版本：<number>'; use the placeholder '(随包发布，见 package.json)' and let package.json be the single source"
  fi
done
echo "  sub-skills do not hardcode Skill version OK"

# 4b. Root SKILL.md references/*.md links must resolve to real files.
root_refs="$(grep -oE '\]\((references/[^)]+)\)' "$repo/SKILL.md" | sed -E 's/.*\]\(([^)]+)\).*/\1/' | sort -u || true)"
while IFS= read -r p; do
  [ -n "$p" ] || continue
  [ -e "$repo/$p" ] || fail "SKILL.md: broken reference '$p'"
done <<< "$root_refs"
echo "  root SKILL.md references resolve OK"

# 4c. Evidence-driven context loading has one shared contract, and every
#     stage that prepares or consumes it must link to that contract.
for f in \
  "$repo/SKILL.md" \
  "$repo/skills/game-requirement-discovery/SKILL.md" \
  "$repo/skills/game-prototype/SKILL.md" \
  "$repo/skills/game-prd-writing/SKILL.md" \
  "$repo/skills/game-prd-review/SKILL.md"; do
  grep -qF 'context-loading.md' "$f" \
    || fail "${f#$repo/}: missing shared context-loading.md contract reference"
  grep -Eq 'context-loading\.md.*「' "$f" \
    || fail "${f#$repo/}: context-loading reference must name stable section headings"
done
echo "  evidence-driven context contract linked from orchestrator and stages OK"

# 4d. Capability-fidelity contract: research and snapshots stay separate,
#     metadata is classified, and role reports expose their reviewed versions.
for heading in \
  '## 快速执行索引' \
  '## 2. 三类权威来源模型' \
  '## 3. 冲突处理：当前状态、目标状态与改动' \
  '## 4. 需求调研来源与现状核验' \
  '## 11. prototype-meta 完整性与 HTML 降级' \
  '## 14. 角色切片、版本一致性与冲突汇总'; do
  # -x：整行匹配。用 -F 子串匹配时「### 快速执行索引」也会满足「## 快速执行索引」，
  # 断言会在标题被降级/改写后依然变绿（同类 bug 见 #18 / #20）。
  grep -qxF -e "$heading" "$repo/references/context-loading.md" \
    || fail "references/context-loading.md: missing heading line '$heading'"
done
for term in '用户访谈' '项目知识' '当前实现' '历史证据' '数据和反馈' '外部调研'; do
  grep -qF -e "$term" "$repo/skills/game-requirement-discovery/SKILL.md" \
    || fail "game-requirement-discovery: missing research source '$term'"
done
grep -qF '00-research-findings.md' "$repo/references/templates.md" \
  || fail "templates.md: missing new research artifact"
grep -qF '00-project-context.md' "$repo/references/templates.md" \
  || fail "templates.md: missing legacy research compatibility"
for term in \
  'validate_research_context' \
  'RESEARCH_FILENAMES' \
  'RESEARCH_REQUIRED_HEADINGS' \
  'SUPPORTED_PROTOTYPE_META_SCHEMA_VERSIONS' \
  'PROTOTYPE_META_PLACEHOLDERS' \
  'classify_prototype_meta' \
  'duplicateIds' \
  '"COMPLETE"' \
  '"INCOMPLETE"' \
  '"INVALID"'; do
  grep -qF -e "$term" \
    "$repo/scripts/stage_gate_core.py" \
    "$repo/scripts/prototype_meta.py" \
    "$repo/scripts/check-stage-gate.py" >/dev/null \
    || fail "stage-gate runtime: missing research/metadata gate contract '$term'"
done
for field in reviewRole snapshotVersion prdVersion prototypeVersion reviewedAt; do
  grep -qF -e "$field" "$repo/references/templates.md" \
    || fail "templates.md: missing review version field '$field'"
  grep -qF -e "$field" "$repo/skills/game-prd-review/SKILL.md" \
    || fail "game-prd-review: missing review version field '$field'"
done
grep -qF 'projectContext.status=completed' "$repo/skills/game-requirement-discovery/SKILL.md" \
  || fail "game-requirement-discovery: missing coordinator research-state handoff"
grep -qF '补齐 metadata' "$repo/skills/game-prd-writing/SKILL.md" \
  || fail "game-prd-writing: INCOMPLETE/INVALID metadata must trigger actual compatibility completion"
grep -qF 'not_applicable 路径不得触发该兼容流程' "$repo/skills/game-prd-writing/SKILL.md" \
  || fail "game-prd-writing: waived path must skip historical HTML/metadata compatibility"
echo "  research, metadata completeness, and review version contracts OK"

# 5b. Every default skills/* directory must be covered by install profiles and
#     root routing. plugin.json intentionally relies on Claude Code's default
#     skills/ scan instead of duplicating those paths.
for d in "$repo"/skills/*/; do
  name="$(basename "$d")"
  test -f "$d/SKILL.md" || fail "default skill missing SKILL.md: $name"
  for prof in core core-life-reboots; do
    grep -qF "skills/$name/" "$repo/install-profiles/$prof.yaml" \
      || fail "$prof.yaml does not include default skill: $name"
  done
done
echo "  default skills/ scan has no orphan sub-skills OK"

# 6b. install-profiles source_files paths must exist (catch phantom/typo'd skills).
for prof in core core-life-reboots; do
  f="$repo/install-profiles/$prof.yaml"
  srcs="$(grep -oE '^[[:space:]]*-[[:space:]]*"([^"]+)"' "$f" | sed -E 's/^[[:space:]]*-[[:space:]]*"([^"]+)".*/\1/' || true)"
  while IFS= read -r p; do
    [ -n "$p" ] || continue
    [ -e "$repo/$p" ] || fail "install-profiles/$prof.yaml: source_files path does not exist: $p"
  done <<< "$srcs"
done
echo "  install-profiles source_files paths exist OK"

# 7. README.md and AGENTS.md must mention each sub-skill (prevent doc drift).
for d in "$repo"/skills/*/; do
  name="$(basename "$d")"
  grep -qF -e "$name" "$repo/README.md" || fail "README.md does not mention sub-skill: $name"
  grep -qF -e "$name" "$repo/AGENTS.md" || fail "AGENTS.md does not mention sub-skill: $name"
done
echo "  README.md and AGENTS.md mention all sub-skills OK"

# 7b. Root orchestrator SKILL.md must route to each non-setup sub-skill
#     (router-can-lie guard: a sub-skill registered in plugin.json but not
#     routed in the orchestrator is unreachable).
for d in "$repo"/skills/*/; do
  name="$(basename "$d")"
  [ "$name" = "setup-mobile-game-product-forge" ] && continue
  grep -qF -e "$name" "$repo/SKILL.md" \
    || fail "orchestrator SKILL.md does not route to sub-skill: $name"
done
echo "  orchestrator SKILL.md routes to all non-setup sub-skills OK"

# 7c. README.md and AGENTS.md must mention each references/*.md (prevent drift
#     between the shared domain specs and the docs that index them).
for f in "$repo"/references/*.md; do
  b="$(basename "$f")"
  grep -qF -e "$b" "$repo/README.md" || fail "README.md does not mention reference: $b"
  grep -qF -e "$b" "$repo/AGENTS.md" || fail "AGENTS.md does not mention reference: $b"
done
echo "  README.md and AGENTS.md mention all references OK"

# 8. SKILL 引用的 scripts/* 必须存在（校验门/发布门依赖的脚本不得被误删）。
for f in "$repo/SKILL.md" "$repo"/skills/*/SKILL.md; do
  [ -f "$f" ] || continue
  while IFS= read -r scr; do
    [ -n "$scr" ] || continue
    [ -e "$repo/$scr" ] || fail "$(basename "$f"): 引用的脚本不存在: $scr"
  done <<< "$(grep -oE 'scripts/[A-Za-z0-9_]+\.(py|sh)' "$f" | sort -u || true)"
done
echo "  SKILL-referenced scripts exist OK"

# 8b. Formal workflow JSON stage-gate contract and runtime script must stay executable.
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/mobile-game-product-forge-pycache" \
  "$py" -m py_compile \
    "$repo/scripts/check-stage-gate.py" \
    "$repo/scripts/stage_gate_core.py" \
    "$repo/scripts/prototype_meta.py" \
    "$repo/scripts/stage_gate_selftest.py"
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/mobile-game-product-forge-pycache" \
  "$py" "$repo/scripts/check-stage-gate.py" --self-test >/dev/null
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/mobile-game-product-forge-pycache" \
  "$py" -m py_compile "$repo/scripts/lint-review-report.py"
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/mobile-game-product-forge-pycache" \
  "$py" "$repo/scripts/lint-review-report.py" --self-test >/dev/null \
  || fail "lint-review-report.py self-test failed"
grep -qF '00-stage-state.json' "$repo/SKILL.md" \
  || fail "root SKILL.md does not declare 00-stage-state.json"
test -f "$repo/references/stage-state.schema.json" \
  || fail "references/stage-state.schema.json missing"
"$py" -c 'import json,sys; json.load(open(sys.argv[1], encoding="utf-8"))' \
  "$repo/references/stage-state.schema.json"
grep -qF 'docs/mobile-game-product-forge/operation-guide.md' "$repo/skills/setup-mobile-game-product-forge/SKILL.md" \
  || fail "setup skill does not write/report the project operation guide"
grep -qF 'docs/mobile-game-product-forge/operation-guide.md' "$repo/operation-guide.md" \
  || fail "operation guide does not declare its project-local path"
echo "  stage-gate runtime and project operation-guide contract OK"

# 9. install.sh 回执不得硬编码 pack 版本（须从 PACK.md 读取为 $pack_ver）。
grep -qF 'version: $pack_ver' "$repo/scripts/install.sh" \
  || fail "install.sh receipt does not use \$pack_ver (read pack version from PACK.md)"

# 10. 紧凑生成记录唯一权威源在主 SKILL.md；子 Skill 不得复制旧式来源信息块。
for f in skills/game-prd-writing/SKILL.md skills/game-prd-publish/SKILL.md; do
  if grep -qF '创建人：' "$repo/$f" && grep -qF '使用的知识模块：' "$repo/$f"; then
    fail "$f: 复制了「文档来源信息」块；改为指向主 SKILL.md「文档来源信息」节的指针"
  fi
done
echo "  sub-skills do not duplicate legacy provenance block OK"

# 11. 知识维护提案格式须对齐 references/project-knowledge.md 第 5 节（防字段漂移）。
proposal="skills/game-knowledge-maintenance-proposal/SKILL.md"
grep -qF '提案编号' "$repo/$proposal" \
  || fail "$proposal: 提案格式缺「提案编号」字段（须对齐 project-knowledge.md 第 5 节）"
grep -qF '证据' "$repo/$proposal" \
  || fail "$proposal: 提案格式缺「证据」字段（须对齐 project-knowledge.md 第 5 节）"
echo "  knowledge proposal format aligned to reference OK"

# 12. 两份 install-profiles 的 skills 清单须一致（仅 project_knowledge 不同）。
core_block="$(awk '/^skills:/{p=1} /^project_knowledge:/{p=0} p' "$repo/install-profiles/core.yaml")"
reboots_block="$(awk '/^skills:/{p=1} /^project_knowledge:/{p=0} p' "$repo/install-profiles/core-life-reboots.yaml")"
[ "$core_block" = "$reboots_block" ] \
  || fail "install-profiles core.yaml and core-life-reboots.yaml skills blocks differ (must be identical; only project_knowledge may differ)"
echo "  install-profiles skills lists identical OK"

# 13. 根编排器注册策略：plugin.json 用 "./" 显式注册根 SKILL.md；
#     默认 skills/ 自动发现子 Skill；两份 install-profiles 继续登记根入口。
root_name="mobile-game-product-forge"
plugin_name="$(grep -E '^  "name":' "$repo/.claude-plugin/plugin.json" | head -1 | sed -E 's/.*"name":[[:space:]]*"([^"]+)".*/\1/')"
skill_name="$(grep -E '^name:' "$repo/SKILL.md" | head -1 | sed -E 's/^name:[[:space:]]*//')"
[ "$plugin_name" = "$root_name" ] || fail "plugin.json name '$plugin_name' != root name '$root_name'"
[ "$skill_name" = "$root_name" ] || fail "root SKILL.md name '$skill_name' != expected '$root_name'"
grep -qF '"./"' "$repo/.claude-plugin/plugin.json" \
  || fail "plugin.json must explicitly register root skill path './' (see ADR-0006)"
if grep -qF '"./skills/' "$repo/.claude-plugin/plugin.json"; then
  fail "plugin.json must not duplicate default skills/ sub-skill paths; Claude Code scans skills/ automatically"
fi
for prof in core core-life-reboots; do
  grep -qF 'name: "mobile-game-product-forge"' "$repo/install-profiles/$prof.yaml" \
    || fail "$prof.yaml: missing root skill entry 'name: \"mobile-game-product-forge\"'"
done
echo "  root orchestrator explicit plugin registration policy OK"

# 13b. 路由描述必须把宽泛正式需求留给根编排器；子 Skill 只匹配
#      编排器委派或用户明确的窄任务。
grep -qF 'Default entry for any new, broad' "$repo/SKILL.md" \
  || fail "root SKILL.md description does not declare broad/formal default entry"
for f in \
  skills/game-requirement-discovery/SKILL.md \
  skills/game-prototype/SKILL.md \
  skills/game-prd-review/SKILL.md \
  skills/game-analytics-design/SKILL.md \
  skills/game-knowledge-maintenance-proposal/SKILL.md; do
  grep -qF 'description: Use only' "$repo/$f" \
    || fail "$f: description must start with a narrow routing guard"
done
for f in \
  skills/game-requirement-discovery/SKILL.md \
  skills/game-prototype/SKILL.md \
  skills/game-prd-review/SKILL.md \
  skills/game-analytics-design/SKILL.md; do
  grep -qF 'root orchestrator' "$repo/$f" \
    || fail "$f: description must route broad requests back to root orchestrator"
done
echo "  root/sub-skill routing descriptions guarded OK"

# 13c. External evidence must be official and applicable by region/date/version.
for term in '目标地区' '目标发布日期' '当前接入版本' '目标版本' '官方迁移指南'; do
  grep -qF -e "$term" "$repo/references/context-loading.md" \
    || fail "context-loading.md: missing applicable external-evidence term '$term'"
  grep -qF -e "$term" "$repo/references/prd-spec.md" \
    || fail "prd-spec.md: missing applicable third-party-evidence term '$term'"
done
if grep -R -nF '优先最新官方资料' \
  "$repo/SKILL.md" \
  "$repo/references/context-loading.md" \
  "$repo/skills/game-requirement-discovery/SKILL.md" \
  "$repo/skills/game-prd-writing/SKILL.md" >/dev/null; then
  fail "external evidence still uses unqualified '优先最新官方资料' wording"
fi
echo "  region/date/version-matched official evidence contract OK"

# 13d. Static routing and real-scenario regression fixtures must stay valid.
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/mobile-game-product-forge-pycache" \
  "$py" -m py_compile "$repo/scripts/validate-regression-fixtures.py"
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/mobile-game-product-forge-pycache" \
  "$py" "$repo/scripts/validate-regression-fixtures.py" >/dev/null
test -f "$repo/docs/capability-regression.md" \
  || fail "docs/capability-regression.md missing"
# 输入风格约定必须成文：只补规范书面句不算扩充覆盖（口语边界才是判错代价所在）。
grep -qxF -e '### 路由夹具的输入风格约定' "$repo/docs/capability-regression.md" \
  || fail "docs/capability-regression.md: 缺少「路由夹具的输入风格约定」小节"
for term in 'colloquial' 'mixed_language' 'explicit_invocation' 'ambiguous_reference' '不少于三分之一'; do
  grep -qF -e "$term" "$repo/docs/capability-regression.md" \
    || fail "docs/capability-regression.md 风格约定缺少：$term"
done
echo "  routing and capability regression fixtures OK"

# 13e. PRD execution structure and legacy compatibility.
for term in '统一使用以下结构' '多模块控制' '页面流转图' '时序图' '状态机图' '数据流图' '项目不使用运营后台'; do
  grep -qF -e "$term" "$repo/references/prd-spec.md" \
    || fail "prd-spec.md: missing execution-structure contract '$term'"
done
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/mobile-game-product-forge-pycache" \
  "$py" -m py_compile "$repo/scripts/lint-prd.py"
"$py" "$repo/scripts/lint-prd.py" "$repo/fixtures/valid-prd.md" >/dev/null \
  || fail "new-structure valid PRD fixture failed"
"$py" "$repo/scripts/lint-prd.py" "$repo/fixtures/legacy-valid-prd.md" >/dev/null \
  || fail "legacy PRD compatibility fixture failed"
invalid_code=0
"$py" "$repo/scripts/lint-prd.py" "$repo/fixtures/invalid-prd.md" >/dev/null || invalid_code=$?
[ "$invalid_code" -eq 1 ] || fail "invalid PRD fixture expected exit 1, got $invalid_code"
echo "  unified PRD structure, table numbering, and legacy compatibility OK"

# 14. agents/openai.yaml 结构校验（零依赖，BSD 兼容；容忍前导空白，靠内容锚定不靠列对齐）。
#     每份须恰好含顶级父键 interface: 与 policy:，无其他顶级键；interface 段下含
#     display_name / short_description / default_prompt 三非空 leaf；policy 段下含
#     allow_implicit_invocation 为 true|false。game-prd-publish 的 1 空格缩进瑕疵以内
#     容锚定兼容（最小缩进上的父键即顶层）。
for f in "$repo/agents/openai.yaml" "$repo"/skills/*/agents/openai.yaml; do
  [ -f "$f" ] || continue
  rel="${f#$repo/}"
  # 最小父键缩进 + 父键集合（父键 = 行匹配 ^<indent>name:$，值空）
  minInd=$(awk '{
    if (match($0, /^[[:space:]]*[a-z_]+:[[:space:]]*$/)) {
      pre=$0; sub(/[a-z_]+:[[:space:]]*$/, "", pre); ind=length(pre)
      if (m=="" || ind<m) m=ind
    }
  } END{ print (m=="" ? -1 : m) }' "$f")
  [ "$minInd" -ge 0 ] 2>/dev/null || fail "$rel: 无顶级父键（缺 interface: / policy:）"
  # 在最小缩进上的父键名
  topkeys=$(awk -v ind="$minInd" '{
    if (match($0, /^[[:space:]]*[a-z_]+:[[:space:]]*$/)) {
      pre=$0; sub(/[a-z_]+:[[:space:]]*$/, "", pre)
      if (length(pre)==ind) { s=$0; sub(/^[[:space:]]*/,"",s); sub(/:.*/,"",s); print s }
    }
  }' "$f" | sort | paste -sd, -)
  [ "$topkeys" = "interface,policy" ] || [ "$topkeys" = "policy,interface" ] \
    || fail "$rel: 顶级父键须恰好为 {interface, policy}，实际: {$topkeys}"
  # leaf 存在性 + 非空（接口三 leaf 必有，策略一 leaf 为布尔字面量）
  grep -Eq '^[[:space:]]*display_name:[[:space:]]*[^[:space:]]' "$f" \
    || fail "$rel: interface 段缺非空 display_name"
  grep -Eq '^[[:space:]]*short_description:[[:space:]]*[^[:space:]]' "$f" \
    || fail "$rel: interface 段缺非空 short_description"
  grep -Eq '^[[:space:]]*default_prompt:[[:space:]]*[^[:space:]]' "$f" \
    || fail "$rel: interface 段缺非空 default_prompt"
  grep -Eq '^[[:space:]]*allow_implicit_invocation:[[:space:]]*(true|false)[[:space:]]*$' "$f" \
    || fail "$rel: policy 段 allow_implicit_invocation 须为 true 或 false"
done
echo "  agents/openai.yaml structure OK"

# 15. 生成记录位置唯一：正式文档一律「文档末尾一行紧凑生成记录」，
#     不得回到「文档信息区/文档信息块」承载来源信息（防 M-01 类漂移复发）。
for f in "$repo/SKILL.md" "$repo"/skills/*/SKILL.md "$repo"/references/*.md; do
  [ -f "$f" ] || continue
  if grep -nE '文档信息(区|块)[^。]*(来源|生成记录)|(来源信息|生成记录)[^。]*文档信息(区|块)' "$f" >/dev/null; then
    fail "${f#$repo/}: 生成记录位置与主 SKILL.md 冲突（唯一位置是文档末尾一行紧凑生成记录，不写入文档信息区）"
  fi
done
grep -qF '文档末尾' "$repo/skills/game-prd-writing/SKILL.md" \
  || fail "game-prd-writing: 必须声明生成记录写在文档末尾（评审前预检按文末位置解析）"
echo "  compact provenance record has one location OK"

# 16. 跨文件「第 N 节」引用必须命中目标文件真实存在的 ## N. 标题
#     （链接能解析不代表章节存在；防 M-03 类死引用）。
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/mobile-game-product-forge-pycache" \
  "$py" - "$repo" <<'PY'
import re
import sys
from pathlib import Path

repo = Path(sys.argv[1])
ref = re.compile(r'\]\(([^)\s]+\.md)\)[^。\n]{0,12}?第\s*(\d+)\s*节')
skip = {".git", "node_modules", "history"}
bad = []
for md in sorted(repo.rglob("*.md")):
    if any(part in skip for part in md.relative_to(repo).parts):
        continue
    for m in ref.finditer(md.read_text(encoding="utf-8")):
        target = (md.parent / m.group(1)).resolve()
        n = m.group(2)
        if not target.is_file():
            bad.append(f"{md.relative_to(repo)} -> 目标文件不存在 {m.group(1)}")
            continue
        heading = re.compile(rf"^##\s+{n}\.", re.MULTILINE)
        if not heading.search(target.read_text(encoding="utf-8")):
            bad.append(f"{md.relative_to(repo)} -> {m.group(1)} 无「## {n}.」章节")
if bad:
    raise SystemExit("cross-file section references are broken:\n  " + "\n  ".join(bad))
PY
echo "  cross-file 「第 N 节」 references resolve to real headings OK"

# 17. 上下文加载清单唯一权威：context-loading.md「快速执行索引」是各阶段清单来源，
#     编排器与阶段子 Skill 只指向该表，不在一行里复制多个章节清单（防 M-04 类漂移）。
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/mobile-game-product-forge-pycache" \
  "$py" - "$repo" <<'PY'
import re
import sys
from pathlib import Path

repo = Path(sys.argv[1])
contract = repo / "references" / "context-loading.md"
headings = {
    m.group(1).strip()
    for m in re.finditer(r"^##\s+(?:\d+\.\s*)?(.+)$", contract.read_text(encoding="utf-8"), re.MULTILINE)
}
INDEX = "快速执行索引"
stages = ["SKILL.md"] + [
    f"skills/{s}/SKILL.md"
    for s in (
        "game-requirement-discovery",
        "game-prototype",
        "game-prd-writing",
        "game-prd-review",
    )
]
problems = []
for rel in stages:
    text = (repo / rel).read_text(encoding="utf-8")
    if f"context-loading.md" not in text:
        problems.append(f"{rel}: 未引用 context-loading.md")
        continue
    if INDEX not in text:
        problems.append(f"{rel}: 必须指向「{INDEX}」（各阶段加载清单的唯一权威源）")
    for i, line in enumerate(text.splitlines(), 1):
        if "context-loading.md" not in line:
            continue
        named = [t for t in re.findall(r"「([^」]+)」", line) if t in headings and t != INDEX]
        if len(named) > 1:
            problems.append(f"{rel}:{i}: 复制了加载清单 {named}；改为指向「{INDEX}」对应行")
if problems:
    raise SystemExit("context-loading list is duplicated instead of referenced:\n  " + "\n  ".join(problems))
PY
echo "  context-loading quick index is the single loading-list authority OK"

# 18. 正式启动前置三条规则（落点确认 / 恢复消歧 / 窄任务接入）必须在
#     workflow.md 第 0 节成文，且窄任务接入不得发状态源。
for anchor in \
  '### 0.1 创建工作目录前先确认落点' \
  '### 0.2 恢复类请求必须消歧到唯一需求目录' \
  '### 0.3 存量或外部 PRD 走窄任务接入，不发状态源'; do
  grep -qxF -e "$anchor" "$repo/references/workflow.md" \
    || fail "references/workflow.md: 第 0 节缺少标题行 '${anchor}'"
done
grep -qF 'history/*/00-stage-state.json' "$repo/references/workflow.md" \
  || fail "workflow.md 0.2: 恢复类请求必须先扫 history/*/00-stage-state.json 形成候选集"
grep -qF '禁止按目录最近修改时间' "$repo/references/workflow.md" \
  || fail "workflow.md 0.2: 必须禁止按最近修改时间猜选需求目录"
grep -qF 'knowledge/INDEX.md' "$repo/references/workflow.md" \
  || fail "workflow.md 0.1: 落点确认必须给出已初始化的检测依据"
echo "  formal-start guards (landing spot / disambiguation / narrow-task intake) OK"

# 19. 截图占位符：lint 逐条列出并降为有条件通过（不阻塞研发），发布门硬拦交付。
test -f "$repo/fixtures/placeholder-prd.md" \
  || fail "fixtures/placeholder-prd.md missing (占位符终稿回归夹具)"
ph_code=0
ph_report="$("$py" "$repo/scripts/lint-prd.py" "$repo/fixtures/placeholder-prd.md")" || ph_code=$?
[ "$ph_code" -eq 0 ] \
  || fail "placeholder fixture must be 有条件通过 (exit 0), got $ph_code"
printf '%s' "$ph_report" | grep -qF '待补充截图' \
  || fail "lint-prd.py 未逐条列出「待补充截图」占位符"
printf '%s' "$ph_report" | grep -qF '有条件通过（存在' \
  || fail "lint-prd.py 占位符结论必须是「有条件通过（存在 N 处待补充截图…）」"
"$py" "$repo/scripts/lint-prd.py" "$repo/fixtures/valid-prd.md" | grep -qF '待补充截图' \
  && fail "无占位符的 valid PRD 夹具不应触发占位符提示"
grep -qF '待补充截图' "$repo/skills/game-prd-publish/SKILL.md" \
  || fail "game-prd-publish: 前置条件缺少占位符硬拦（交付前须补图或显式确认）"
grep -qF '停止发布' "$repo/skills/game-prd-publish/SKILL.md" \
  || fail "game-prd-publish: 占位符命中时必须停止发布，等待产品负责人确认"
echo "  screenshot placeholders: lint conditional-pass + publish-gate hard stop OK"

# 20. 升级 SOP 必须成文（ZIP 覆盖解压是版本碎片化主因），且 install-profiles
#     的「校验清单，不驱动安装」声明必须与 install 脚本的实际行为一致。
grep -qxF -e '## 升级' "$repo/README.md" \
  || fail "README.md: 缺少「## 升级」小节（无升级 SOP 会导致版本碎片化）"
for sub in '^### 插件安装' '^### 脚本安装' '^### ZIP 分发' '^### 用户数据边界' '^### 升级后自检'; do
  grep -qE -e "$sub" "$repo/README.md" \
    || fail "README.md 升级小节缺少子节：${sub#^### }"
done
for term in 'git pull' '--agent all --force' '.installed-packs' 'conflicts'; do
  grep -qF -e "$term" "$repo/README.md" \
    || fail "README.md 升级小节缺少关键步骤/口径：$term"
done
grep -qF 'scripts/validate.sh` 全绿' "$repo/README.md" \
  || fail "README.md: 升级后自检必须要求 validate.sh 全绿"
for prof in core core-life-reboots; do
  grep -qF '校验清单，不驱动安装' "$repo/install-profiles/$prof.yaml" \
    || fail "install-profiles/$prof.yaml: 缺少「校验清单，不驱动安装」声明（防止被当成安装配置）"
done
grep -qF '校验清单，不是安装配置' "$repo/README.md" \
  || fail "README.md: 安装小节必须说明 install-profiles 是校验清单而非安装配置"
for f in scripts/install.sh scripts/install.ps1; do
  if grep -qF 'install-profiles' "$repo/$f"; then
    fail "$f 开始读取 install-profiles/：请同步改掉 YAML 与 README 里「不驱动安装」的声明"
  fi
done
echo "  upgrade SOP documented and install-profiles role matches installer behavior OK"

echo
echo "PASS: P0 + P1 validation complete"
