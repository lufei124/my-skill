#!/usr/bin/env bash
#
# Maintenance pre-check for research-workflow.
#
# Maps changed paths (working-tree diff + untracked, or an explicit --base ref)
# to AGENTS.md §8 document-sync suggestions, and auto-annotates the §9 doc-impact
# checklist. Output is advisory only: non-blocking, exit code always 0, not in CI.
#
# Usage:
#   bash scripts/doc-impact-check.sh              # diff working tree + untracked
#   bash scripts/doc-impact-check.sh --base HEAD  # diff against a ref
#
# Portable: bash 3.2 (macOS) compatible - no associative arrays, no \s.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo"

base=""
if [ "${1:-}" = "--base" ]; then
  base="${2:-HEAD}"
fi

# Normalize git paths to be relative to the skill dir (cwd). git diff reports
# repo-root-relative paths while git ls-files reports cwd-relative; strip the
# skill-dir prefix (git rev-parse --show-prefix) from diff paths so both bases
# agree and patterns like ^SKILL\.md match. Portable: bash 3.2, no \s in sed.
prefix="$(git rev-parse --show-prefix 2>/dev/null || true)"
strip_prefix() { sed "s|^${prefix}||" 2>/dev/null; }

if [ -n "$base" ]; then
  paths="$(git diff --name-only "$base" -- 2>/dev/null | strip_prefix || true)"
else
  paths="$( { git diff --name-only HEAD -- 2>/dev/null | strip_prefix; git ls-files --others --exclude-standard 2>/dev/null; } | sort -u )"
fi

if [ -z "$paths" ]; then
  echo "doc-impact-check: no changed paths."
  exit 0
fi

# affected_doc <doc> -> prints suggestion string (empty if unaffected).
# Re-scans paths per doc (small sets, O(docs*paths) is fine).
affected_doc() {
  local doc="$1" out=""
  while IFS= read -r p; do
    [ -n "$p" ] || continue
    case "$p" in
      SKILL.md)
        case "$doc" in
          SKILL.md) out+="协议/流程变更；" ;;
          README.md) out+="产物/流程描述；" ;;
          operation-guide.md) out+="操作流程；" ;;
          AGENTS.md) out+="协议硬约束/边界；" ;;
          CHANGELOG.md) out+="对外能力变；" ;;
        esac ;;
      references/grilling-questions.md|references/team-roles.md|references/output-structure.md|references/workflow-template.md)
        case "$doc" in
          SKILL.md) out+="引用的通用参考；" ;;
          README.md) out+="参考清单；" ;;
          AGENTS.md) out+="参考清单；" ;;
          operation-guide.md) out+="操作参考；" ;;
        esac ;;
      references/domain-presets/*)
        case "$doc" in
          SKILL.md) out+="预设清单/映射；" ;;
          README.md) out+="预设清单；" ;;
          AGENTS.md) out+="预设配对/PRESETS 须同步；" ;;
          CHANGELOG.md) out+="预设变；" ;;
        esac ;;
      scripts/create_research_skeleton.py)
        case "$doc" in
          AGENTS.md) out+="初始化器逻辑；" ;;
          README.md) out+="命令/选项；" ;;
          operation-guide.md) out+="骨架生成操作；" ;;
          CHANGELOG.md) out+="骨架生成行为变；" ;;
        esac ;;
      scripts/grade_research_init.py|evals/evals.json)
        case "$doc" in
          AGENTS.md) out+="断言/检查器映射；" ;;
          operation-guide.md) out+="评分用法；" ;;
          CHANGELOG.md) out+="评分/eval 变；" ;;
        esac ;;
      scripts/aggregate_benchmark.py)
        case "$doc" in
          AGENTS.md) out+="benchmark 脚本；" ;;
          README.md) out+="脚本表；" ;;
          operation-guide.md) out+="benchmark 用法；" ;;
        esac ;;
      scripts/validate.sh|scripts/install.sh|scripts/install.ps1|scripts/release.sh|scripts/doc-impact-check.sh|scripts/githooks/pre-push)
        case "$doc" in
          AGENTS.md) out+="验证矩阵/脚本表；" ;;
          README.md) out+="脚本表；" ;;
          CHANGELOG.md) out+="校验/发布机制变；" ;;
        esac ;;
      .claude-plugin/plugin.json|.claude-plugin/marketplace.json)
        case "$doc" in
          AGENTS.md) out+="插件清单/注册策略；" ;;
          README.md) out+="安装/升级；" ;;
          CHANGELOG.md) out+="插件机制变；" ;;
        esac ;;
      install-profiles/core.yaml)
        case "$doc" in
          AGENTS.md) out+="安装档案；" ;;
          README.md) out+="安装档案；" ;;
          CHANGELOG.md) out+="安装档案变；" ;;
        esac ;;
      agents/openai.yaml)
        case "$doc" in
          AGENTS.md) out+="调用策略；" ;;
          README.md) out+="调用入口；" ;;
        esac ;;
      package.json)
        case "$doc" in
          CHANGELOG.md) out+="版本变；" ;;
          SKILL.md) out+="版本须同步；" ;;
        esac ;;
      .agents/adr/*)
        case "$doc" in
          AGENTS.md) out+="若决策反转须 supersede；" ;;
        esac ;;
      operation-guide.md|install-guide.md)
        case "$doc" in
          CHANGELOG.md) out+="用户文档变；" ;;
        esac ;;
    esac
  done <<< "$paths"
  printf '%s' "$out"
}

echo "doc-impact-check: 改动路径 -> 文档同步建议（建议、非阻断）"
echo

for doc in SKILL.md README.md AGENTS.md operation-guide.md install-guide.md CHANGELOG.md; do
  s="$(affected_doc "$doc")"
  if [ -n "$s" ]; then
    printf '  [x] %-22s %s\n' "$doc" "$s"
  else
    printf '  [-] %-22s （本次改动未触及）\n' "$doc"
  fi
done

echo
echo "AGENTS.md §9 文档影响检查表（自动标注：[x]=是 / [-]=否 / [ ]=待人工判断）"
touch_skill=0
echo "$paths" | grep -qE '^(SKILL\.md|references/|scripts/create_research_skeleton\.py)' && touch_skill=1
printf '  [%s] 协议规则 / 调研流程 / 产出 / 输入是否变化？\n' "$( [ "$touch_skill" = 1 ] && echo x || echo - )"
echo "  [ ] 用户安装 / 调用 / 使用方式是否变化？（人工判断）"
touch_struct=0
echo "$paths" | grep -qE '^(references/|scripts/|evals/|\.claude-plugin/|install-profiles/)' && touch_struct=1
printf '  [%s] 仓库结构或文件职责是否变化？\n' "$( [ "$touch_struct" = 1 ] && echo x || echo - )"
touch_val=0
echo "$paths" | grep -qE '^(scripts/validate\.sh|scripts/release\.sh|\.claude-plugin/|package\.json)' && touch_val=1
printf '  [%s] 校验 / 版本 / 发布方式是否变化？\n' "$( [ "$touch_val" = 1 ] && echo x || echo - )"
echo "  [ ] 其余项由人工/Agent 判断。"
echo
echo "（doc-impact-check 仅建议，不阻断。改完后按 AGENTS.md §11 验证矩阵跑对应命令。）"
exit 0
