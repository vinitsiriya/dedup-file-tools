# fs-copy-tool: Portable Documentation for AI Tool Integration

## Overview
`fs-copy-tool` is a robust, resumable, and auditable file copy utility for safe, non-redundant media migration between storage pools. It uses an SQLite database to track all state, supports both fixed and removable drives, and provides a fully automated, testable, and auditable workflow for file migration, deduplication, and verification.

The tool supports a one-shot command to run the entire workflow in a single step, making it ideal for AI tool integration and automation scenarios.

## Architecture Note (2025-07)
- All job databases are now named `<job-name>.db` in the job directory. All CLI commands require `--job-name <job-name>`.
- The checksum cache database is always named `checksum-cache.db` in the job directory.
- The tool will not operate on legacy `copytool.db` files; migrate or re-initialize jobs as needed.


## Mechanism & Workflow
- The tool operates in phases: initialization, file addition, analysis, checksum calculation, copy, verification, and audit.
- All phases can be orchestrated in a single call using the one-shot command for automation and integration.
- All state and progress are tracked in a dedicated SQLite database (one per job directory).
- The CLI orchestrates all operations, ensuring resumability, deduplication, and auditability.
- The tool is designed to be idempotent: interrupted or failed operations can be safely resumed without data loss or duplication.
- Verification phases (shallow and deep) ensure data integrity after copy.
- All operations, errors, and results are queryable and auditable via the database and CLI.


For advanced automation and AI tool integration, all CLI options can also be provided in a YAML file using the `-c <config.yaml>` option. This enables workflows to be defined, versioned, and reused as code or data, making integration with external orchestrators or AI agents straightforward. For example:

```
python fs_copy_tool/main.py one-shot -c config.yaml
```
with a `config.yaml` such as:
```yaml
command: one-shot
job_dir: /mnt/job
job_name: job1
src:
  - /mnt/source1
dst:
  - /mnt/dest1
threads: 8
log_level: DEBUG
```
All CLI options are supported as YAML keys, and CLI arguments always override YAML config values if both are provided. This enables reproducible, declarative, and programmatically generated workflows for AI-driven automation.

## Import Checksums Feature (2025-07-15: Current Implementation)
The import checksums feature allows you to import file checksums from another compatible job's checksum cache database, enabling fast migration and verification across jobs.

- **Command:**
  ```
  import-checksums --job-dir <job_dir> --job-name <job_name> --other-db <other_job_dir>/checksum-cache.db
  ```
- **How it works:**
  1. Specify the current job directory (`--job-dir`), job name (`--job-name`), and the path to another compatible checksum cache database (`--other-db`).
  2. The tool reads the `checksum_cache` table from the other database (legacy table import is not supported).
  3. For each entry, it extracts:
     - `uid` (volume identifier)
     - `relative_path` (path relative to volume root)
     - `size` (file size)
     - `last_modified` (modification time)
     - `checksum` (SHA-256 hash)
     - `imported_at`, `last_validated`, `is_valid` (if present)
  4. It inserts or updates these values into the `checksum_cache` table in the current job's checksum cache database, along with an import timestamp and validation status.
  5. The `checksum_cache` table is used as a fallback for all copy and verification operations: if a file in the current job does not have a checksum in the main tables, the tool will look it up in the cache and use it if available and valid.
  6. The cache is indexed for fast lookup by checksum and (uid, relative_path).
  7. This process is robust and idempotent: repeated imports will not create duplicates, and only the latest valid checksum is used.

- **Example usage:**
  ```
  python fs_copy_tool/main.py import-checksums --job-dir <job_dir> --job-name <job_name> --other-db <other_job_dir>/checksum-cache.db
  ```
  This will import all checksums from the `checksum_cache` table in the other job's checksum cache database into the current job's `checksum_cache`.

- **Benefits:**
  - Avoids recomputing checksums for files that have not changed.
  - Greatly speeds up migration and verification for large datasets.
  - Ensures continuity and auditability across multiple migration jobs.

## Database Schema

- **checksum_cache** (in `checksum-cache.db`)
  - `uid` TEXT
  - `relative_path` TEXT
  - `size` INTEGER
  - `last_modified` INTEGER
  - `checksum` TEXT
  - `imported_at` INTEGER
  - `last_validated` INTEGER
  - `is_valid` INTEGER DEFAULT 1
  - PRIMARY KEY (`uid`, `relative_path`)

(Other tables: `source_files`, `destination_files`, `verification_shallow_results`, `verification_deep_results` are present in `<job-name>.db` for job state and verification.)

- Key Features
- Block-wise (4KB) file copying with SHA-256 checksums
- Deduplication: skips files already present in the destination (by checksum)
- Fully resumable: safely interrupt and resume at any time
- All state, logs, and planning files are stored in a dedicated job directory
- Stateful, file-level job setup and modification
- CLI commands for all phases: initialization, analysis, checksum, copy, resume, verification, audit, and more
- Comprehensive verification and audit commands
- **One-shot command:** Run the entire workflow in a single step for automation and integration
- Handles edge cases: partial/incomplete copies, missing files, already copied files, corrupted files (reports errors, does not fix)
- Cross-platform: Windows & Linux
- Full automated and manual test suite for all features and edge cases


## How It Works
You can run the full workflow in a single step using the one-shot command, or follow the step-by-step process below:


**One-shot (full workflow in one command):**
```
python fs_copy_tool/main.py one-shot --job-dir <job_dir> --job-name <job_name> --src <SRC_ROOT> --dst <DST_ROOT> [options]
```
Or, using a YAML config file for all options:
```
python fs_copy_tool/main.py one-shot -c config.yaml
```
*Runs all steps below in order, stops on error, prints "Done" on success. All CLI options can be set in the YAML file; CLI args override YAML values.*

**Step-by-step:**
1. **Initialize a job directory** to store all state and logs.
2. **Add files or directories** to the job database (file-level stateful setup).
3. **Analyze** source and destination volumes to gather file metadata.
4. **Compute checksums** for all files.
5. **Copy** only non-duplicate files from source to destination. *Before copying, the tool updates and validates all destination pool checksums with a progress bar to ensure deduplication is accurate and up to date.*
6. **Resume** interrupted or failed jobs safely.
7. **Verify** and audit all copy operations (shallow and deep verification).
8. **Import checksums** from another compatible checksum cache database if needed (from `checksum_cache` only).



## CLI Usage

To run the full workflow in one step (recommended for automation):
```
python fs_copy_tool/main.py one-shot --job-dir <job_dir> --job-name <job_name> --src <SRC_ROOT> --dst <DST_ROOT> [options]
```

Or use the step-by-step commands:
```
python fs_copy_tool/main.py <command> --job-dir <job_dir> --job-name <job_name> [other options]
```
Or, if installed as a package:
```
fs-copy-tool <command> --job-dir <job_dir> --job-name <job_name> [other options]
```

### Main Commands & Options

- `init --job-dir <job_dir> --job-name <job_name>`
  - Initialize a new job directory (creates `<job-name>.db` and `checksum-cache.db`).

- `import-checksums --job-dir <job_dir> --job-name <job_name> --other-db <other_job_dir>/checksum-cache.db`
  - Import checksums from another compatible job's checksum cache database.

- `analyze --job-dir <job_dir> --job-name <job_name> [--src <src_dir> ...] [--dst <dst_dir> ...]`
  - Analyze source and/or destination volumes to gather file metadata.

- `checksum --job-dir <job_dir> --job-name <job_name> --table <source_files|destination_files> [--threads N] [--no-progress]`
  - Compute or update checksums for files in the specified table.

- `copy --job-dir <job_dir> --job-name <job_name> [--src <src_dir> ...] [--dst <dst_dir> ...] [--threads N] [--no-progress] [--resume]`
  - Copy files from source to destination, skipping duplicates and resuming incomplete jobs.
  - `--resume` is always enabled by default and can be omitted.
  - Before copying, all destination pool checksums are updated and validated with a progress bar to ensure deduplication is accurate and up to date.

- `resume --job-dir <job_dir> --job-name <job_name> [--src <src_dir> ...] [--dst <dst_dir> ...] [--threads N] [--no-progress]`
  - Resume interrupted or failed copy operations.

- `status --job-dir <job_dir> --job-name <job_name>`
  - Show job progress and statistics.

- `log --job-dir <job_dir> --job-name <job_name>`
  - Show job log or audit trail.

- `verify --job-dir <job_dir> --job-name <job_name> [--src <src_dir> ...] [--dst <dst_dir> ...] [--stage <shallow|deep>]`
  - Verify copied files. Use `--stage shallow` for basic attribute checks, or `--stage deep` for checksum comparison.

- `deep-verify --job-dir <job_dir> --job-name <job_name> [--src <src_dir> ...] [--dst <dst_dir> ...]`
  - Perform deep verification (checksum comparison) between source and destination.

- `verify-status --job-dir <job_dir> --job-name <job_name>`
  - Show a summary of the latest shallow verification results for each file.

- `deep-verify-status --job-dir <job_dir> --job-name <job_name>`
  - Show a summary of the latest deep verification results for each file.

- `verify-status-summary --job-dir <job_dir> --job-name <job_name>`
  - Show a short summary of shallow verification results.

- `verify-status-full --job-dir <job_dir> --job-name <job_name>`
  - Show all shallow verification results (full history).

- `deep-verify-status-summary --job-dir <job_dir> --job-name <job_name>`
  - Show a short summary of deep verification results.

- `deep-verify-status-full --job-dir <job_dir> --job-name <job_name>`
  - Show all deep verification results (full history).

- `add-file --job-dir <job_dir> --job-name <job_name> --file <file_path>`
  - Add a single file to the job database.

- `add-source --job-dir <job_dir> --job-name <job_name> --src <src_dir>`
  - Recursively add all files from a directory to the job database.
  - (Uses batching and multithreading for fast file addition; progress bar is shown for large directories.)

- `add-to-destination-index-pool --job-dir <job_dir> --job-name <job_name> --dst <dst_dir>`
  - Scan and add/update all files in the destination pool index.

- `list-files --job-dir <job_dir> --job-name <job_name>`
  - List all files currently in the job database.

- `remove-file --job-dir <job_dir> --job-name <job_name> --file <file_path>`
  - Remove a file from the job database.

- `summary --job-dir <job_dir> --job-name <job_name>`
  - Print a summary of the job, including what has happened, where the logs are, and generate a CSV report (summary_report.csv) of all files with errors or not done.

**Notes:**
- All commands require both `--job-dir <job_dir>` and `--job-name <job_name>`.
- The checksum cache database is always `checksum-cache.db` in the job directory.
- For verification, always use `--stage shallow` or `--stage deep` (not `--phase`).
- The add-source command is optimized for large datasets using batching and multithreading, and will show a progress bar for visibility.
- All operations are resumable, auditable, and robust against interruption.


### Example Workflow
To run the full workflow in one step:
```
python fs_copy_tool/main.py one-shot --job-dir <job_dir> --job-name <job_name> --src <SRC_ROOT> --dst <DST_ROOT> [options]
```
Or, using a YAML config file:
```
python fs_copy_tool/main.py one-shot -c config.yaml
```

Or step-by-step:
```
python fs_copy_tool/main.py init --job-dir <job_dir> --job-name <job_name>
python fs_copy_tool/main.py add-source --job-dir <job_dir> --job-name <job_name> --src <SRC_ROOT>
python fs_copy_tool/main.py analyze --job-dir <job_dir> --job-name <job_name> --src <SRC_ROOT> --dst <DST_ROOT>
python fs_copy_tool/main.py checksum --job-dir <job_dir> --job-name <job_name> --table source_files
python fs_copy_tool/main.py checksum --job-dir <job_dir> --job-name <job_name> --table destination_files
python fs_copy_tool/main.py copy --job-dir <job_dir> --job-name <job_name> --src <SRC_ROOT> --dst <DST_ROOT>
python fs_copy_tool/main.py status --job-dir <job_dir> --job-name <job_name>
python fs_copy_tool/main.py verify --job-dir <job_dir> --job-name <job_name> --src <SRC_ROOT> --dst <DST_ROOT>
python fs_copy_tool/main.py deep-verify --job-dir <job_dir> --job-name <job_name> --src <SRC_ROOT> --dst <DST_ROOT>
python fs_copy_tool/main.py import-checksums --job-dir <job_dir> --job-name <job_name> --other-db <other_job_dir>/checksum-cache.db
python fs_copy_tool/main.py summary --job-dir <job_dir> --job-name <job_name>
```

## Edge Cases & Robustness
- Skips already copied files (deduplication)
- Handles partial/incomplete copies and resumes them
- Reports but does not fix corrupted files
- All operations are auditable and stateful

## Testing
- Run all tests with your preferred test runner (e.g., `pytest`)
- Full E2E, integration, and unit test coverage for all features and edge cases

## Project Structure
- `fs_copy_tool/` — Main source code
- `tests/` — Automated tests
- `e2e_tests/` — End-to-end and integration tests
- `docs/` — Documentation
- `scripts/` — Automation scripts
- `Taskfile.yml` — Cross-platform automation tasks

## Packaging & Installation
- Standard Python packaging via `setup.py` and `pyproject.toml`
- Install dependencies with `pip install -r requirements.txt`
- Install as a package: `pip install .`
- Entry point: `fs-copy-tool` (console script) or `python -m fs_copy_tool.main`

## License
MIT License
