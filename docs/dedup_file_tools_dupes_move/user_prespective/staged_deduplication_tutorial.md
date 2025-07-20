
# Tutorial: Staged Deduplication Workflow for X: Drive with dedup-file-move-dupes

This tutorial walks you through a safe, staged deduplication process for a large photo collection on your X: drive using `dedup-file-move-dupes`. The workflow is designed for maximum control: you can preview planned duplicate moves before actually moving any files.

## Prerequisites
- `dedup-file-move-dupes` installed (see main README for pipx instructions)
- Lookup pool: The folder or drive to scan for duplicates (e.g., `X:\AllPhotos`)
- Dupes folder: Where duplicates will be moved (e.g., `X:\_deduped_dupes`)
- Sufficient free space on the destination for moved files

## Variables
```powershell
$JobDir = "C:\Users\vinit\OneDrive\Documents\project-4\backup-task\dedup_move_job_X_drive"
$JobName = "X_drive_dedup"
$LookupPool = "X:\AllPhotos"
$DupesFolder = "X:\_deduped_dupes"
$Threads = 8  # Adjust as needed
```

## PowerShell Script Example
```powershell
# Ensure job directory exists
if (!(Test-Path -Path $JobDir)) {
    New-Item -ItemType Directory -Path $JobDir | Out-Null
}

# 1. Initialize the job
dedup-file-move-dupes init `
    --job-dir $JobDir `
    --job-name $JobName

# 2. Analyze for duplicates
dedup-file-move-dupes analyze `
    --job-dir $JobDir `
    --job-name $JobName `
    --lookup-pool $LookupPool `
    --threads $Threads

# 3. Preview planned duplicate moves
dedup-file-move-dupes preview-summary `
    --job-dir $JobDir `
    --job-name $JobName

# 4. Move duplicates (uncomment after reviewing preview)
# dedup-file-move-dupes move `
#     --job-dir $JobDir `
#     --job-name $JobName `
#     --lookup-pool $LookupPool `
#     --dupes-folder $DupesFolder `
#     --threads $Threads

# 5. Verify moves (run after move)
# dedup-file-move-dupes verify `
#     --job-dir $JobDir `
#     --job-name $JobName `
#     --lookup-pool $LookupPool `
#     --dupes-folder $DupesFolder `
#     --threads $Threads

# 6. Generate summary (run after verify)
# dedup-file-move-dupes summary `
#     --job-dir $JobDir `
#     --job-name $JobName
```

## Step-by-Step Breakdown
1. **Initialize the job**: Sets up the job directory and database for tracking all actions.
2. **Analyze for duplicates**: Scans the lookup pool, computes checksums, and plans which files are duplicates.
3. **Preview planned moves**: Lets you review which files will be moved before any action is taken.
4. **Move duplicates**: (Uncomment to enable) Moves all but one file per duplicate group to the dupes folder.
5. **Verify**: Checks that all planned moves were successful and no duplicates remain.
6. **Summary**: Generates a CSV report and prints a summary of deduplication results.

## Tips
- Always review the preview before running the move phase, especially on large or important datasets.
- You can adjust the number of threads for faster processing on powerful machines.
- All actions are logged and auditable for safety and traceability.
- For more advanced options, see the [CLI reference](../developer_reference/cli.md).


This tutorial is designed for anyone who wants a safe, auditable, and staged deduplication workflow using dedup-file-move-dupes.

## One-Shot: Run the Full Workflow in a Single Command

If you want to run the entire deduplication workflow (init, analyze, preview-summary, move, verify, summary) in one step, use the `one-shot` command. This is ideal for automation or when you want everything handled in a single call.

### Example Command
```powershell
dedup-file-move-dupes one-shot `
    --job-dir $JobDir `
    --job-name $JobName `
    --lookup-pool $LookupPool `
    --dupes-folder $DupesFolder `
    --threads $Threads
```

You can also use a YAML config file for reproducible workflows:
```powershell
dedup-file-move-dupes one-shot --config config.yaml
```

For a detailed explanation of all phases and options, see the [CLI Reference](../developer_reference/cli.md).
