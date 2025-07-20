# Tutorial: Full L: to X: Drive Copy Workflow with dedup-file-copy-fs

This tutorial demonstrates a complete, step-by-step workflow for copying all files from `L:` to `X:\L-drive-copy` using `dedup-file-copy-fs`. It includes checksum import, deduplication, and verification, and is suitable for scripting or manual execution.

## Prerequisites
- `dedup-file-copy-fs` installed (see main README for pipx instructions)
- Source drive: `L:`
- Destination drive: `X:`
- Optional: Existing checksum cache database for import

## Variables
```powershell
$JobDir = ".\copy_job_L_to_X_L-drive-copy"
$JobName = "L_to_X_L-drive-copy"
$SrcDir = "L:\"
$DstDir = "X:\L-drive-copy"
$DstIndexPool = "X:\"
$ChecksumCacheDb = ".dbs\checksum_cache_for_import.db"
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

Run-Step "dedup-file-copy-fs init --job-dir $JobDir --job-name $JobName" "Initialize job"
Run-Step "dedup-file-copy-fs import-checksums --job-dir $JobDir --job-name $JobName --other-db 'C:\Users\vinit\OneDrive\Documents\project-4\backup-task\copy_job_M_to_X_AllPhotos\checksum-cache.db'" "Import checksums from M_to_X_AllPhotos job"
Run-Step "dedup-file-copy-fs add-source --job-dir $JobDir --job-name $JobName --src $SrcDir" "Add source directory"
Run-Step "dedup-file-copy-fs add-to-destination-index-pool --job-dir $JobDir --job-name $JobName --dst $DstIndexPool" "Add destination index pool (X:\)"
Run-Step "dedup-file-copy-fs analyze --job-dir $JobDir --job-name $JobName --src $SrcDir --dst $DstDir" "Analyze source and destination"
Run-Step "dedup-file-copy-fs checksum --job-dir $JobDir --job-name $JobName --table source_files" "Compute checksums for source files"
Run-Step "dedup-file-copy-fs checksum --job-dir $JobDir --job-name $JobName --table destination_files" "Compute checksums for destination files"
Run-Step "dedup-file-copy-fs copy --job-dir $JobDir --job-name $JobName --src $SrcDir --dst $DstDir" "Start copy operation"
Run-Step "dedup-file-copy-fs verify --job-dir $JobDir --job-name $JobName --stage shallow" "Verify copied files (shallow)"
Run-Step "dedup-file-copy-fs verify --job-dir $JobDir --job-name $JobName --stage deep" "Verify copied files (deep)"
Run-Step "dedup-file-copy-fs status --job-dir $JobDir --job-name $JobName" "Show job status"
```

## Step-by-Step Breakdown
1. **Initialize the job**: Creates the job directory and database.
2. **Import checksums**: (Optional) Import from a compatible checksum cache for faster deduplication.
3. **Add source**: Indexes all files from the source drive.
4. **Add destination index pool**: Indexes all files in the destination pool for deduplication.
5. **Analyze**: Scans source and destination for file metadata.
6. **Checksum**: Computes checksums for both source and destination files.
7. **Copy**: Copies only unique files from source to destination.
8. **Verify**: Performs both shallow and deep verification of copied files.
9. **Status**: Shows job progress and summary.

## Notes
- All commands use the new dedup-file-copy-fs CLI (not fs-copy-tool).
- Adjust paths and job names as needed for your environment.
- For more advanced options, see the [main documentation](../standalone/external_ai_tool_doc.md).
