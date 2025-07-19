# Manual Test Script: Partial Destination Prepopulation
#
# This script tests the scenario where the destination already contains some files from the source, and a new job is scheduled.
# Workspace: .temp/manual_tests/partial_dst_prepop
#
# Steps:
# 1. Set up workspace and create source/destination directories.
# 2. Populate source with fileA, fileB, fileC, fileD.
# 3. Populate destination with fileA, fileC.
# 4. Schedule a new job and add source.
# 5. Run the workflow: init, add-source, checksum, copy, status, verify.
# 6. Observe which files are copied/skipped and check logs.

$ErrorActionPreference = 'Stop'

# Set up workspace
$workspace = ".temp/manual_tests/partial_dst_prepop"
if (Test-Path $workspace) { Remove-Item -Recurse -Force $workspace }
New-Item -ItemType Directory -Path $workspace | Out-Null

# Create source and destination directories
$src = "$workspace/src"
$dst = "$workspace/dst"
New-Item -ItemType Directory -Path $src | Out-Null
New-Item -ItemType Directory -Path $dst | Out-Null

# Create files in source
Set-Content -Path "$src/fileA.txt" -Value "This is file A"
Set-Content -Path "$src/fileB.txt" -Value "This is file B"
Set-Content -Path "$src/fileC.txt" -Value "This is file C"
Set-Content -Path "$src/fileD.txt" -Value "This is file D"

# Prepopulate destination with fileA and fileC
Copy-Item "$src/fileA.txt" "$dst/fileA.txt"
Copy-Item "$src/fileC.txt" "$dst/fileC.txt"

$venvPython = if (Test-Path ".\venv\Scripts\python.exe") { ".\venv\Scripts\python.exe" } else { "python" }

# Initialize job directory
& $venvPython fs_copy_tool/main.py init --job-dir $workspace/job

# Add source to job
& $venvPython fs_copy_tool/main.py add-source --job-dir $workspace/job --src $src

# Run checksum phase for both source and destination tables
& $venvPython fs_copy_tool/main.py checksum --job-dir $workspace/job --table source_files
& $venvPython fs_copy_tool/main.py checksum --job-dir $workspace/job --table destination_files

# Run copy phase
& $venvPython fs_copy_tool/main.py copy --job-dir $workspace/job --dst $dst

# Check status
& $venvPython fs_copy_tool/main.py status --job-dir $workspace/job

# Verify results
& $venvPython fs_copy_tool/main.py verify --job-dir $workspace/job --dst $dst

Write-Host "Manual test complete. Check $dst and job logs for results."
