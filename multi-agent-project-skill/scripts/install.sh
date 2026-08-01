#!/usr/bin/env bash
#
# Cross-agent installer for multi-agent-project-skill.
#
# Links the skill bundle into Codex / Claude Code skill directories, and can
# write a Cursor rule file. The whole skill directory is linked as a single
# bundle so that relative references (references/..., scripts/...) keep
# resolving.
#
# Usage:
#   bash scripts/install.sh --agent codex
#   bash scripts/install.sh --agent claude
#   bash scripts/install.sh --agent cursor --target <project-dir>
#   bash scripts/install.sh --agent all
#   bash scripts/install.sh --agent claude --unlink
#
# Options:
#   --agent codex|claude|cursor|all   Which agent to install for (default: codex)
#   --target <dir>                    Target project for Cursor rules
#   --force                           Replace an existing symlink
#   --unlink                          Remove the symlinks instead of creating them
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
name="multi-agent-project-skill"
version="$(grep -m1 '"version"' "$repo/package.json" | sed -E 's/.*"version": *"?([^",]+)"?.*/\1/')"

agent=""
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
  local rule="$dir/multi-agent-project-skill.mdc"
  if [ "$unlink" -eq 1 ]; then
    rm -f "$rule" && echo "removed: $rule"
    return
  fi
  cat > "$rule" << RULE
---
description: Multi-agent project coordination (init skeleton, claim/handoff/review/integrate protocol)
globs:
alwaysApply: false
---

For projects that may be edited by multiple AI agents in parallel or handed off
at any time, read the installed multi-agent-project-skill bundle at:
$repo

Initialize a project with scripts/init_workspace.py, then follow the .agent/
bookkeeping protocol (task board, file locks, handoffs, atomic task-id via
mkdir). Never erase/reset/overwrite other agents' unmerged work; do not commit
or push unless explicitly asked.
RULE
  echo "wrote: $rule"
}

echo "$name v$version  (repo: $repo)"

case "$agent" in
  codex) install_codex ;;
  claude) install_claude ;;
  cursor) install_cursor ;;
  all) install_codex; install_claude; install_cursor ;;
  *) echo "unknown agent: $agent (use codex|claude|cursor|all)" >&2; exit 1 ;;
esac

if [ "$unlink" -eq 0 ]; then
  py_bin="$(command -v python3 || command -v python || true)"
  echo ""
  echo "-- 依赖体检 --"
  if [ -n "$py_bin" ]; then
    echo "  [OK]   python（必需：init_workspace.py 初始化器）: $py_bin"
  else
    echo "  [缺失] python（必需）：init_workspace.py 将无法运行"
    echo "         macOS: xcode-select --install 或 brew install python3"
    echo "         其他:  https://www.python.org/downloads/"
  fi
fi
