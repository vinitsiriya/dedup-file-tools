# Tutorial: Comparing Directories with dedup-file-compare

This tutorial walks you through a typical workflow for comparing two directories using the `dedup-file-compare` tool. It is designed for users who want to verify, audit, or synchronize large file sets, such as backups or photo archives.

## Prerequisites
- Install `dedup-file-compare` and its dependencies.
- Ensure you have access to the directories you want to compare.
- (Optional) Have a checksum cache database from a previous copy job for faster comparison.

## Example Scenario
Suppose you want to compare your source photo directory on drive D: with a backup on drive X:.

- **Source Directory:** `D:\photos`
- **Backup Directory:** `X:\AllPhotos\more\ws2-pc-data\d_photos`
- **Job Directory:** `compare_job_D_to_X_d_photos`
- **Job Name:** `compare_D_to_X_d_photos`
- **Checksum Cache (optional):** `copy_job_D_to_X_d_photos\checksum-cache.db`


## Step-by-Step Workflow

### 1. Set Up Environment Variables (PowerShell)
```powershell
$env:LOG_LEVEL = "WARNING"
$JobDir = ".\compare_job_D_to_X_d_photos"
$JobName = "compare_D_to_X_d_photos"
$LeftDir = "D:\photos"
$RightDir = "X:\AllPhotos\more\ws2-pc-data\d_photos"
$ChecksumsDb = ".\copy_job_D_to_X_d_photos\checksum-cache.db"
```

### 2. Initialize the Compare Job
```powershell
dedup-file-compare init --job-dir $JobDir --job-name $JobName
```

### 3. (Optional) Import Checksums from Copy Job
If you have a checksum cache from a previous copy job, import it to speed up comparison:
```powershell
dedup-file-compare import-checksums --job-dir $JobDir --job-name $JobName --other-db $ChecksumsDb
```

### 4. Add Source and Destination Directories
```powershell
dedup-file-compare add-to-left --job-dir $JobDir --job-name $JobName --dir $LeftDir
dedup-file-compare add-to-right --job-dir $JobDir --job-name $JobName --dir $RightDir
```

### 5. Find Missing or Mismatched Files
```powershell
dedup-file-compare find-missing-files --job-dir $JobDir --job-name $JobName
```

### 6. Export Results to CSV
This creates a timestamped reports directory with separate CSVs for identical, missing, and different files.
```powershell
dedup-file-compare show-result --job-dir $JobDir --job-name $JobName --output $JobDir\compare_results.csv
```


## One-Shot Full Workflow

You can run the entire workflow in a single command using `one-shot`. This will initialize the job, add both directories, compare, and export results:

```powershell
# (Optional) Import checksums from a previous copy job for faster comparison
dedup-file-compare import-checksums --job-dir $JobDir --job-name $JobName --other-db $ChecksumsDb

# Run the full workflow in one step
dedup-file-compare one-shot --job-dir $JobDir --job-name $JobName --left $LeftDir --right $RightDir --output $JobDir\compare_results.csv
```

You can also add options like `--threads`, `--summary`, or `--full-report` as needed.

## What Happens Next?
- Results are stored in the job's SQLite database for audit and scripting.
- CSV files are written to a timestamped `reports_YYYYMMDD_HHMMSS` directory under your job directory.
- You can review identical, missing, and different files in the generated reports.

## Tips
- Use `--threads N` to speed up checksum calculation on large datasets.
- Use `--no-progress` for scripting or automation.
- Use `--show` to filter results (identical, different, unique-left, unique-right, all).
- For more details, see the [User Perspective README](README.md) and [CLI Reference](cli.md).

---
For troubleshooting or advanced scripting, see the developer reference and requirements documentation.
