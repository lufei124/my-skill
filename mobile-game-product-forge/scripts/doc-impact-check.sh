#!/usr/bin/env bash
#
# doc-impact-check.sh — 文档影响预检（AGENTS.md §9/§10 机械化）
#
# 在 Agent 改完代码、进入人工/Agent 文档影响判断之前运行的脚本化预检层。
# 它不替代判断、不修改任何文件、不跑 validate.sh；只把可机器判定的
# 「改动路径 -> AGENTS §9 文档同步建议」与「§10 检查表自动标注」做出来，
# 其余标「待人工/Agent 判断」。
#
# 退出码恒 0（建议性、非阻断）。CI 不跑本脚本。
#
# 用法：
#   bash scripts/doc-impact-check.sh                     # 默认：git 工作树改动 + 未跟踪新文件
#   bash scripts/doc-impact-check.sh --base main         # 与分支/ref 对比（git diff --name-only <ref>）
#   bash scripts/doc-impact-check.sh path/a path/b      # 显式指定改动列表（非 git 友好）
#
# 依赖：bash + git（仅当未显式传路径时用于取改动列表）+ grep/awk/case。零外部依赖，
#       与 scripts/validate.sh 同款 BSD 兼容约定（grep 不引 rg；[[:space:]] 不用 \s）。
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo"

# 收集改动文件列表（仓库相对路径），统一写入临时文件后去重排序。
changes_file=""
base=""
explicit=0
if [ $# -gt 0 ] && [ "${1:-}" = "--base" ]; then
  base="${2:?--base 需要一个 ref}"
  shift 2
fi
changes_file="$(mktemp)"
if [ $# -gt 0 ]; then
  explicit=1
  for p in "$@"; do
    # 归一为仓库相对路径
    if [ "${p#/}" != "$p" ]; then abs="$p"; else abs="$repo/$p"; fi
    case "$abs" in
      "$repo"/*) rel="${abs#$repo/}";;
      *) rel="$p";;
    esac
    printf '%s\n' "$rel" >> "$changes_file"
  done
fi
if [ "$explicit" -eq 0 ]; then
  if [ -n "$base" ] && git rev-parse --verify "$base" >/dev/null 2>&1; then
    git diff --name-only "$base" 2>/dev/null >> "$changes_file" || true
  else
    git diff --name-only 2>/dev/null >> "$changes_file" || true
  fi
  git ls-files --others --exclude-standard 2>/dev/null >> "$changes_file" || true
fi
# 去重、去空、稳定排序
changes="$(grep -v '^[[:space:]]*$' "$changes_file" | sort -u || true)"
rm -f "$changes_file"

if [ -z "$changes" ]; then
  echo "== 文档影响预检（AGENTS.md §9/§10）=="
  echo "改动文件（0）：无"
  echo "（git 无工作树改动且未传显式路径；跳过预检）"
  exit 0
fi

# 每个改动文件触发哪些文档「检查」建议（§9 同步条件映射，机器可判定部分）。
# 约定：用关联文档集合表示；逐文件累加。值通过临时文件收集再聚合输出。
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# add <doc> 建议检查某文档；warn <msg> 出告警
reco_file="$tmp/reco"
warn_file="$tmp/warn"

reco() { printf '%s\n' "$1" >> "$reco_file"; }
warn() { printf '%s\n' "$1" >> "$warn_file"; }

n=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  n=$((n+1))
  case "$f" in
    SKILL.md)
      reco "README.md"; reco "AGENTS.md"; reco "CHANGELOG.md"
      reco "根目录 SKILL.md"; reco "相关子 Skill 的 SKILL.md（路由/前置若变）"; reco "references/（若引用规范变）"
      ;;
    skills/*/SKILL.md)
      sk=$(basename "$(dirname "$f")")
      reco "该子 Skill 的 SKILL.md（${sk}）"; reco "README.md"; reco "AGENTS.md"; reco "CHANGELOG.md"
      # 被该 Skill 引用的 references（grep 引用）
      for r in $(grep -oE 'references/[A-Za-z0-9_-]+\.md' "$f" 2>/dev/null | sort -u); do
        reco "${r}（被 ${sk} 引用）"
      done
      # setup 不入路由表；其余子 Skill 路由在根 SKILL.md
      if [ "$sk" != "setup-mobile-game-product-forge" ]; then
        reco "根目录 SKILL.md（确认路由表登记 ${sk}）"
      fi
      ;;
    agents/openai.yaml)
      reco "agents/openai.yaml（根编排器 interface/调用策略）"; reco "README.md"; reco "AGENTS.md"; reco "CHANGELOG.md"
      ;;
    skills/*/agents/openai.yaml)
      sk=$(basename "$(dirname "$(dirname "$f")")")
      reco "agents/openai.yaml（$sk interface/调用策略）"; reco "README.md"; reco "CHANGELOG.md"
      ;;
    references/*.md)
      rb=$(basename "$f")
      reco "references/${rb}（本规范）"; reco "README.md"; reco "AGENTS.md"; reco "CHANGELOG.md"
      reco "根目录 SKILL.md（前置若变）"
      # 引用该 reference 的子 Skill
      for d in "$repo"/skills/*/; do
        [ -d "$d" ] || continue
        nm=$(basename "$d")
        if grep -qF "$rb" "$d/SKILL.md" 2>/dev/null; then
          reco "${nm} 的 SKILL.md（引用 ${rb}）"
        fi
      done
      # prd-spec 模板被 lint 校验：改格式契约须同步 lint-prd.py 与夹具
      case "$rb" in prd-spec.md|templates.md) reco "scripts/lint-prd.py（若该规范被机器校验）"; reco "fixtures/（若校验行为变）";; esac
      ;;
    install-profiles/*.yaml)
      reco "install-profiles/$(basename "$f")（本档案）"; reco "README.md"; reco "AGENTS.md"; reco "CHANGELOG.md"
      reco "scripts/validate.sh（source_files 契约 #6/#12）"
      ;;
    .claude-plugin/plugin.json)
      reco ".claude-plugin/plugin.json（本清单）"; reco "README.md"; reco "AGENTS.md"; reco "CHANGELOG.md"
      ;;
    scripts/validate*.sh)
      reco "AGENTS.md（验证矩阵 §12）"; reco "README.md（脚本表）"; reco "CHANGELOG.md"
      ;;
    scripts/lint-prd.py)
      reco "AGENTS.md（验证矩阵 §12）"; reco "README.md（脚本表）"; reco "CHANGELOG.md"; reco "fixtures/（若校验行为变）"
      ;;
    scripts/install.sh|scripts/install.ps1)
      reco "AGENTS.md（安装段/验证矩阵）"; reco "README.md（安装方式/脚本表）"; reco "CHANGELOG.md"
      ;;
    scripts/*)
      # 通用脚本兜底（如 scripts/doc-impact-check.sh 等维护工具）
      reco "AGENTS.md（相关段/验证矩阵）"; reco "README.md（脚本表）"; reco "CHANGELOG.md"
      ;;
    package.json)
      reco "package.json（唯一版本源）"; reco "根目录 SKILL.md（两版本字段）"; reco ".claude-plugin/plugin.json"; reco "README.md"; reco "AGENTS.md"; reco "CHANGELOG.md"
      ;;
    fixtures/*.md)
      reco "fixtures/$(basename "$f")（本夹具）"; reco "CHANGELOG.md"; reco "AGENTS.md（验证矩阵若涉 lint）"
      ;;
    fixtures/*.json)
      reco "fixtures/$(basename "$f")（路由/能力回归夹具）"; reco "scripts/validate-regression-fixtures.py"; reco "docs/capability-regression.md"; reco "README.md"; reco "AGENTS.md（验证矩阵 §12）"; reco "CHANGELOG.md"
      ;;
    docs/capability-regression.md)
      reco "docs/capability-regression.md（真实质量回归协议）"; reco "fixtures/（路由/能力回归夹具）"; reco "scripts/validate-regression-fixtures.py"; reco "README.md"; reco "AGENTS.md（验证矩阵 §12）"; reco "CHANGELOG.md"
      ;;
    .agents/adr/*.md)
      reco ".agents/adr/（架构决策记录）"; reco "AGENTS.md"; reco "CHANGELOG.md"
      ;;
    AGENTS.md)
      reco "AGENTS.md（本手册）"; reco "CHANGELOG.md"
      ;;
    operation-guide.md)
      reco "operation-guide.md（用户操作文档）"; reco "README.md"; reco "AGENTS.md"; reco "CHANGELOG.md"
      ;;
    README.md)
      reco "README.md（用户文档）"; reco "CHANGELOG.md"
      ;;
    CHANGELOG.md)
      : # 改 CHANGELOG 不触发其他文档同步
      ;;
    knowledge-packs/*)
      warn "knowledge-packs 项目知识对 AI 只读（ADR-0003）：$f 被修改。AI 不直接改项目知识；如为知识包正规升级，请走 game-knowledge-maintenance-proposal 流程产出提案，由人工落库。"
      ;;
    history/*)
      warn "history/ 为历史归档，只作参考、非当前规范：$f 被修改。不得把历史当回滚依据或当前规范来源。"
      ;;
    *)
      # 兜底：未命中已知映射。
      case "$f" in
        skills/*)
          # skills/ 下非 SKILL.md / agents/openai.yaml 的新路径，可能是新增子 Skill 的附属文件
          warn "skills/ 下出现新路径 ${f}：若是新增子 Skill，须按 AGENTS §7 同步清单登记（默认 skills/ 扫描、两份 install-profiles、根 SKILL.md 路由、路由回归夹具、README、AGENTS、workflow.md、CHANGELOG、validate.sh）；plugin.json 只保留根入口 ./。"
          ;;
        *)
          warn "改动路径 $f 不在已知映射表内；由人工/Agent 按 AGENTS §9 判断可能影响的文档。"
          ;;
      esac
      ;;
  esac
done <<< "$changes"

# §10 检查表自动标注：根据改动路径是否触及相关区域，标注 [x]/[-]/[ ]。
# [x]=自动判定「是」；[-]=自动判定「否」；[ ]=可能为真但无法机械确认 -> 待人工判断。
touch_skill=0; touch_route=0; touch_install=0; touch_struct=0; touch_validate=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  case "$f" in
    skills/*/SKILL.md|skills/*/agents/openai.yaml|SKILL.md) touch_skill=1 ;;
    install-profiles/*.yaml|scripts/install.sh|scripts/install.ps1|skills/setup-mobile-game-product-forge/*) touch_install=1 ;;
    scripts/validate*.sh|scripts/doc-impact-check.sh|scripts/lint-prd.py|scripts/validate-regression-fixtures.py|.github/*|fixtures/*|docs/capability-regression.md) touch_validate=1 ;;
    package.json|.claude-plugin/plugin.json|knowledge-packs/*|references/*|operation-guide.md|agents/openai.yaml) touch_struct=1 ;;
  esac
done <<< "$changes"
# 路由/跨阶段状态变化：触及根 SKILL.md 才可能为真
while IFS= read -r f; do
  [ -n "$f" ] || continue
  case "$f" in SKILL.md) touch_route=1 ;; esac
done <<< "$changes"

echo "== 文档影响预检（AGENTS.md §9/§10）=="
echo "改动文件（${n}）："
while IFS= read -r f; do [ -n "$f" ] && echo "  - $f"; done <<< "$changes"
echo
echo "§9 同步建议（机器可判定）——建议检查以下文档；其余待人工/Agent 判断："
if [ -s "$reco_file" ]; then
  sort -u "$reco_file" | while IFS= read -r d; do printf '  [建议] %s\n' "$d"; done
else
  echo "  （无显式复现型映射命中；按改动类型人工判断）"
fi
if [ -s "$warn_file" ]; then
  echo
  echo "告警："
  while IFS= read -r w; do printf '  ! %s\n' "$w"; done < "$warn_file"
fi
echo
echo "§10 文档影响检查表（自动标注 [x]=是 / [-]=否 / [ ]=待人工判断）："
[ "$touch_skill" -eq 1 ]   && printf '  [x] Skill 功能/输入/输出/流程是否变化？\n'   || printf '  [-] Skill 功能/输入/输出/流程是否变化？（未触及 Skill 文件）\n'
[ "$touch_route" -eq 1 ]   && printf '  [x] 主编排器路由或跨阶段状态是否变化？\n'   || printf '  [-] 主编排器路由或跨阶段状态是否变化？（未触及根 SKILL.md）\n'
[ "$touch_install" -eq 1 ] && printf '  [x] 用户安装/调用/使用方式是否变化？\n' || printf '  [-] 用户安装/调用/使用方式是否变化？（未触及安装/调用文件）\n'
[ "$touch_struct" -eq 1 ]  && printf '  [x] 仓库结构或文件职责是否变化？\n' || printf '  [-] 仓库结构或文件职责是否变化？（未触及目录/清单/知识包/references）\n'
[ "$touch_validate" -eq 1 ]&& printf '  [x] 校验/版本/发布方式是否变化？\n'         || printf '  [-] 校验/版本/发布方式是否变化？（未触及校验/版本/CI/夹具文件）\n'
printf '  [ ] README.md 是否需要更新？\n'
printf '  [ ] operation-guide.md 操作文档是否需要更新？\n'
printf '  [ ] AGENTS.md 是否需要更新？\n'
printf '  [ ] 根目录 SKILL.md 是否需要更新？\n'
printf '  [ ] 相关子 Skill 的 SKILL.md 是否需要更新？\n'
printf '  [ ] references/ 是否需要更新？\n'
printf '  [ ] install-profiles/ 是否需要更新？\n'
printf '  [ ] Claude 插件清单是否需要更新？\n'
printf '  [ ] agents/openai.yaml 是否需要更新？\n'
printf '  [ ] CHANGELOG.md 是否需要更新？\n'
echo
echo "下一步：人工/Agent 按 AGENTS §9/§10 裁定，改受影响文档，再跑 §12 验证矩阵对应强制命令（不含本预检）。"

exit 0