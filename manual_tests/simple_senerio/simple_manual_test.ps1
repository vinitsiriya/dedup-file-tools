# Manual Test Scenario: Simple Deduplication
# This script is self-contained and uses .temp/manual_tests/simple_senerio as its workspace.
#
# To run: pwsh manual_tests/simple_senerio/simple_manual_test.ps1
#
# This script exercises the full workflow: fixture generation, add-source, add-file, remove-file, checksum, copy, resume, status, log, verify, and deep-verify.
#
# - Source and destination directories are created under .temp/manual_tests/simple_senerio
# - Duplicate files in different directories are included for deduplication testing
# - All results and logs are in .temp/manual_tests/simple_senerio/job
#
# Review the output and .temp/manual_tests/simple_senerio/dst for results.
#
# To add more scenarios, copy and adapt this script in the manual_tests/ directory.

$ErrorActionPreference = 'Stop'

# Set up .temp/manual_tests/simple_senerio as workspace
$workspace = ".temp/manual_tests/simple_senerio"
if (Test-Path $workspace) { Remove-Item -Recurse -Force $workspace }
New-Item -ItemType Directory -Path $workspace | Out-Null

# Create dummy source and destination directories
$src = "$workspace/src"
$dst = "$workspace/dst"
New-Item -ItemType Directory -Path $src | Out-Null
New-Item -ItemType Directory -Path $dst | Out-Null

# Generate test files in source using fixture generator script
python scripts/generate_fixtures_manual.py --src $src

$venvPython = if (Test-Path ".\venv\Scripts\python.exe") { ".\venv\Scripts\python.exe" } else { "python" }

# Initialize job directory (protocol: always use a dedicated job dir)
& $venvPython fs_copy_tool/main.py init --job-dir $workspace/job

# Instead of analyze, use add-source to incrementally add files to the job state
& $venvPython fs_copy_tool/main.py add-source --job-dir $workspace/job --src $src

# Optionally, demonstrate add-file for a single file
$singleFile = Get-ChildItem $src -Recurse | Where-Object { -not $_.PSIsContainer } | Select-Object -First 1
if ($singleFile) {
    & $venvPython fs_copy_tool/main.py add-file --job-dir $workspace/job --file $singleFile.FullName
}

# List files in the job state
& $venvPython fs_copy_tool/main.py list-files --job-dir $workspace/job

# Remove a file from the job state (demonstrate remove-file)
if ($singleFile) {
    & $venvPython fs_copy_tool/main.py remove-file --job-dir $workspace/job --file $singleFile.FullName
    & $venvPython fs_copy_tool/main.py list-files --job-dir $workspace/job
}

# Analyze destination only (since source files are now added incrementally)
& $venvPython fs_copy_tool/main.py analyze --job-dir $workspace/job --dst $dst

# Compute checksums for both source and destination (protocol: both tables)
& $venvPython fs_copy_tool/main.py checksum --job-dir $workspace/job --table source_files --threads 2
& $venvPython fs_copy_tool/main.py checksum --job-dir $workspace/job --table destination_files --threads 2

# Copy files (protocol: must use progress bars and threads)
& $venvPython fs_copy_tool/main.py copy --job-dir $workspace/job --src $src --dst $dst --threads 2

# Simulate interruption: delete one file from destination
$deletedFile = Get-ChildItem $dst | Select-Object -First 1
if ($deletedFile) {
    Write-Host "Simulating interruption: deleting $($deletedFile.Name) from destination."
    Remove-Item $deletedFile.FullName
}

# Resume copy (should only re-copy the missing file)
& $venvPython fs_copy_tool/main.py copy --job-dir $workspace/job --src $src --dst $dst --threads 2

# Show status and log (protocol: must check results)
& $venvPython fs_copy_tool/main.py status --job-dir $workspace/job
& $venvPython fs_copy_tool/main.py log --job-dir $workspace/job

# Run shallow and deep verification as separate phases
& $venvPython fs_copy_tool/main.py verify --job-dir $workspace/job --src $src --dst $dst
& $venvPython fs_copy_tool/main.py deep-verify --job-dir $workspace/job --src $src --dst $dst

# Print verification summary and full history using the new CLI commands
Write-Host "\nShallow verification status summary (latest for each file):"
& $venvPython fs_copy_tool/main.py verify-status-summary --job-dir $workspace/job
Write-Host "\nShallow verification status full (all history):"
& $venvPython fs_copy_tool/main.py verify-status-full --job-dir $workspace/job
Write-Host "\nDeep verification status summary (latest for each file):"
& $venvPython fs_copy_tool/main.py deep-verify-status-summary --job-dir $workspace/job
Write-Host "\nDeep verification status full (all history):"
& $venvPython fs_copy_tool/main.py deep-verify-status-full --job-dir $workspace/job

Write-Host "Manual test completed. Check $dst for copied files and $workspace/job for database/logs."
Write-Host "Review logs for per-file and overall progress bar output as required by protocol."
