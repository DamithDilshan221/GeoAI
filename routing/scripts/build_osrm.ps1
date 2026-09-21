# routing/scripts/build_osrm.ps1
#
# Phase E -- osrm-extract + osrm-partition + osrm-customize (MLD pipeline)
#
# Reads routing/config/osrm_binaries.yaml for the install directory.
# Consumes data/routing/build/augmented.osm.pbf (or augmented.osm if no osmconvert).
# Writes OSRM routing files to data/routing/build/campus.osrm.*
#
# Usage:
#   cd <repo root>
#   .\routing\scripts\build_osrm.ps1
#   .\routing\scripts\build_osrm.ps1 -InputFile data/routing/build/additions.osm
#   .\routing\scripts\build_osrm.ps1 -Force   # re-extract even if .osrm exists

param(
    [string]$InputFile = "",
    [switch]$Force
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

# Executables
$osrmExtract   = Join-Path $binDir "osrm-extract.exe"
$osrmPartition = Join-Path $binDir "osrm-partition.exe"
$osrmCustomize = Join-Path $binDir "osrm-customize.exe"
$footLua       = Join-Path $binDir "profiles/foot.lua"

foreach ($exe in @($osrmExtract, $osrmPartition, $osrmCustomize, $footLua)) {
    if (-not (Test-Path $exe)) {
        Write-Error "Required file not found: $exe -- run fetch_osrm_binaries.ps1 first"
        exit 1
    }
}

# Input: prefer augmented PBF, fallback to augmented OSM, then additions.osm
$buildDir = "data/routing/build"
if ($InputFile) {
    $input = $InputFile
} elseif (Test-Path "$buildDir/augmented.osm.pbf") {
    $input = "$buildDir/augmented.osm.pbf"
} elseif (Test-Path "$buildDir/augmented.osm") {
    $input = "$buildDir/augmented.osm"
} elseif (Test-Path "$buildDir/additions.osm") {
    Write-Warning "augmented.osm[.pbf] not found -- extracting from additions.osm only (campus paths ONLY, no base OSM roads)"
    $input = "$buildDir/additions.osm"
} else {
    Write-Error "No input file found. Run build_network.py first."
    exit 1
}

$osrmBase = "$buildDir/campus.osrm"

Write-Host ""
Write-Host "=== OSRM Build Pipeline (Phase E) ===" -ForegroundColor Cyan
Write-Host "  Input   : $input"
Write-Host "  Profile : $footLua"
Write-Host "  Output  : $osrmBase.*"
Write-Host "  Binaries: $binDir"
Write-Host ""

# ── E1: osrm-extract ─────────────────────────────────────────────────────────
if ((Test-Path "$osrmBase.edges") -and -not $Force) {
    Write-Host "osrm-extract already done (use -Force to re-extract)"
} else {
    Write-Host "Running osrm-extract..." -ForegroundColor Yellow
    $t = [System.Diagnostics.Stopwatch]::StartNew()
    & $osrmExtract -p $footLua $input --output $osrmBase 2>&1
    if ($LASTEXITCODE -ne 0) { Write-Error "osrm-extract failed with exit code $LASTEXITCODE"; exit 1 }
    $t.Stop()
    Write-Host "  osrm-extract: $($t.Elapsed.TotalSeconds.ToString('F1'))s" -ForegroundColor Green
}

# ── E2: osrm-partition ────────────────────────────────────────────────────────
if ((Test-Path "$osrmBase.partition") -and -not $Force) {
    Write-Host "osrm-partition already done (use -Force to re-run)"
} else {
    Write-Host "Running osrm-partition..." -ForegroundColor Yellow
    $t = [System.Diagnostics.Stopwatch]::StartNew()
    & $osrmPartition $osrmBase 2>&1
    if ($LASTEXITCODE -ne 0) { Write-Error "osrm-partition failed with exit code $LASTEXITCODE"; exit 1 }
    $t.Stop()
    Write-Host "  osrm-partition: $($t.Elapsed.TotalSeconds.ToString('F1'))s" -ForegroundColor Green
}

# ── E3: osrm-customize ───────────────────────────────────────────────────────
if ((Test-Path "$osrmBase.mldgr") -and -not $Force) {
    Write-Host "osrm-customize already done (use -Force to re-run)"
} else {
    Write-Host "Running osrm-customize..." -ForegroundColor Yellow
    $t = [System.Diagnostics.Stopwatch]::StartNew()
    & $osrmCustomize $osrmBase 2>&1
    if ($LASTEXITCODE -ne 0) { Write-Error "osrm-customize failed with exit code $LASTEXITCODE"; exit 1 }
    $t.Stop()
    Write-Host "  osrm-customize: $($t.Elapsed.TotalSeconds.ToString('F1'))s" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== OSRM Build complete ===" -ForegroundColor Cyan
Write-Host "Run start_osrm.ps1 to launch osrm-routed and verify routing."
Write-Host "campus.osrm.* files: $(Get-ChildItem $buildDir -Filter 'campus.osrm*' | Measure-Object | Select-Object -ExpandProperty Count) files"
