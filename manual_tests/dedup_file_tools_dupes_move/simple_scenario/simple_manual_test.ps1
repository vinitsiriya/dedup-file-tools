# Manual Test Scenario: Simple Deduplication (dedup_file_tools_dupes_move)
# To run: pwsh manual_tests/dedup_file_tools_dupes_move/simple_scenario/simple_manual_test.ps1

$dedupMain = "-m dedup_file_tools_dupes_move.main"
$commandSpacer = "`n====================`n"
$ErrorActionPreference = 'Stop'


# Set up .temp root and workspace
$tempRoot = ".temp"
if (-not (Test-Path $tempRoot)) { New-Item -ItemType Directory -Path $tempRoot | Out-Null }
$workspace = "$tempRoot/manual_tests/dedup_file_tools_dupes_move/simple_scenario"
if (Test-Path $workspace) { Remove-Item -Recurse -Force $workspace }
New-Item -ItemType Directory -Path $workspace | Out-Null

# Create dummy data and dupes folders under .temp
$data = "$workspace/data"
$dupes = "$workspace/dupes"
New-Item -ItemType Directory -Path $data | Out-Null
New-Item -ItemType Directory -Path $dupes | Out-Null

$tempRoot = Resolve-Path ".temp"
if (-not (Test-Path $tempRoot)) { New-Item -ItemType Directory -Path $tempRoot | Out-Null }
$workspace = Join-Path $tempRoot "manual_tests/dedup_file_tools_dupes_move/simple_scenario" | Resolve-Path -ErrorAction SilentlyContinue
if ($null -eq $workspace) {
    $workspace = Join-Path $tempRoot "manual_tests/dedup_file_tools_dupes_move/simple_scenario"
    if (Test-Path $workspace) { Remove-Item -Recurse -Force $workspace }
    New-Item -ItemType Directory -Path $workspace | Out-Null
    $workspace = Resolve-Path $workspace
}

# Create dummy data and dupes folders under .temp
$data = Join-Path $workspace "data"
$dupes = Join-Path $workspace "dupes"
if (-not (Test-Path $data)) { New-Item -ItemType Directory -Path $data | Out-Null }
if (-not (Test-Path $dupes)) { New-Item -ItemType Directory -Path $dupes | Out-Null }

# Generate test files in data using the dedicated fixture generator script
python manual_tests/dedup_file_tools_dupes_move/generate_fixtures_manual.py --src $data

python manual_tests/dedup_file_tools_dupes_move/generate_fixtures_manual.py --src $data

$venvPython = if (Test-Path ".\venv\Scripts\python.exe") { ".\venv\Scripts\python.exe" } else { "python" }

# Use absolute paths for all CLI arguments
$jobDir = Join-Path $workspace "job" | Resolve-Path -ErrorAction SilentlyContinue
if ($null -eq $jobDir) {
    $jobDir = Join-Path $workspace "job"
    if (Test-Path $jobDir) { Remove-Item -Recurse -Force $jobDir }
    New-Item -ItemType Directory -Path $jobDir | Out-Null
    $jobDir = Resolve-Path $jobDir
}


# Helper to print commands in green
function Write-Green($msg) { Write-Host $msg -ForegroundColor Green }

# Initialize job directory
Write-Host $commandSpacer
$cmd = "$venvPython $dedupMain init --job-dir $jobDir --job-name testjob"
Write-Green $cmd
Write-Host $commandSpacer
Invoke-Expression $cmd

# Analyze for duplicates
Write-Host $commandSpacer
$cmd = "$venvPython $dedupMain analyze --job-dir $jobDir --job-name testjob --lookup-pool $data --threads 4"
Write-Green $cmd
Write-Host $commandSpacer
Invoke-Expression $cmd

# Preview planned moves
Write-Host $commandSpacer
$cmd = "$venvPython $dedupMain preview-summary --job-dir $jobDir --job-name testjob"
Write-Green $cmd
Write-Host $commandSpacer
Invoke-Expression $cmd

# Initialize job directory
& $venvPython dedup_file_tools_dupes_move/main.py init --job-dir $workspace/job --job-name testjob

# Analyze for duplicates

# Analyze for duplicates
& $venvPython dedup_file_tools_dupes_move/main.py analyze --job-dir $workspace/job --job-name testjob --lookup-pool $data --threads 4

# Preview planned moves
& $venvPython dedup_file_tools_dupes_move/main.py preview-summary --job-dir $workspace/job --job-name testjob

# Print file listing and hashes BEFORE move
Write-Host "\n==== File listing and hashes in DATA directory (before move) ===="
Get-ChildItem -Path $data -File -Recurse | ForEach-Object {
    $hash = Get-FileHash $_.FullName -Algorithm SHA256
    Write-Host ("{0,-50} {1}" -f $_.FullName.Substring($data.Length+1), $hash.Hash)
}
Write-Host "\n==== File listing and hashes in DUPES directory (before move) ===="
Get-ChildItem -Path $dupes -File -Recurse | ForEach-Object {
    $hash = Get-FileHash $_.FullName -Algorithm SHA256
    Write-Host ("{0,-50} {1}" -f $_.FullName.Substring($dupes.Length+1), $hash.Hash)
}

# Move duplicates
& $venvPython dedup_file_tools_dupes_move/main.py move --job-dir $workspace/job --job-name testjob --lookup-pool $data --dupes-folder $dupes --threads 4

# Move duplicates
Write-Host $commandSpacer
$cmd = "$venvPython $dedupMain move --job-dir $jobDir --job-name testjob --lookup-pool $data --dupes-folder $dupes --threads 4"
Write-Green $cmd
Write-Host $commandSpacer
Invoke-Expression $cmd

# Verify moves
& $venvPython dedup_file_tools_dupes_move/main.py verify --job-dir $workspace/job --job-name testjob --lookup-pool $data --dupes-folder $dupes --threads 4

# Verify moves
Write-Host $commandSpacer
$cmd = "$venvPython $dedupMain verify --job-dir $jobDir --job-name testjob --lookup-pool $data --dupes-folder $dupes --threads 4"
Write-Green $cmd
Write-Host $commandSpacer
Invoke-Expression $cmd

# Print summary
& $venvPython dedup_file_tools_dupes_move/main.py summary --job-dir $workspace/job --job-name testjob

# Print summary
Write-Host $commandSpacer
$cmd = "$venvPython $dedupMain summary --job-dir $jobDir --job-name testjob"
Write-Green $cmd
Write-Host $commandSpacer
Invoke-Expression $cmd

# Print file listing and hashes AFTER move
Write-Host "\n==== File listing and hashes in DATA directory (after move) ===="
Get-ChildItem -Path $data -File -Recurse | ForEach-Object {
    $hash = Get-FileHash $_.FullName -Algorithm SHA256
    Write-Host ("{0,-50} {1}" -f $_.FullName.Substring($data.Length+1), $hash.Hash)
}
Write-Host "\n==== File listing and hashes in DUPES directory (after move) ===="
Get-ChildItem -Path $dupes -File -Recurse | ForEach-Object {
    $hash = Get-FileHash $_.FullName -Algorithm SHA256
    Write-Host ("{0,-50} {1}" -f $_.FullName.Substring($dupes.Length+1), $hash.Hash)
}

# (Optional) Import checksums from another job (simulate by copying the job DB)
$importJob = "$workspace/importjob"
New-Item -ItemType Directory -Path $importJob | Out-Null
if (Test-Path "$workspace/job/testjob.db") {
    Copy-Item "$workspace/job/testjob.db" "$importJob/importjob.db"
    & $venvPython dedup_file_tools_dupes_move/main.py import-checksums --job-dir $workspace/job --job-name testjob --other-db $importJob/importjob.db
} else {
    Write-Host "WARNING: testjob.db not found, skipping import-checksums step."
}
$importJob = Join-Path $workspace "importjob"
if (-not (Test-Path $importJob)) { New-Item -ItemType Directory -Path $importJob | Out-Null }
if (Test-Path (Join-Path $jobDir "testjob.db")) {
    Copy-Item (Join-Path $jobDir "testjob.db") (Join-Path $importJob "importjob.db")
    Write-Host $commandSpacer
    $cmd = "$venvPython $dedupMain import-checksums --job-dir $jobDir --job-name testjob --other-db " + (Join-Path $importJob "importjob.db")
    Write-Green $cmd
    Write-Host $commandSpacer
    Invoke-Expression $cmd
} else {
    Write-Host "WARNING: testjob.db not found, skipping import-checksums step."
}

Write-Host "\n==== File listing and hashes in DATA directory ===="
Get-ChildItem -Path $data -File -Recurse | ForEach-Object {
    $hash = Get-FileHash $_.FullName -Algorithm SHA256
    Write-Host ("{0,-50} {1}" -f $_.FullName.Substring($data.Length+1), $hash.Hash)
}
Write-Host "\n==== File listing and hashes in DUPES directory ===="
Get-ChildItem -Path $dupes -File -Recurse | ForEach-Object {
    $hash = Get-FileHash $_.FullName -Algorithm SHA256
    Write-Host ("{0,-50} {1}" -f $_.FullName.Substring($dupes.Length+1), $hash.Hash)
}

Write-Host "\nManual test completed. Check $dupes for moved files and $workspace/job for database/logs."
Write-Host "Review logs and summary for per-file and overall progress as required by protocol."