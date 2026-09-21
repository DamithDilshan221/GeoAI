# routing/scripts/fetch_osrm_binaries.ps1
#
# Phase B2 — Download, sha256-verify, and extract the pinned OSRM native binaries.
# Also fetches profiles/foot.lua from the matching upstream Project-OSRM/osrm-backend tag.
#
# Reads routing/config/osrm_binaries.yaml for version, platform, and URLs.
# Writes routing/bin/<install_dir>/ (gitignored).
#
# Usage:
#   cd <repo root>
#   .\routing\scripts\fetch_osrm_binaries.ps1
#   .\routing\scripts\fetch_osrm_binaries.ps1 -Force   # re-download even if already present

param(
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ── Load config ───────────────────────────────────────────────────────────────
$configPath = "routing/config/osrm_binaries.yaml"
if (-not (Test-Path $configPath)) {
    Write-Error "Config not found: $configPath"
    exit 1
}

# Simple YAML key: value parser (no external dependency)
$cfg = @{}
Get-Content $configPath | ForEach-Object {
    if ($_ -match '^\s*([^#:][^:]*?)\s*:\s*"?([^"#]+?)"?\s*$') {
        $cfg[$Matches[1].Trim()] = $Matches[2].Trim()
    }
}

$version    = $cfg["osrm_version"]          # e.g. v26.9.0
$platform   = $cfg["platform"]              # e.g. win32-x64
$versionNoV = $version.TrimStart('v')       # e.g. 26.9.0
$provider   = $cfg["provider"]              # e-kotov/osrm-binaries

# Resolve templates
$archiveName      = "osrm-$version-$platform-Release.tar.gz"   # keeps the v-prefix: osrm-v26.9.0-win32-x64-Release.tar.gz
$archiveUrl       = "https://github.com/e-kotov/osrm-binaries/releases/download/$version/$archiveName"
$checksumsUrl     = "https://github.com/e-kotov/osrm-binaries/releases/download/$version/checksums.txt"
$footLuaUrl       = "https://raw.githubusercontent.com/Project-OSRM/osrm-backend/$version/profiles/foot.lua"
$installDir       = "routing/bin/osrm-$version-$platform"

Write-Host ""
Write-Host "=== OSRM Binary Fetcher (Phase B2) ===" -ForegroundColor Cyan
Write-Host "  Version  : $version"
Write-Host "  Platform : $platform"
Write-Host "  Provider : $provider (THIRD-PARTY -- see osrm_binaries.yaml)"
Write-Host "  Archive  : $archiveName"
Write-Host "  InstDir  : $installDir"
Write-Host ""

# ── Create directories ────────────────────────────────────────────────────────
$tempDir   = "data/routing/raw"
$binDir    = $installDir
New-Item -ItemType Directory -Force -Path $tempDir, $binDir | Out-Null

$archivePath = Join-Path $tempDir $archiveName

# ── Download archive (skip if already present and --Force not set) ─────────────
if ((Test-Path $archivePath) -and -not $Force) {
    Write-Host "Archive already downloaded: $archivePath (use -Force to re-download)"
} else {
    Write-Host "Downloading archive from $archiveUrl ..."
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $archiveUrl -OutFile $archivePath -UseBasicParsing
    Write-Host "  Downloaded: $([math]::Round((Get-Item $archivePath).Length / 1MB, 2)) MB"
}

# ── Download checksums file ───────────────────────────────────────────────────
$checksumsPath = Join-Path $tempDir "osrm-$version-checksums.txt"
Write-Host "Downloading checksums from $checksumsUrl ..."
$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest -Uri $checksumsUrl -OutFile $checksumsPath -UseBasicParsing
Write-Host "  Checksums file downloaded."

# ── Verify sha256 ─────────────────────────────────────────────────────────────
Write-Host "Computing sha256 of $archiveName ..."
$actualHash = (Get-FileHash -Path $archivePath -Algorithm SHA256).Hash.ToLower()
Write-Host "  Actual  sha256: $actualHash"

# Parse checksums.txt — format: "<hash>  <filename>" or "<hash> *<filename>"
$expectedHash = $null
Get-Content $checksumsPath | ForEach-Object {
    if ($_ -match "^([0-9a-f]{64})\s+\*?$archiveName\s*$") {
        $expectedHash = $Matches[1].ToLower()
    }
}

if ($null -eq $expectedHash) {
    Write-Error "Could not find checksum for '$archiveName' in checksums.txt"
    exit 1
}

Write-Host "  Expected sha256: $expectedHash"

if ($actualHash -ne $expectedHash) {
    Write-Error "SHA256 MISMATCH for $archiveName! Aborting."
    exit 1
}

Write-Host "  SHA256 VERIFIED OK" -ForegroundColor Green

# ── Extract archive ────────────────────────────────────────────────────────────
Write-Host "Extracting to $binDir ..."
tar -xzf $archivePath -C $binDir --strip-components=0 2>&1
Write-Host "  Extraction complete."

# List extracted executables
$exes = Get-ChildItem $binDir -Filter "*.exe" -Recurse
Write-Host "  Executables found:"
$exes | ForEach-Object { Write-Host "    $($_.Name)  ($([math]::Round($_.Length/1KB,1)) KB)" }

# ── Download foot.lua from upstream Project-OSRM/osrm-backend ─────────────────
$footLuaPath = Join-Path $binDir "profiles/foot.lua"
New-Item -ItemType Directory -Force -Path (Split-Path $footLuaPath) | Out-Null

Write-Host ""
Write-Host "Fetching foot.lua from upstream Project-OSRM/osrm-backend $version ..."
Write-Host "  URL: $footLuaUrl"
Invoke-WebRequest -Uri $footLuaUrl -OutFile $footLuaPath -UseBasicParsing
$footLuaHash = (Get-FileHash -Path $footLuaPath -Algorithm SHA256).Hash.ToLower()
$footLuaSize = (Get-Item $footLuaPath).Length
Write-Host "  Downloaded: $footLuaSize bytes, sha256: $footLuaHash"
Write-Host "  Note: fetched from official Project-OSRM/osrm-backend, NOT from the third-party binary archive"

# ── Write manifest entry ───────────────────────────────────────────────────────
$manifest = [ordered]@{
    osrm_version         = $version
    platform             = $platform
    provider             = "$provider (THIRD-PARTY -- NOT official OSRM release channel)"
    archive_name         = $archiveName
    archive_url          = $archiveUrl
    archive_sha256       = $actualHash
    checksums_url        = $checksumsUrl
    foot_lua_url         = $footLuaUrl
    foot_lua_sha256      = $footLuaHash
    foot_lua_size_bytes  = $footLuaSize
    install_dir          = $binDir
    fetched_at           = (Get-Date -Format "o")
}
$manifestPath = Join-Path $binDir "fetch_manifest.json"
$manifest | ConvertTo-Json | Set-Content $manifestPath
Write-Host ""
Write-Host "Manifest written to: $manifestPath" -ForegroundColor Green
Write-Host ""
Write-Host "=== Phase B2 complete ===" -ForegroundColor Cyan
Write-Host "Binaries in: $binDir"
Write-Host "foot.lua at: $footLuaPath"
