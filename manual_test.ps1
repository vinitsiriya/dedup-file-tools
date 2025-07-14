#!/usr/bin/env pwsh
# manual_test.ps1
# Manual test script for fs-copy-tool CLI using .temp directory as workspace

$ErrorActionPreference = 'Stop'

# Clean up and set up .temp test workspace
if (Test-Path .temp/src) { Remove-Item -Recurse -Force .temp/src }
if (Test-Path .temp/dst) { Remove-Item -Recurse -Force .temp/dst }
if (Test-Path .temp/job) { Remove-Item -Recurse -Force .temp/job }
if (Test-Path .temp) { Remove-Item -Recurse -Force .temp }
New-Item -ItemType Directory -Path .temp | Out-Null

# Create dummy source and destination directories
$src = ".temp/src"
$dst = ".temp/dst"
New-Item -ItemType Directory -Path $src | Out-Null
New-Item -ItemType Directory -Path $dst | Out-Null

# Generate test files in source using fixture generator script
python scripts/generate_fixtures_manual.py --src $src

# Instead of 'fs-copy-tool', use the venv python and main.py directly
$venvPython = if (Test-Path ".\venv\Scripts\python.exe") { ".\venv\Scripts\python.exe" } else { "python" }

# Initialize job directory (protocol: always use a dedicated job dir)
& $venvPython fs_copy_tool/main.py init --job-dir .temp/job

# Instead of analyze, use add-source to incrementally add files to the job state
& $venvPython fs_copy_tool/main.py add-source --job-dir .temp/job --src $src

# Optionally, demonstrate add-file for a single file
$singleFile = Get-ChildItem $src -Recurse | Where-Object { -not $_.PSIsContainer } | Select-Object -First 1
if ($singleFile) {
    & $venvPython fs_copy_tool/main.py add-file --job-dir .temp/job --file $singleFile.FullName
}

# List files in the job state
& $venvPython fs_copy_tool/main.py list-files --job-dir .temp/job

# Remove a file from the job state (demonstrate remove-file)
if ($singleFile) {
    & $venvPython fs_copy_tool/main.py remove-file --job-dir .temp/job --file $singleFile.FullName
    & $venvPython fs_copy_tool/main.py list-files --job-dir .temp/job
}

# Analyze destination only (since source files are now added incrementally)
& $venvPython fs_copy_tool/main.py analyze --job-dir .temp/job --dst $dst

# Compute checksums for both source and destination (protocol: both tables)
& $venvPython fs_copy_tool/main.py checksum --job-dir .temp/job --table source_files --threads 2
& $venvPython fs_copy_tool/main.py checksum --job-dir .temp/job --table destination_files --threads 2

# Copy files (protocol: must use progress bars and threads)
& $venvPython fs_copy_tool/main.py copy --job-dir .temp/job --src $src --dst $dst --threads 2

# Simulate interruption: delete one file from destination
$deletedFile = Get-ChildItem $dst | Select-Object -First 1
if ($deletedFile) {
    Write-Host "Simulating interruption: deleting $($deletedFile.Name) from destination."
    Remove-Item $deletedFile.FullName
}

# Resume copy (should only re-copy the missing file)
& $venvPython fs_copy_tool/main.py copy --job-dir .temp/job --src $src --dst $dst --threads 2

# Show status and log (protocol: must check results)
& $venvPython fs_copy_tool/main.py status --job-dir .temp/job
& $venvPython fs_copy_tool/main.py log --job-dir .temp/job

# Run shallow and deep verification as separate phases
& $venvPython fs_copy_tool/main.py verify --job-dir .temp/job --src $src --dst $dst
& $venvPython fs_copy_tool/main.py deep-verify --job-dir .temp/job --src $src --dst $dst

# Print verification summary and full history using the new CLI commands
Write-Host "\nShallow verification status summary (latest for each file):"
& $venvPython fs_copy_tool/main.py verify-status-summary --job-dir .temp/job
Write-Host "\nShallow verification status full (all history):"
& $venvPython fs_copy_tool/main.py verify-status-full --job-dir .temp/job
Write-Host "\nDeep verification status summary (latest for each file):"
& $venvPython fs_copy_tool/main.py deep-verify-status-summary --job-dir .temp/job
Write-Host "\nDeep verification status full (all history):"
& $venvPython fs_copy_tool/main.py deep-verify-status-full --job-dir .temp/job

Write-Host "Manual test completed. Check .temp/dst for copied files and .temp/job for database/logs."
Write-Host "Review logs for per-file and overall progress bar output as required by protocol."
