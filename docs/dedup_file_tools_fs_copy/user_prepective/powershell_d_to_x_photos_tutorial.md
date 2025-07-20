# Tutorial: Copy D:\photos to X:\AllPhotos\more\ws2-pc-data\d_photos with dedup-file-copy-fs

This tutorial demonstrates a streamlined workflow for copying a photo collection from `D:\photos` to `X:\AllPhotos\more\ws2-pc-data\d_photos` using `dedup-file-copy-fs`, with optional checksum import for faster deduplication.

## Prerequisites
- `dedup-file-copy-fs` installed (see main README for pipx instructions)
- Source directory: `D:\photos`
- Destination directory: `X:\AllPhotos\more\ws2-pc-data\d_photos`
- Destination index pool: `X:` (root of X: drive)
- Optional: Existing checksum cache database for import

## Variables
```powershell
$env:LOG_LEVEL = "WARNING"
$JobDir = ".\copy_job_D_to_X_d_photos"
$JobName = "D_to_X_d_photos"
$SrcDir = "D:\photos"
$DstDir = "X:\AllPhotos\more\ws2-pc-data\d_photos"
$DstIndexPool = "X:"  # Set to the root of X: as the index pool
```

## PowerShell Script Example
```powershell
function Run-Step {
    param (
        [string]$Command,
        [string]$StepName
    )
    Write-Host "Running: $StepName"
    Write-Host "Command: $Command"
    Invoke-Expression $Command
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Step '$StepName' failed with exit code $LASTEXITCODE. Stopping script."
        exit $LASTEXITCODE
    }
}

# Create job directory if it doesn't exist
if (!(Test-Path $JobDir)) {
    New-Item -ItemType Directory -Path $JobDir | Out-Null
}

# Import checksums from dedup_move_job_X_drive (optional, improves performance if available)
Run-Step "dedup-file-copy-fs import-checksums --job-dir $JobDir --other-db ..\dedup_move_job_X_drive\checksum-cache.db" "Import checksums from dedup_move_job_X_drive"

# Run the full workflow in one step using one-shot and destination index pool
Run-Step "dedup-file-copy-fs one-shot --job-dir $JobDir --job-name $JobName --src $SrcDir --dst $DstDir --dst-index-pool $DstIndexPool" "Run full workflow (one-shot with destination index pool)"
```

## Step-by-Step Breakdown
1. **Set environment variable**: Sets log level to WARNING for less verbose output.
2. **Initialize variables**: Defines job, source, destination, and index pool paths.
3. **Create job directory**: Ensures the job directory exists.
4. **Import checksums**: (Optional) Imports from a compatible checksum cache for faster deduplication.
5. **Run one-shot workflow**: Runs the full deduplication and copy process in a single command, using the destination index pool for robust deduplication.

## Notes
- All commands use dedup-file-copy-fs CLI (not fs-copy-tool).
- Adjust paths and job names as needed for your environment.
- For more advanced options, see the [main documentation](../standalone/external_ai_tool_doc.md).
