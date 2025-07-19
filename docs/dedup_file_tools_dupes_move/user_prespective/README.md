# Deduplication/Removal Tool: User Guide

Welcome to the deduplication/removal tool! This guide will help you quickly get started, understand the main features, and use the CLI for robust, auditable duplicate file management.

---

## What is this tool?
This tool scans a folder (or set of folders), finds duplicate files, and moves/removes them in a safe, auditable, and resumable way. All actions are tracked in a job-specific database for full traceability.

---


## CLI Commands Overview

Here are all available CLI commands for the deduplication/removal tool:

- **init**: Initialize a new deduplication job.
  - Example: `dedup-file-move-dupes init --job-dir ./myjob --job-name myjob`
- **analyze**: Scan for duplicates and prepare the move plan.
  - Example: `dedup-file-move-dupes analyze --job-dir ./myjob --job-name myjob --lookup-pool ./data --threads 8`
- **preview-summary**: Preview planned duplicate groups and moves.
  - Example: `dedup-file-move-dupes preview-summary --job-dir ./myjob --job-name myjob`
- **move**: Move or remove duplicate files as planned.
  - Example: `dedup-file-move-dupes move --job-dir ./myjob --job-name myjob --dupes-folder ./dupes --threads 8`
    *Note: `--dupes-folder` is only required the first time you run `move`.*
- **verify**: Verify that all planned moves/removals were successful.
  - Example: `dedup-file-move-dupes verify --job-dir ./myjob --job-name myjob --threads 8`
- **summary**: Print a summary and generate a CSV report of results.
  - Example: `dedup-file-move-dupes summary --job-dir ./myjob --job-name myjob`
- **import-checksums**: Import checksums from another compatible database.
  - Example: `dedup-file-move-dupes import-checksums --job-dir ./myjob --job-name myjob --other-db ./otherjob/myjob.db`
- **one-shot**: Run the full deduplication workflow in one command.
  - Example: `dedup-file-move-dupes one-shot --job-dir ./myjob --job-name myjob --lookup-pool ./data --dupes-folder ./dupes --threads 8`

---

## Quickstart

### 1. Install the tool
Install via pip (in your virtual environment or system-wide):
```
pip install .
```
Or use pipx for isolated CLI usage:
```
pipx install .
```

### 2. Initialize a job
Create a job directory and database:
```
dedup-file-move-dupes init --job-dir ./myjob --job-name myjob
```

### 3. Analyze for duplicates
Scan your folder for duplicates (using 8 threads):
```
dedup-file-move-dupes analyze --job-dir ./myjob --job-name myjob --lookup-pool ./data --threads 8
```

### 4. Preview planned moves
See what will be moved/removed:
```
dedup-file-move-dupes preview-summary --job-dir ./myjob --job-name myjob
```

### 5. Move duplicates
Move all duplicates to a separate folder:
```
dedup-file-move-dupes move --job-dir ./myjob --job-name myjob --dupes-folder ./dupes --threads 8
```
*Note: `--dupes-folder` is only required the first time you run `move`. On subsequent runs, it is loaded from job metadata.*

### 6. Verify
Check that all moves/removals succeeded:
```
dedup-file-move-dupes verify --job-dir ./myjob --job-name myjob --threads 8
```
*Note: The tool loads the `dupes-folder` from job metadata set during the move phase.*

### 7. Summary
Get a CSV and console summary:
```
dedup-file-move-dupes summary --job-dir ./myjob --job-name myjob
```

---

## One-Shot Workflow
Run the entire workflow in one command:
```
dedup-file-move-dupes one-shot --job-dir ./myjob --job-name myjob --lookup-pool ./data --dupes-folder ./dupes --threads 8
```

---

## Importing Checksums
If you have checksums from another job or run, you can import them:
```
dedup-file-move-dupes import-checksums --job-dir ./myjob --job-name myjob --other-db ./otherjob/myjob.db
```

---

## YAML Config Support
You can use a YAML config file for reproducible runs:
```
dedup-file-move-dupes one-shot --config config.yaml
```
Command-line arguments always override config values.

---


## About UidPath: Robust, Portable File Tracking
This tool uses a system-independent path abstraction called **UidPath**. Instead of relying on drive letters (which can change, especially on Windows), UidPath uses a unique identifier (UID) for each filesystem and stores file paths relative to the mount point. This means:
- Your checksum cache and job database remain valid even if drive letters or mount points change.
- The tool is robust to moving drives between systems or plugging them into different USB ports.
- Deduplication and verification work reliably across different environments.
For more details, see the [UidPath documentation](../../dedup_file_tools_commons/uidpath.md).

## Troubleshooting & Tips
- All logs and job state are stored in your job directory.
- If a command fails, check the logs in the job directory for details.
- You can safely re-run any phase; the tool is idempotent and will not repeat completed work.
- Use more threads for faster processing on large datasets.
- The tool never deletes files from your original data folder unless you explicitly move them to a removal folder.
- If you omit `--dupes-folder` in `move` or `verify`, the tool will use the value saved in job metadata from the first move phase.

---

## More Help
- For full CLI reference and advanced usage, see the developer documentation in `docs/dedup_file_tools_dupes_move/developer_reference/cli.md`.
- For protocol and agent integration, see `docs/dedup_file_tools_dupes_move/developer_reference/standalone/external_ai_tool_doc.md`.

---

Happy deduplicating!
