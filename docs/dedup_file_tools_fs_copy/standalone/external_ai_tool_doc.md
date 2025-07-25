
# dedup-file-copy-fs: Portable Documentation for AI Tool Integration

## Table of Contents

- [Overview](#overview)
- [Architecture Note (2025-07)](#architecture-note-2025-07)
- [Mechanism & Workflow](#mechanism--workflow)
- [Import Checksums Feature](#import-checksums-feature-2025-07-15-current-implementation)
- [Database Schema](#database-schema)
- [How It Works](#how-it-works)
- [CLI Usage](#cli-usage)
- [Main Commands & Options](#main-commands--options)
- [Example Workflow](#example-workflow)
- [Edge Cases & Robustness](#edge-cases--robustness)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Packaging & Installation](#packaging--installation)
- [License](#license)

## Overview

`dedup-file-copy-fs` is a robust, resumable, and auditable file copy utility for safe, non-redundant media migration between storage pools. It uses an SQLite database to track all state, supports both fixed and removable drives, and provides a fully automated, testable, and auditable workflow for file migration, deduplication, and verification.

**New Feature (2025-07-18):**
The tool now includes an interactive config generator (`generate-config` command) that allows users or agents to create a YAML config file step-by-step via CLI prompts. This makes onboarding, automation, and integration even easier.

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


### Interactive Config Generation (2025-07-18: New Feature)

You can now generate a YAML config file interactively using the CLI:
```
python fs_copy_tool/main.py generate-config
```
`dedup-file-copy-fs` is a robust, resumable, and auditable file copy utility for safe, non-redundant media migration between storage pools. It uses an SQLite database to track all state, supports both fixed and removable drives, and provides a fully automated, testable, and auditable workflow for file migration, deduplication, and verification.

This will prompt for all required fields and write a config file for use with `-c`. This is ideal for onboarding, automation, and reducing manual errors. The generated config can then be used with any command that supports `-c`, for example:
```
python fs_copy_tool/main.py one-shot -c config.yaml
```
or
```
python fs_copy_tool/main.py copy -c config.yaml
```
Example generated `config.yaml`:
```yaml
command: one-shot
job_dir: /mnt/job
job_name: job1
`dedup-file-copy-fs` is a robust, resumable, and auditable file copy utility for safe, non-redundant media migration between storage pools. It uses an SQLite database to track all state, supports both fixed and removable drives, and provides a fully automated, testable, and auditable workflow for file migration, deduplication, and verification.
src:
  - /mnt/source1
dst:
  - /mnt/dest1
You can now generate a YAML config file interactively using the CLI:
```
dedup-file-copy-fs generate-config
```
All CLI options are supported as YAML keys, and CLI arguments always override YAML config values if both are provided. This enables reproducible, declarative, and programmatically generated workflows for AI-driven automation.

This will prompt for all required fields and write a config file for use with `-c`. This is ideal for onboarding, automation, and reducing manual errors. The generated config can then be used with any command that supports `-c`, for example:
```
dedup-file-copy-fs one-shot -c config.yaml
```
- **Command:**
```
dedup-file-copy-fs copy -c config.yaml
```
- **How it works:**
 **Example usage:**
 ```
 dedup-file-copy-fs import-checksums --job-dir <job_dir> --job-name <job_name> --other-db <other_job_dir>/checksum-cache.db
 ```
     - `relative_path` (path relative to volume root)
 ```
 dedup-file-copy-fs one-shot --job-dir <job_dir> --job-name <job_name> --src <SRC_ROOT> --dst <DST_ROOT> --dst-index-pool <POOL_PATH> [options]
 ```
     - `imported_at`, `last_validated`, `is_valid` (if present)
 ```
 dedup-file-copy-fs one-shot -c config.yaml --dst-index-pool <POOL_PATH>
 ```
  7. This process is robust and idempotent: repeated imports will not create duplicates, and only the latest valid checksum is used.
 ```
 dedup-file-copy-fs one-shot -c config.yaml
 ```
  python fs_copy_tool/main.py import-checksums --job-dir <job_dir> --job-name <job_name> --other-db <other_job_dir>/checksum-cache.db
 ```
 dedup-file-copy-fs generate-config
 ```
- **Benefits:**
 ```
 dedup-file-copy-fs one-shot -c config.yaml --dst-index-pool /mnt/pool
 ```

 ```
 dedup-file-copy-fs one-shot --job-dir jobs/job1 --job-name job1 --src /mnt/src --dst /mnt/dst --dst-index-pool /mnt/pool --threads 4 --log-level DEBUG
 ```
  - `uid` TEXT
 ```
 dedup-file-copy-fs init -c config.yaml
 ```
  - `checksum` TEXT
 ```
 dedup-file-copy-fs add-source -c config.yaml
 ```
  - PRIMARY KEY (`uid`, `relative_path`)
 ```
 dedup-file-copy-fs add-to-destination-index-pool -c config.yaml --dst-index-pool /mnt/pool
 ```
- Key Features
 ```
 dedup-file-copy-fs analyze -c config.yaml
 ```
- All state, logs, and planning files are stored in a dedicated job directory
 ```
 dedup-file-copy-fs checksum -c config.yaml
 ```
- **One-shot command:** Run the entire workflow in a single step for automation and integration
 ```
 dedup-file-copy-fs copy -c config.yaml
 ```

 ```
 dedup-file-copy-fs status -c config.yaml
 ```
You can run the full workflow in a single step using the one-shot command, or follow the step-by-step process below. To simplify setup, use the interactive config generator to create your YAML config file first:
 ```
 dedup-file-copy-fs verify -c config.yaml
 ```
```
 ```
 dedup-file-copy-fs deep-verify -c config.yaml
 ```

 ```
 dedup-file-copy-fs import-checksums -c config.yaml
 ```
```
 ```
 dedup-file-copy-fs summary -c config.yaml
 ```
```
 `dedup_file_tools_fs_copy/` — Main source code

 Entry point: `dedup-file-copy-fs` (console script) or `python -m dedup_file_tools_fs_copy.main`
- Use `--dst-index-pool <POOL_PATH>` (or `--destination-index-pool <POOL_PATH>`) to specify a destination index pool for deduplication or multi-destination workflows.
- This is used in the "Add to Destination Index Pool" step of the workflow.
- If not provided, the first `--dst` value is used as the pool by default.

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

### Generate a Config File Interactively
To create a YAML config file interactively, run:
```
dedup-file-copy-fs generate-config
```
Follow the prompts to generate a config file for use with `-c`.

### Run the Full Workflow
To run the full workflow in one step (recommended for automation):
```
dedup-file-copy-fs one-shot -c config.yaml
```
Or use the step-by-step commands:
```
dedup-file-copy-fs <command> -c config.yaml
```
Or, if installed as a package:
```
python -m dedup_file_tools_fs_copy.main <command> -c config.yaml
```



### Main Commands & Options

- `generate-config`
  - Launches an interactive prompt to create a YAML config file for use with `-c`.
  - Example:
    ```
    python fs_copy_tool/main.py generate-config
    ```
  - Prompts for all required fields and writes a config file for use with any command supporting `-c`.

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
  - You can also use `--dst-index-pool <POOL_PATH>` or `--destination-index-pool <POOL_PATH>` to specify the pool explicitly in one-shot and related commands.

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


### Example Workflow
1. **Generate a config file interactively:**
   ```
   python fs_copy_tool/main.py generate-config
   ```
2. **Run the full workflow in one step (with destination index pool):**
   ```
   python fs_copy_tool/main.py one-shot -c config.yaml --dst-index-pool /mnt/pool
   ```
   Or, without a config file:
   ```
   python fs_copy_tool/main.py one-shot --job-dir jobs/job1 --job-name job1 --src /mnt/src --dst /mnt/dst --dst-index-pool /mnt/pool --threads 4 --log-level DEBUG
   ```
   If `--dst-index-pool` is not specified, the first `--dst` value is used as the pool by default.
3. **Or step-by-step:**
   ```
   dedup-file-copy-fs init -c config.yaml
   dedup-file-copy-fs add-source -c config.yaml
   dedup-file-copy-fs add-to-destination-index-pool -c config.yaml --dst-index-pool /mnt/pool
   dedup-file-copy-fs analyze -c config.yaml
   dedup-file-copy-fs checksum -c config.yaml
   dedup-file-copy-fs copy -c config.yaml
   dedup-file-copy-fs status -c config.yaml
   dedup-file-copy-fs verify -c config.yaml
   dedup-file-copy-fs deep-verify -c config.yaml
   dedup-file-copy-fs import-checksums -c config.yaml
   dedup-file-copy-fs summary -c config.yaml
   ```

## Edge Cases & Robustness
- Skips already copied files (deduplication)
- Handles partial/incomplete copies and resumes them
- Reports but does not fix corrupted files
- All operations are auditable and stateful

## Testing
- Run all tests with your preferred test runner (e.g., `pytest`)
- Full E2E, integration, and unit test coverage for all features and edge cases

- `dedup_file_tools_fs_copy/` — Main source code
- `tests/` — Automated tests
- `e2e_tests/` — End-to-end and integration tests
- `docs/` — Documentation
- `scripts/` — Automation scripts
- `Taskfile.yml` — Cross-platform automation tasks

## Packaging & Installation
- Standard Python packaging via `setup.py` and `pyproject.toml`
- Install dependencies with `pip install -r requirements.txt`
- Install as a package: `pip install .`
- Entry point: `dedup-file-copy-fs` (console script) or `python -m dedup_file_tools_fs_copy.main`

## License
MIT License
