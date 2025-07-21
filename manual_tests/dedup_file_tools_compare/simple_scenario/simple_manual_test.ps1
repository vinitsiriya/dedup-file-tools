# Manual Test Script: Simple Directory Compare (dedup_file_tools_compare)
# This script is self-contained and uses .temp/manual_tests/dedup_file_tools_compare/simple_scenario as its workspace.
#
# To run: pwsh manual_tests/dedup_file_tools_compare/simple_scenario/simple_manual_test.ps1
#
# This script exercises the full compare workflow: fixture generation, init, add-to-left, add-to-right, find-missing-files, show-result.
#
# All results and logs are in .temp/manual_tests/dedup_file_tools_compare/simple_scenario/job
#
# Review the output and .temp/manual_tests/dedup_file_tools_compare/simple_scenario/job for results.

$ErrorActionPreference = 'Stop'

# Set up workspace
$workspace = ".temp/manual_tests/dedup_file_tools_compare/simple_scenario"
if (Test-Path $workspace) { Remove-Item -Recurse -Force $workspace }
New-Item -ItemType Directory -Path $workspace | Out-Null

# Create left and right directories
$left = "$workspace/left"
$right = "$workspace/right"
$job = "$workspace/job"
New-Item -ItemType Directory -Path $left | Out-Null
New-Item -ItemType Directory -Path $right | Out-Null
New-Item -ItemType Directory -Path $job | Out-Null

# Generate test files in left and right using fixture generator script
python manual_tests/dedup_file_tools_compare/simple_scenario/generate_fixtures_manual.py --left $left --right $right

# Show files before compare
Write-Host "`n=== Left before compare ==="
Get-ChildItem -Path $left -Recurse | Select-Object FullName
Write-Host "`n=== Right before compare ==="
Get-ChildItem -Path $right -Recurse | Select-Object FullName

# Setup Python from .venv
$venvPython = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "ERROR: .\.venv\Scripts\python.exe not found. Please create a virtual environment in .\.venv and install your package with 'pip install -e .'"
    exit 1
}

# Compare workflow
$cmd = "$venvPython -m dedup_file_tools_compare.main init --job-dir $job --job-name testjob"
Write-Host "`n>>> Running: $cmd"
Invoke-Expression $cmd

$cmd = "$venvPython -m dedup_file_tools_compare.main add-to-left --job-dir $job --job-name testjob --dir $left"
Write-Host "`n>>> Running: $cmd"
Invoke-Expression $cmd

$cmd = "$venvPython -m dedup_file_tools_compare.main add-to-right --job-dir $job --job-name testjob --dir $right"
Write-Host "`n>>> Running: $cmd"
Invoke-Expression $cmd

$cmd = "$venvPython -m dedup_file_tools_compare.main find-missing-files --job-dir $job --job-name testjob"
Write-Host "`n>>> Running: $cmd"
Invoke-Expression $cmd


# Show results and write to CSV (full report, not summary)
$reportsDir = "$job/reports"
if (-not (Test-Path $reportsDir)) { New-Item -ItemType Directory -Path $reportsDir | Out-Null }
$cmd = "$venvPython -m dedup_file_tools_compare.main show-result --job-dir $job --job-name testjob"
Write-Host "`n>>> Running: $cmd"
Invoke-Expression $cmd

# Find the latest compare_summary_*.csv in reports dir
$csvFiles = Get-ChildItem -Path $reportsDir -Filter 'comparison_report_*.csv' | Sort-Object LastWriteTime -Descending
if ($csvFiles.Count -gt 0) {
    $csvPath = $csvFiles[0].FullName
    Write-Host "`n=== Compare Summary CSV ==="
    Get-Content $csvPath
} else {
    Write-Host "No comparison_report_*.csv found in $reportsDir"
}

Write-Host "`nManual test completed. Check $job for database/logs/results."
