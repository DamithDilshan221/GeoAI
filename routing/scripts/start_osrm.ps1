# routing/scripts/start_osrm.ps1
#
# Phase F -- Launch osrm-routed (MLD algorithm) on the campus OSRM files.
# Writes its PID to data/routing/build/osrm-routed.pid.
# This is a FOREGROUND process -- run in a dedicated terminal tab.
#
# Usage:
#   cd <repo root>
#   .\routing\scripts\start_osrm.ps1
#   .\routing\scripts\start_osrm.ps1 -Port 5001

param(
    [int]$Port    = 5001,
    [int]$Threads = 4,
    [string]$Algorithm = "MLD"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ── Resolve paths ─────────────────────────────────────────────────────────────
$configPath = "routing/config/osrm_binaries.yaml"
$cfg = @{}
Get-Content $configPath | ForEach-Object {
    if ($_ -match '^\s*([^#:][^:]*?)\s*:\s*"?([^"#]+?)"?\s*$') {
        $cfg[$Matches[1].Trim()] = $Matches[2].Trim()
    }
}
$version  = $cfg["osrm_version"]
$platform = $cfg["platform"]
$binDir   = "routing/bin/osrm-$version-$platform"
$osrmRoutedExe = Join-Path $binDir "osrm-routed.exe"

$osrmBase = "data/routing/build/campus.osrm"
$pidFile  = "data/routing/build/osrm-routed.pid"

if (-not (Test-Path $osrmRoutedExe)) {
    Write-Error "osrm-routed.exe not found at $osrmRoutedExe -- run fetch_osrm_binaries.ps1"
    exit 1
}
if (-not (Test-Path "$osrmBase.mldgr")) {
    Write-Error "$osrmBase.mldgr not found -- run build_osrm.ps1 first"
    exit 1
}

Write-Host ""
Write-Host "=== Starting osrm-routed (Phase F) ===" -ForegroundColor Cyan
Write-Host "  Binary   : $osrmRoutedExe"
Write-Host "  Data     : $osrmBase"
Write-Host "  Port     : $Port"
Write-Host "  Algorithm: $Algorithm"
Write-Host "  Threads  : $Threads"
Write-Host ""
Write-Host "osrm-routed will run in the FOREGROUND of this terminal."
Write-Host "Use Ctrl+C to stop it. The .env variable OSRM_BASE_URL should be"
Write-Host "set to http://localhost:$Port (backend) and the frontend constant"
Write-Host "updated to http://localhost:$Port during testing."
Write-Host ""

# Run osrm-routed
& $osrmRoutedExe $osrmBase `
    --algorithm $Algorithm `
    --port $Port `
    -t $Threads `
    --max-viaroute-size 5000 `
    --max-table-size 100 `
    --max-matching-size 100 2>&1
