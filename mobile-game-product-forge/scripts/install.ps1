# Cross-agent installer for mobile-game-product-forge (Windows native).
#
# Mirrors scripts/install.sh for PowerShell 5.1+ (ships with Windows). Copies the
# skill bundle into Codex / Claude Code skill directories (symlink when Developer
# Mode is available, copy otherwise), and can initialize a project knowledge pack.
# Also sets the MOBILE_GAME_PRODUCT_FORGE user environment variable so the runtime
# MGPF locator resolves out of the box (Windows copies may live at non-standard paths).
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent codex
#   powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent claude
#   powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent cursor -Target <project-dir>
#   powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent all
#   powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent codex -Profile core-life-reboots -Target <project-dir>
#   powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent codex -Unlink
#
# Options:
#   -Agent codex|claude|cursor|all   Which agent to install for (default: codex)
#   -Profile core|core-life-reboots  Knowledge profile for -Target install (default: core)
#   -Target <dir>                    Target game project for Cursor rules / knowledge pack
#   -Force                           Replace an existing install
#   -Unlink                          Remove the install instead of creating it
[CmdletBinding()]
param(
  [ValidateSet('codex','claude','cursor','all')][string]$Agent = 'codex',
  [ValidateSet('core','core-life-reboots')][string]$Profile = 'core',
  [string]$Target = '',
  [switch]$Force,
  [switch]$Unlink
)

$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path "$PSScriptRoot/..").Path
$name = 'mobile-game-product-forge'
$pkg = Get-Content "$repo/package.json" -Raw | ConvertFrom-Json
$version = $pkg.version

# sha8 <file> -> first 8 hex chars of SHA256 (lowercase, matches install.sh sha256sum/shasum).
function sha8([string]$file) {
  return (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.Substring(0, 8)
}

# prev_sha_of <receipt> <relpath> -> sha8 recorded in a previous receipt's files: manifest
# (empty if receipt absent or path not recorded -> first install / backward compat).
function prev_sha_of([string]$receipt, [string]$rel) {
  if (-not (Test-Path -LiteralPath $receipt)) { return $null }
  $inFiles = $false
  foreach ($line in Get-Content -LiteralPath $receipt) {
    if ($line -match '^files:\s*$') { $inFiles = $true; continue }
    if ($line -match '^[a-z_]+:') { $inFiles = $false; continue }
    if ($inFiles -and $line -match '^\s+(\S+)\s+(\S+)\s*$') {
      if ($matches[1] -eq $rel) { return $matches[2] }
    }
  }
  return $null
}

# Link-SkillDir <src> <dst> - symlink when possible (Developer Mode), else copy.
function Link-SkillDir([string]$src, [string]$dst) {
  if ($Unlink) {
    if (Test-Path -LiteralPath $dst) {
      $item = Get-Item -LiteralPath $dst -Force
      if ($item.LinkType) { $item.Delete() } else { Remove-Item -LiteralPath $dst -Recurse -Force }
    }
    Write-Output "removed: $dst"
    return
  }
  if (Test-Path -LiteralPath $dst) {
    if ($Force) {
      $item = Get-Item -LiteralPath $dst -Force
      if ($item.LinkType) { $item.Delete() } else { Remove-Item -LiteralPath $dst -Recurse -Force }
    } else {
      Write-Output "skip (exists, use -Force): $dst"
      return
    }
  }
  try {
    New-Item -ItemType SymbolicLink -Path $dst -Value $src -ErrorAction Stop | Out-Null
    Write-Output "linked: $dst -> $src"
  } catch {
    Copy-Item -LiteralPath $src -Destination $dst -Recurse -Force
    Write-Output "copied: $dst (symlink unavailable, used copy)"
  }
}

function Install-Codex {
  $dir = if ($env:CODEX_SKILLS_DIR) { $env:CODEX_SKILLS_DIR } else { Join-Path $env:USERPROFILE '.codex\skills' }
  New-Item -ItemType Directory -Path $dir -Force | Out-Null
  Link-SkillDir $repo (Join-Path $dir $name)
}

function Install-Claude {
  $dir = if ($env:CLAUDE_SKILLS_DIR) { $env:CLAUDE_SKILLS_DIR } else { Join-Path $env:USERPROFILE '.claude\skills' }
  New-Item -ItemType Directory -Path $dir -Force | Out-Null
  Link-SkillDir $repo (Join-Path $dir $name)
}

function Install-Cursor {
  $dir = if ($Target) { Join-Path $Target '.cursor\rules' } elseif ($env:CURSOR_RULES_DIR) { $env:CURSOR_RULES_DIR } else { Join-Path $env:USERPROFILE '.cursor\rules' }
  New-Item -ItemType Directory -Path $dir -Force | Out-Null
  $rule = Join-Path $dir 'mobile-game-product-forge.mdc'
  if ($Unlink) {
    if (Test-Path -LiteralPath $rule) { Remove-Item -LiteralPath $rule -Force }
    Write-Output "removed: $rule"
    return
  }
  $content = @"
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
"@
  Set-Content -LiteralPath $rule -Value $content -Encoding UTF8
  Write-Output "wrote: $rule"
}

# Install-Knowledge copies the selected pack into <target>/knowledge without
# overwriting existing files; conflicts are reported only. Mirrors install.sh
# so receipts are interchangeable across platforms.
function Install-Knowledge {
  if (-not $Target) { Write-Error 'knowledge install needs -Target'; return }
  if ($Profile -ne 'core-life-reboots') { Write-Output "profile '$Profile' has no knowledge pack; skipping"; return }
  $pack = Join-Path $repo 'knowledge-packs\life-reboots\knowledge'
  if (-not (Test-Path -LiteralPath $pack)) { Write-Error "knowledge pack not found: $pack"; return }
  $packManifest = Join-Path $repo 'knowledge-packs\life-reboots\PACK.md'
  $packVerLine = Get-Content -LiteralPath $packManifest | Where-Object { $_ -match '^version:' } | Select-Object -First 1
  $packVer = ($packVerLine -replace '^version:\s*', '' -replace '\s', '')
  if (-not $packVer) { Write-Error "PACK.md version not found: $packManifest"; return }

  $dst = Join-Path $Target 'knowledge'
  New-Item -ItemType Directory -Path $dst -Force | Out-Null
  $receiptDir = Join-Path $dst '.installed-packs'
  New-Item -ItemType Directory -Path $receiptDir -Force | Out-Null
  $receipt = Join-Path $receiptDir 'life-reboots.md'

  $created = 0; $identical = 0; $packUpdated = 0; $conflicts = 0; $humanAdded = 0
  $filesBlock = New-Object System.Text.StringBuilder
  foreach ($f in (Get-ChildItem -LiteralPath $pack -Recurse -File)) {
    # Native rel for filesystem ops, forward-slash rel for the cross-platform manifest.
    $relNative = $f.FullName.Substring($pack.Length + 1)
    $rel = $relNative -replace '\\', '/'
    $psha = sha8 $f.FullName
    [void]$filesBlock.AppendFormat("  {0}  {1}`n", $rel, $psha)
    $out = Join-Path $dst $relNative
    if (-not (Test-Path -LiteralPath $out)) {
      New-Item -ItemType Directory -Path (Split-Path $out -Parent) -Force | Out-Null
      Copy-Item -LiteralPath $f.FullName -Destination $out
      $created++
    } else {
      $tsha = sha8 $out
      if ($tsha -eq $psha) {
        $identical++
      } else {
        $oldSha = prev_sha_of $receipt $rel
        if ($oldSha -and $tsha -eq $oldSha) {
          Copy-Item -LiteralPath $f.FullName -Destination $out -Force
          $packUpdated++
        } else {
          Write-Output "conflict (kept existing): $out"
          $conflicts++
        }
      }
    }
  }

  if (Test-Path -LiteralPath $dst) {
    foreach ($tf in (Get-ChildItem -LiteralPath $dst -Recurse -File)) {
      $relNative = $tf.FullName.Substring($dst.Length + 1)
      $rel = $relNative -replace '\\', '/'
      if ($rel -like '.installed-packs/*') { continue }
      if (Test-Path -LiteralPath (Join-Path $pack $relNative)) { continue }
      $humanAdded++
    }
  }

  $installedAt = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
  # installed_from is informational only: record a stable source id, not a
  # versioned plugin-cache path that dies on the next upgrade.
  $pluginCachePrefix = Join-Path $env:USERPROFILE '.claude\plugins\cache'
  $sourceId = if ("$repo".StartsWith($pluginCachePrefix)) { "plugin:$name@$version" } else { "repo:$repo" }
  $tmp = [System.IO.Path]::GetTempFileName()
  $receiptContent = @"
pack: life-reboots
version: $packVer
installed_from: $sourceId
installed_skill_version: $version
installed_at: $installedAt
files:
$($filesBlock.ToString())
"@
  Set-Content -LiteralPath $tmp -Value $receiptContent -Encoding UTF8

  $newStable = ($receiptContent -split "`n" | Where-Object { $_ -notmatch '^installed_at:' }) -join "`n"
  $prevStable = if (Test-Path -LiteralPath $receipt) { (Get-Content -LiteralPath $receipt | Where-Object { $_ -notmatch '^installed_at:' }) -join "`n" } else { '' }
  $receiptAction = if (Test-Path -LiteralPath $receipt) { if ($newStable -eq $prevStable) { 'refreshed' } else { 'updated' } } else { 'created' }
  Move-Item -LiteralPath $tmp -Destination $receipt -Force
  Write-Output "receipt: $receiptAction -> $receipt"
  Write-Output "knowledge: created=$created identical=$identical pack_updated=$packUpdated conflicts=$conflicts human_added=$humanAdded"
}

Write-Output "mobile-game-product-forge v$version  (repo: $repo)"

switch ($Agent) {
  'codex' { Install-Codex }
  'claude' { Install-Claude }
  'cursor' { Install-Cursor }
  'all' { Install-Codex; Install-Claude; Install-Cursor }
}

if ($Target) {
  if ($Unlink) {
    Write-Output 'knowledge: -Unlink leaves project knowledge in place (remove manually if needed)'
  } else {
    Install-Knowledge
  }
}

# Set / clear the user environment variable so the runtime MGPF locator resolves
# without relying on the standard skill dirs (Windows copies may be elsewhere).
if ($Unlink) {
  [Environment]::SetEnvironmentVariable('MOBILE_GAME_PRODUCT_FORGE', $null, 'User')
} else {
  [Environment]::SetEnvironmentVariable('MOBILE_GAME_PRODUCT_FORGE', $repo, 'User')
}

if (-not $Unlink) {
  $pyCmd = Get-Command python3, python -ErrorAction SilentlyContinue | Select-Object -First 1
  $nodeCmd = Get-Command node, npx -ErrorAction SilentlyContinue | Select-Object -First 1
  Write-Output ''
  Write-Output '-- Dependency check --'
  if ($pyCmd) {
    Write-Output "  [OK]      python (required: stage-gate and PRD lint scripts): $($pyCmd.Source)"
  } else {
    Write-Output '  [MISSING] python (required): check-stage-gate.py / lint-prd.py will not run'
    Write-Output '            Install: winget install Python.Python.3 or https://www.python.org/downloads/'
  }
  if ($nodeCmd) {
    Write-Output '  [OK]      node/npx (optional: Feishu publish only)'
  } else {
    Write-Output '  [MISSING] node/npx (optional: Feishu publish only; does not affect this install)'
  }
}

if (-not $Unlink) {
  @'

-- Feishu publish (optional) --
To publish PRDs to Feishu cloud docs:
  1) Install Feishu CLI:  npx @larksuite/cli@latest install
  2) (recommended) peer:  npx skills add larksuite/cli -y -g
  3) Run setup in the target project to bind and authorize Feishu
'@
}
