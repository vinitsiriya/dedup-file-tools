# archive_agents.ps1: Archive all agent .md files to a date-stamped backup directory and reset them
$timestamp = Get-Date -Format "yyyy-MM-dd-HHmm"
$backupDir = "agents/backup/$timestamp"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
Get-ChildItem agents -Filter *.md | ForEach-Object {
    Copy-Item $_.FullName $backupDir
    Set-Content $_.FullName "# $($_.Name)`n"
}
