#!/usr/bin/env bash
#
# Cross-agent installer for mobile-game-product-forge.
#
# Links the skill bundle into Codex / Claude Code skill directories, and can
# optionally initialize a project knowledge pack. The whole repo is linked as a
# single bundle so that sub-skill relative references (../../references/...) keep
# resolving.
#
# Usage:
#   bash scripts/install.sh --agent codex
#   bash scripts/install.sh --agent claude
#   bash scripts/install.sh --agent cursor --target <project-dir>
#   bash scripts/install.sh --agent all
#   bash scripts/install.sh --agent codex --profile core-life-reboots --target <project-dir>
#   bash scripts/install.sh --agent codex --unlink
#
# Options:
#   --agent codex|claude|cursor|all   Which agent to install for (default: codex)
#   --profile core|core-life-reboots  Knowledge profile for --target install (default: core)
#   --target <dir>                    Target game project for Cursor rules / knowledge pack
#   --force                           Replace an existing symlink
#   --unlink                          Remove the symlinks instead of creating them
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
name="mobile-game-product-forge"
version="$(grep -m1 '"version"' "$repo/package.json" | sed -E 's/.*"version": *"?([^",]+)"?.*/\1/')"

agent=""
profile="core"
target=""
force=0
unlink=0

usage() {
  sed -n '3,22p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --agent) agent="$2"; shift 2 ;;
    --profile) profile="$2"; shift 2 ;;
    --target) target="$2"; shift 2 ;;
    --force) force=1; shift ;;
    --unlink) unlink=1; shift ;;
    -h|--help) usage 0 ;;
    *) echo "unknown argument: $1" >&2; usage 1 ;;
  esac
done

[ -z "$agent" ] && agent="codex"

# link_skill_dir <src> <dst>
link_skill_dir() {
  local src="$1" dst="$2"
  if [ "$unlink" -eq 1 ]; then
    rm -f "$dst" && echo "removed: $dst"
    return
  fi
  if [ -L "$dst" ]; then
    if [ "$force" -eq 1 ]; then
      rm -f "$dst"
    else
      echo "skip (symlink exists, use --force): $dst"
      return
    fi
  elif [ -e "$dst" ]; then
    echo "skip (real file/dir exists, won't touch): $dst"
    return
  fi
  ln -s "$src" "$dst"
  echo "linked: $dst -> $src"
}

install_codex() {
  local dir="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}"
  mkdir -p "$dir"
  link_skill_dir "$repo" "$dir/$name"
}

install_claude() {
  local dir="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
  mkdir -p "$dir"
  link_skill_dir "$repo" "$dir/$name"
}

install_cursor() {
  local dir
  if [ -n "$target" ]; then
    dir="$target/.cursor/rules"
  else
    dir="${CURSOR_RULES_DIR:-$HOME/.cursor/rules}"
  fi
  mkdir -p "$dir"
  local rule="$dir/mobile-game-product-forge.mdc"
  if [ "$unlink" -eq 1 ]; then
    rm -f "$rule" && echo "removed: $rule"
    return
  fi
  cat > "$rule" << RULE
---
description: Mobile-game product requirements workshop (PRD, prototype, review, analytics)
globs:
alwaysApply: false
---

For mobile-game requirements, PRDs, prototypes, configuration, analytics, or
reviews, read the installed mobile-game-product-forge skill bundle at:
$repo

Project knowledge lives under knowledge/ and is read-only during normal product
work. Generated PRDs go to docs/prd/; working history goes to history/.
RULE
  echo "wrote: $rule"
}

# sha8 <file> -> first 8 hex chars of sha256 (portable: sha256sum on Linux, shasum on macOS).
sha8() {
  local h=""
  h="$(sha256sum "$1" 2>/dev/null | awk '{print $1}')" || true
  [ -n "$h" ] || h="$(shasum -a 256 "$1" 2>/dev/null | awk '{print $1}')" || true
  printf '%s' "${h:0:8}"
}

# prev_sha_of <receipt> <relpath> -> sha8 recorded in a previous receipt's files: manifest
# (empty if receipt absent or path not recorded -> first install / backward compat).
prev_sha_of() {
  [ -e "$1" ] || return 0
  awk -v p="$2" '/^files:/{f=1;next} /^[a-z_]/{f=0} f && $1==p {print $2; exit}' "$1" 2>/dev/null
}

# install_knowledge copies the selected pack into <target>/knowledge without
# overwriting existing files; conflicts are reported only.
install_knowledge() {
  [ -z "$target" ] && { echo "knowledge install needs --target" >&2; return; }
  [ "$profile" != "core-life-reboots" ] && { echo "profile '$profile' has no knowledge pack; skipping"; return; }
  local pack="$repo/knowledge-packs/life-reboots/knowledge"
  [ -d "$pack" ] || { echo "knowledge pack not found: $pack" >&2; return; }
  local pack_manifest="${pack%/*}/PACK.md"
  local pack_ver
  pack_ver="$(grep -m1 '^version:' "$pack_manifest" | sed -E 's/^version:[[:space:]]*//' | tr -d '[:space:]')"
  [ -n "$pack_ver" ] || { echo "PACK.md version not found: $pack_manifest" >&2; return 1; }
  local dst="$target/knowledge"
  mkdir -p "$dst"
  local receipt_dir="$dst/.installed-packs"
  mkdir -p "$receipt_dir"
  local receipt="$receipt_dir/life-reboots.md"
  local created=0 identical=0 pack_updated=0 conflicts=0 human_added=0
  local files_block="" rel out psha tsha old_sha
  while IFS= read -r -d '' f; do
    rel="${f#"$pack"/}"
    psha="$(sha8 "$f")"
    files_block="${files_block}  ${rel}  ${psha}"$'\n'
    out="$dst/$rel"
    if [ ! -e "$out" ]; then
      mkdir -p "$(dirname "$out")"
      cp "$f" "$out"
      created=$((created+1))
    else
      tsha="$(sha8 "$out")"
      if [ "$tsha" = "$psha" ]; then
        identical=$((identical+1))
      else
        old_sha="$(prev_sha_of "$receipt" "$rel")"
        if [ -n "$old_sha" ] && [ "$tsha" = "$old_sha" ]; then
          # target unchanged since last install; pack upgraded this file -> update
          cp "$f" "$out"
          pack_updated=$((pack_updated+1))
        else
          # target differs from both pack and last-installed (or no manifest) -> human modified -> keep
          echo "conflict (kept existing): $out"
          conflicts=$((conflicts+1))
        fi
      fi
    fi
  done < <(find "$pack" -type f -print0)

  # Report human-added files (in target, not from pack) for provenance; never touch them.
  if [ -d "$dst" ]; then
    while IFS= read -r -d '' tf; do
      rel="${tf#"$dst"/}"
      case "$rel" in
        .installed-packs/*) continue ;;
      esac
      [ -e "$pack/$rel" ] && continue
      human_added=$((human_added+1))
    done < <(find "$dst" -type f -print0)
  fi

  # write a non-invasive install receipt with a files: manifest (relpath + sha256[:8]).
  # installed_at changes every run, so exclude it when deciding whether the install
  # metadata actually changed; the files: manifest makes pack upgrades visible in the
  # stable comparison (shas change) while re-runs of the same pack stay "refreshed".
  # installed_from is informational only (no consumer parses it). Record a stable
  # source id instead of an absolute path: plugin-cache installs would otherwise
  # pin a versioned cache dir that dies on the next upgrade.
  local source_id
  case "$repo" in
    "$HOME/.claude/plugins/cache/"*) source_id="plugin:$name@$version" ;;
    *) source_id="repo:$repo" ;;
  esac
  local tmp
  tmp="$(mktemp)"
  cat > "$tmp" << REC
pack: life-reboots
version: $pack_ver
installed_from: $source_id
installed_skill_version: $version
installed_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)
files:
REC
  printf '%s' "$files_block" >> "$tmp"
  local new_stable prev_stable
  new_stable="$(grep -v '^installed_at:' "$tmp" 2>/dev/null || true)"
  prev_stable="$(grep -v '^installed_at:' "$receipt" 2>/dev/null || true)"
  local receipt_action="created"
  if [ -e "$receipt" ]; then
    if [ "$new_stable" = "$prev_stable" ]; then
      receipt_action="refreshed"
    else
      receipt_action="updated"
    fi
  fi
  mv -f "$tmp" "$receipt"
  echo "receipt: $receipt_action -> $receipt"
  echo "knowledge: created=$created identical=$identical pack_updated=$pack_updated conflicts=$conflicts human_added=$human_added"
}

echo "mobile-game-product-forge v$version  (repo: $repo)"

case "$agent" in
  codex) install_codex ;;
  claude) install_claude ;;
  cursor) install_cursor ;;
  all) install_codex; install_claude; install_cursor ;;
  *) echo "unknown agent: $agent (use codex|claude|cursor|all)" >&2; exit 1 ;;
esac

if [ -n "$target" ]; then
  if [ "$unlink" -eq 1 ]; then
    echo "knowledge: --unlink leaves project knowledge in place (remove manually if needed)"
  else
    install_knowledge
  fi
fi

if [ "$unlink" -eq 0 ]; then
  py_bin="$(command -v python3 || command -v python || true)"
  node_bin="$(command -v node || command -v npx || true)"
  echo ""
  echo "-- 依赖体检 --"
  if [ -n "$py_bin" ]; then
    echo "  [OK]   python（必需：阶段门禁与 PRD 校验脚本）: $py_bin"
  else
    echo "  [缺失] python（必需）：check-stage-gate.py / lint-prd.py 将无法运行"
    echo "         macOS: xcode-select --install 或 brew install python3"
    echo "         其他:  https://www.python.org/downloads/"
  fi
  if [ -n "$node_bin" ]; then
    echo "  [OK]   node/npx（可选：仅飞书发布需要）"
  else
    echo "  [缺失] node/npx（可选：仅飞书发布需要，不影响本次安装）"
  fi

  cat <<'FEISHU_NOTE'

-- 飞书发布（可选） --
如需把 PRD 发布到飞书云文档：
  1) 安装飞书 CLI:       npx @larksuite/cli@latest install
  2) (推荐)配套 skills:  npx skills add larksuite/cli -y -g
  3) 在目标项目运行 setup 完成飞书绑定授权
FEISHU_NOTE
fi
