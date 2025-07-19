
# Manual Test Script: Simple Deduplication (dedup_file_tools_dupes_move)
# This script is self-contained and uses .temp/manual_tests/dedup_file_tools_dupes_move/simple_scenario as its workspace.
#
# To run: pwsh manual_tests/dedup_file_tools_dupes_move/simple_scenario/simple_manual_test.ps1
#
# This script exercises the full deduplication workflow: fixture generation, init, analyze, move, verify, summary.
#
# All results and logs are in .temp/manual_tests/dedup_file_tools_dupes_move/simple_scenario/job
#
# Review the output and .temp/manual_tests/dedup_file_tools_dupes_move/simple_scenario/dupes for results.

$ErrorActionPreference = 'Stop'

# Set up workspace
$workspace = ".temp/manual_tests/dedup_file_tools_dupes_move/simple_scenario"
if (Test-Path $workspace) { Remove-Item -Recurse -Force $workspace }
New-Item -ItemType Directory -Path $workspace | Out-Null

# Create pool and dupes directories
$pool = "$workspace/pool"
$dupes = "$workspace/dupes"
$job = "$workspace/job"
New-Item -ItemType Directory -Path $pool | Out-Null
New-Item -ItemType Directory -Path $dupes | Out-Null
New-Item -ItemType Directory -Path $job | Out-Null

# Generate test files in pool using fixture generator script
python manual_tests/dedup_file_tools_dupes_move/generate_fixtures_manual.py --pool $pool

# Show files before move
Write-Host "`n=== Pool before move ==="
Get-ChildItem -Path $pool -Recurse | Select-Object FullName

# Setup Python from .venv
$venvPython = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "ERROR: .\.venv\Scripts\python.exe not found. Please create a virtual environment in .\.venv and install your package with 'pip install -e .'"
    exit 1
}

# Deduplication workflow
$cmd = "$venvPython -m dedup_file_tools_dupes_move.main init --job-dir $job --job-name testjob"
Write-Host "`n>>> Running: $cmd"
Invoke-Expression $cmd

$cmd = "$venvPython -m dedup_file_tools_dupes_move.main analyze --job-dir $job --job-name testjob --lookup-pool $pool"
Write-Host "`n>>> Running: $cmd"
Invoke-Expression $cmd

$cmd = "$venvPython -m dedup_file_tools_dupes_move.main move --job-dir $job --job-name testjob --dupes-folder $dupes"
Write-Host "`n>>> Running: $cmd"
Invoke-Expression $cmd

$cmd = "$venvPython -m dedup_file_tools_dupes_move.main verify --job-dir $job --job-name testjob --lookup-pool $pool --dupes-folder $dupes"
Write-Host "`n>>> Running: $cmd"
Invoke-Expression $cmd

$cmd = "$venvPython -m dedup_file_tools_dupes_move.main summary --job-dir $job --job-name testjob"
Write-Host "`n>>> Running: $cmd"
Invoke-Expression $cmd

# Show files after move
Write-Host "`n=== Pool after move ==="
Get-ChildItem -Path $pool -Recurse | Select-Object FullName
Write-Host "`n=== Dupes after move ==="
Get-ChildItem -Path $dupes -Recurse | Select-Object FullName

# Show summary CSV
Write-Host "`n=== Summary CSV ==="
if (Test-Path "$job/dedup_move_summary.csv") {
    Get-Content "$job/dedup_move_summary.csv"
} else {
    Write-Host "Summary CSV not found: $job/dedup_move_summary.csv"
}

Write-Host "`nManual test completed. Check $dupes for moved files and $job for database/logs."
