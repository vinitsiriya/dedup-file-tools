# Manual Test Scenario: Simple Deduplication (dedup_file_tools_dupes_move)
# To run: pwsh manual_tests/dedup_file_tools_dupes_move/simple_scenario/simple_manual_test.ps1

$ErrorActionPreference = 'Stop'

# Set up workspace
$workspace = ".temp/manual_tests/dedup_file_tools_dupes_move/simple_scenario"
if (Test-Path $workspace) { Remove-Item -Recurse -Force $workspace }
New-Item -ItemType Directory -Path $workspace | Out-Null

# Create dummy data and dupes folders
$data = "$workspace/data"
$dupes = "$workspace/dupes"
New-Item -ItemType Directory -Path $data | Out-Null
New-Item -ItemType Directory -Path $dupes | Out-Null

# Generate test files in data using the dedicated fixture generator script
python manual_tests/dedup_file_tools_dupes_move/generate_fixtures_manual.py --src $data

$venvPython = if (Test-Path ".\venv\Scripts\python.exe") { ".\venv\Scripts\python.exe" } else { "python" }

# Initialize job directory
& $venvPython dedup_file_tools_dupes_move/main.py init --job-dir $workspace/job --job-name testjob

# Analyze for duplicates
& $venvPython dedup_file_tools_dupes_move/main.py analyze --job-dir $workspace/job --job-name testjob --lookup-pool $data --threads 4

# Preview planned moves
& $venvPython dedup_file_tools_dupes_move/main.py preview-summary --job-dir $workspace/job --job-name testjob

# Move duplicates
& $venvPython dedup_file_tools_dupes_move/main.py move --job-dir $workspace/job --job-name testjob --lookup-pool $data --dupes-folder $dupes --threads 4

# Verify moves
& $venvPython dedup_file_tools_dupes_move/main.py verify --job-dir $workspace/job --job-name testjob --lookup-pool $data --dupes-folder $dupes --threads 4

# Print summary
& $venvPython dedup_file_tools_dupes_move/main.py summary --job-dir $workspace/job --job-name testjob

# (Optional) Import checksums from another job (simulate by copying the job DB)
$importJob = "$workspace/importjob"
New-Item -ItemType Directory -Path $importJob | Out-Null
if (Test-Path "$workspace/job/testjob.db") {
    Copy-Item "$workspace/job/testjob.db" "$importJob/importjob.db"
    & $venvPython dedup_file_tools_dupes_move/main.py import-checksums --job-dir $workspace/job --job-name testjob --other-db $importJob/importjob.db
} else {
    Write-Host "WARNING: testjob.db not found, skipping import-checksums step."
}

Write-Host "Manual test completed. Check $dupes for moved files and $workspace/job for database/logs."
Write-Host "Review logs and summary for per-file and overall progress as required by protocol."