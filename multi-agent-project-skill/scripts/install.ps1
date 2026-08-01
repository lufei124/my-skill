# Windows native installer for multi-agent-project-skill (PowerShell 5.1+).
# Mirrors scripts/install.sh. Symlink preferred (developer mode), copy fallback.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent claude
#   powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent all
#   powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent cursor -Target .\my-project
#   powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent claude -Unlink
[CmdletBinding()]
param(
  [ValidateSet('codex','claude','cursor','all')]
  [string]$Agent = 'codex',
  [string]$Target = '',
  [switch]$Force,
  [switch]$Unlink
)

$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$name = 'multi-agent-project-skill'
$pkg = Get-Content (Join-Path $repo 'package.json') -Raw | ConvertFrom-Json
$version = $pkg.version

function Link-SkillDir([string]$src, [string]$dst) {
  if ($Unlink) {
    if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
    Write-Output "removed: $dst"
    return
  }
  if (Test-Path $dst) {
    $item = Get-Item $dst -Force
    $isLink = $item.LinkType -ne $null
    if ($isLink) {
      if ($Force) {
        Remove-Item -Recurse -Force $dst
      } else {
        Write-Output "skip (symlink exists, use -Force): $dst"
        return
      }
    } else {
      Write-Output "skip (real file/dir exists, won't touch): $dst"
      return
    }
  }
  try {
    New-Item -ItemType SymbolicLink -Path $dst -Target $src | Out-Null
  } catch {
    # Fallback: copy (developer mode unavailable).
    Copy-Item -Recurse -Force $src $dst
  }
  Write-Output "linked: $dst -> $src"
}

function Install-Codex {
  $dir = if ($env:CODEX_SKILLS_DIR) { $env:CODEX_SKILLS_DIR } else { Join-Path $env:USERPROFILE '.codex\skills' }
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  Link-SkillDir $repo (Join-Path $dir $name)
}

function Install-Claude {
  $dir = if ($env:CLAUDE_SKILLS_DIR) { $env:CLAUDE_SKILLS_DIR } else { Join-Path $env:USERPROFILE '.claude\skills' }
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  Link-SkillDir $repo (Join-Path $dir $name)
}

function Install-Cursor {
  $dir = if ($Target) { Join-Path $Target '.cursor\rules' } elseif ($env:CURSOR_RULES_DIR) { $env:CURSOR_RULES_DIR } else { Join-Path $env:USERPROFILE '.cursor\rules' }
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  $rule = Join-Path $dir "$name.mdc"
  if ($Unlink) {
    if (Test-Path $rule) { Remove-Item -Force $rule }
    Write-Output "removed: $rule"
    return
  }
  $body = @"
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
"@
  Set-Content -Path $rule -Value $body -Encoding UTF8
  Write-Output "wrote: $rule"
}

Write-Output "$name v$version  (repo: $repo)"

switch ($Agent) {
  'codex'   { Install-Codex }
  'claude'  { Install-Claude }
  'cursor'  { Install-Cursor }
  'all'     { Install-Codex; Install-Claude; Install-Cursor }
}

if (-not $Unlink) {
  $pyBin = (Get-Command python -ErrorAction SilentlyContinue) ?? (Get-Command python3 -ErrorAction SilentlyContinue)
  Write-Output ''
  Write-Output '-- 依赖体检 --'
  if ($pyBin) {
    Write-Output "  [OK]   python（必需：init_workspace.py 初始化器）: $($pyBin.Source)"
  } else {
    Write-Output '  [缺失] python（必需）：init_workspace.py 将无法运行'
    Write-Output '         winget install Python.Python.3 或 https://www.python.org/downloads/'
  }
}
