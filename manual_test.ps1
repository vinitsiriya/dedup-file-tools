#!/usr/bin/env pwsh
# manual_test.ps1
# Manual test script for fs-copy-tool CLI using .temp directory as workspace

$ErrorActionPreference = 'Stop'

# Clean up and set up .temp test workspace
if (Test-Path .temp) { Remove-Item -Recurse -Force .temp }
New-Item -ItemType Directory -Path .temp | Out-Null

# Create dummy source and destination directories
$src = ".temp/src"
$dst = ".temp/dst"
New-Item -ItemType Directory -Path $src | Out-Null
New-Item -ItemType Directory -Path $dst | Out-Null

# Create some test files in source
Set-Content -Path "$src/file1.txt" -Value "hello world"
Set-Content -Path "$src/file2.txt" -Value "another file"

# Initialize job directory
fs-copy-tool init --job-dir .temp/job

# Analyze source and destination
fs-copy-tool analyze --job-dir .temp/job --src $src --dst $dst

# Compute checksums
fs-copy-tool checksum --job-dir .temp/job --table source_files
fs-copy-tool checksum --job-dir .temp/job --table destination_files

# Copy files
fs-copy-tool copy --job-dir .temp/job --src $src --dst $dst

# Show status and log
fs-copy-tool status --job-dir .temp/job
fs-copy-tool log --job-dir .temp/job

Write-Host "Manual test completed. Check .temp/dst for copied files and .temp/job for database/logs."
