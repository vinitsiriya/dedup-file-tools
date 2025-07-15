# archive_agents.ps1: Archive all workflow proposal and user story .md files to a date-stamped archive directory with confirmation
$timestamp = Get-Date -Format "yyyy-MM-dd-HHmm"
$archiveDir = "agents/workflow/archived/$timestamp"


# Gather all .md files in proposal and user-story (recursively)
$proposalFiles = @(Get-ChildItem -Path "agents/workflow/proposal" -Filter *.md -Recurse -File)
$userStoryFiles = @(Get-ChildItem -Path "agents/workflow/user-story" -Filter *.md -Recurse -File)
$allFiles = @($proposalFiles + $userStoryFiles)

if ($allFiles.Count -eq 0) {
    Write-Host "No proposal or user story .md files found to archive."
    exit 0
}

Write-Host "The following files will be moved to ${archiveDir}:" -ForegroundColor Yellow
$allFiles | ForEach-Object { Write-Host $_.FullName }

$confirmation = Read-Host "Proceed with archival? (y/n)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "Archival cancelled."
    exit 1
}

New-Item -ItemType Directory -Force -Path $archiveDir | Out-Null
foreach ($file in $allFiles) {
    $dest = Join-Path $archiveDir ($file.FullName -replace '^.*agents\\workflow\\', '')
    $destDir = Split-Path $dest -Parent
    if (!(Test-Path $destDir)) { New-Item -ItemType Directory -Force -Path $destDir | Out-Null }
    Move-Item $file.FullName $dest
}

Write-Host "Archival complete. Files moved to ${archiveDir}." -ForegroundColor Green
