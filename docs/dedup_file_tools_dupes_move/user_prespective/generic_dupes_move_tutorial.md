# Tutorial: How to Find and Move Duplicate Files with dedup-file-move-dupes

This guide explains, in plain English, how to use `dedup-file-move-dupes` to scan any folder or drive for duplicate files and safely move them to a separate location. The steps are generic and can be adapted for any source, destination, or operating system.

## What You'll Need
- The `dedup-file-move-dupes` tool installed (see the main README for installation instructions)
- A folder or drive you want to scan for duplicates (the "lookup pool")
- A folder where you want to move the duplicates (the "dupes folder")

## Step-by-Step Instructions

### 1. Set Up Your Job
Decide on a job directory and a job name. This is where all state and logs will be kept. For example:
- Job directory: `./my_dedup_job`
- Job name: `my_dedup_job`

### 2. Initialize the Job
Create the job database and state files:
```sh
dedup-file-move-dupes init --job-dir ./my_dedup_job --job-name my_dedup_job
```

### 3. Analyze for Duplicates
Scan your lookup pool for duplicate files:
```sh
dedup-file-move-dupes analyze --job-dir ./my_dedup_job --job-name my_dedup_job --lookup-pool /path/to/scan
```

### 4. Preview Planned Moves
See which files will be moved before making any changes:
```sh
dedup-file-move-dupes preview-summary --job-dir ./my_dedup_job --job-name my_dedup_job
```

### 5. Move Duplicates
Move all but one file per duplicate group to your dupes folder:
```sh
dedup-file-move-dupes move --job-dir ./my_dedup_job --job-name my_dedup_job --lookup-pool /path/to/scan --dupes-folder /path/to/dupes
```

### 6. Verify
Check that all planned moves were successful and no duplicates remain:
```sh
dedup-file-move-dupes verify --job-dir ./my_dedup_job --job-name my_dedup_job --lookup-pool /path/to/scan --dupes-folder /path/to/dupes
```

### 7. Summary
Generate a CSV report and print a summary of deduplication results:
```sh
dedup-file-move-dupes summary --job-dir ./my_dedup_job --job-name my_dedup_job
```

## One-Shot: Do It All in One Command
If you want to run the full workflow in a single step, use the `one-shot` command:
```sh
dedup-file-move-dupes one-shot --job-dir ./my_dedup_job --job-name my_dedup_job --lookup-pool /path/to/scan --dupes-folder /path/to/dupes
```

## Tips
- Always review the preview before running the move phase, especially on important data.
- You can use any folder or drive for the lookup pool and dupes folder—just update the paths.
- All actions are logged and auditable for safety and traceability.
- For more advanced options, see the [CLI reference](../developer_reference/cli.md).

---

This tutorial is designed to help anyone—no scripting required!—get started with safe, deduplicated file moving using dedup-file-move-dupes.
