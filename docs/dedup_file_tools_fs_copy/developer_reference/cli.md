# CLI Reference: dedup_file_tools_fs_copy

This document provides a complete reference for the dedup_file_tools_fs_copy CLI, matching the code in main.py and all handler/phase logic.

## Usage
```
python -m dedup_file_tools_fs_copy.main <command> [OPTIONS]
```
or, if installed as a package:
```
fs-copy-tool <command> [OPTIONS]
```

## Global Options
- `-c`, `--config FILE`: Path to YAML configuration file (all options can be set in YAML; CLI args override YAML values)
- `--log-level LEVEL`: Set logging verbosity (default: WARNING)

## Commands and Arguments

### `generate-config`
Interactively generate a YAML config file for use with `-c`.

### `init`
Initialize a new job directory (creates `<job-name>.db` and `checksum-cache.db`).
- `--job-dir PATH` (required): Path to job directory
- `--job-name NAME` (required): Name of the job (database file will be `<job-name>.db`)

### `import-checksums`
Import checksums from the checksum_cache table of another compatible database.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--other-db PATH` (required): Path to other compatible SQLite database (must have checksum_cache table)

### `analyze`
Analyze source and/or destination volumes to gather file metadata.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--src PATH [PATH ...]`: Source volume root(s)
- `--dst PATH [PATH ...]`: Destination volume root(s)

### `checksum`
Compute or update checksums for files in the specified table.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--table {source_files|destination_files}`: Table to use for checksumming (default: source_files)
- `--threads N`: Number of threads for parallel operations (default: 4)
- `--no-progress`: Disable progress bars

### `copy`
Copy files from source to destination, skipping duplicates and resuming incomplete jobs.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--src PATH [PATH ...]`: Source volume root(s)
- `--dst PATH [PATH ...]`: Destination volume root(s)
- `--threads N`: Number of threads for parallel operations (default: 4)
- `--no-progress`: Disable progress bars
- `--resume`: Resume incomplete jobs (default: True for copy phase)

### `resume`
Resume interrupted or failed copy operations.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--src PATH [PATH ...]`: Source volume root(s)
- `--dst PATH [PATH ...]`: Destination volume root(s)
- `--threads N`: Number of threads for parallel operations (default: 4)
- `--no-progress`: Disable progress bars

### `status`
Show job progress and statistics.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)

### `log`
Show job log or audit trail.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)

### `verify`
Verify copied files. Use `--stage shallow` for basic attribute checks, or `--stage deep` for checksum comparison.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--src PATH [PATH ...]`: Source volume root(s)
- `--dst PATH [PATH ...]`: Destination volume root(s)
- `--stage {shallow|deep}`: Verification stage (default: shallow)

### `deep-verify`
Perform deep verification (checksum comparison) for copied files.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--src PATH [PATH ...]`: Source volume root(s)
- `--dst PATH [PATH ...]`: Destination volume root(s)

### `verify-status`, `deep-verify-status`, `verify-status-summary`, `verify-status-full`, `deep-verify-status-summary`, `deep-verify-status-full`
Show verification results and summaries.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)

### `add-file`
Add a single file to the job database.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--file FILE_PATH` (required)

### `add-source`
Add a source directory to the job database.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--src SRC_DIR` (required)

### `list-files`
List all files in the job database.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)

### `remove-file`
Remove a file from the job database.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--file FILE_PATH` (required)

### `one-shot`
Run the full workflow (init, import, add-source, analyze, checksum, copy, verify, summary) in one command.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--src PATH [PATH ...]` (required)
- `--dst PATH [PATH ...]` (required)
- `--threads N`: Number of threads for parallel operations (default: 4)
- `--no-progress`: Disable progress bars
- `--resume`: Resume incomplete jobs (default: True for copy phase)
- `--reverify`: Force re-verification in verify/deep-verify
- `--checksum-db PATH`: Custom checksum DB path (default: <job-dir>/checksum-cache.db)
- `--other-db PATH`: Path to another compatible SQLite database for importing checksums
- `--table {source_files|destination_files}`: Table to use for checksumming (default: source_files)
- `--stage {shallow|deep}`: Verification stage (default: shallow)
- `--skip-verify`: Skip verification steps
- `--deep-verify`: Perform deep verification after shallow verification
- `--dst-index-pool PATH`: Path to destination index pool (default: value of --dst)

### `add-to-destination-index-pool`
Scan and add/update all files in the destination pool index.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--dst DST_DIR` (required)
