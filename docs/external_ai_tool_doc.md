# fs-copy-tool: Complete Documentation for AI Tool Integration

## Overview
`fs-copy-tool` is a robust, resumable, and auditable file copy utility for safe, non-redundant media migration between storage pools. It uses an SQLite database to track all state, supports both fixed and removable drives, and provides a fully automated, testable, and auditable workflow for file migration, deduplication, and verification.

## Mechanism & Workflow
- The tool operates in phases: initialization, file addition, analysis, checksum calculation, copy, verification, and audit.
- All state and progress are tracked in a dedicated SQLite database (one per job directory).
- The CLI orchestrates all operations, ensuring resumability, deduplication, and auditability.
- The tool is designed to be idempotent: interrupted or failed operations can be safely resumed without data loss or duplication.
- Verification phases (shallow and deep) ensure data integrity after copy.
- All operations, errors, and results are queryable and auditable via the database and CLI.

## Import Checksums Feature (Full Implementation)
The import checksums feature is implemented as follows:

- **Command:**
  ```
  import-checksums --job-dir <path> --old-db <old_db_path> [--table <source_files|destination_files>]
  ```
- **How it works:**
  1. The user specifies the current job directory (`--job-dir`) and the path to an old SQLite database (`--old-db`).
  2. The tool opens the old database and reads the specified table (`source_files` or `destination_files`).
  3. For each file entry in the old table, it extracts:
     - `uid` (volume identifier)
     - `relative_path` (path relative to volume root)
     - `size` (file size)
     - `last_modified` (modification time)
     - `checksum` (SHA-256 hash)
  4. It inserts or updates these values into the `checksum_cache` table in the current job's database, along with an import timestamp and validation status.
  5. The `checksum_cache` table is then used as a fallback for all copy and verification operations: if a file in the current job does not have a checksum in the main tables, the tool will look it up in the cache and use it if available and valid.
  6. The cache is indexed for fast lookup by checksum and (uid, relative_path).
  7. This process is robust and idempotent: repeated imports will not create duplicates, and only the latest valid checksum is used.

- **Relevant code locations:**
  - CLI command and argument parsing: `fs_copy_tool/main.py` (see `import-checksums` command)
  - Database schema and cache table: `fs_copy_tool/db.py` (see `checksum_cache` table definition)
  - Import logic: implemented in the handler for the `import-checksums` command in `main.py`

- **Example usage:**
  ```
  .venv\Scripts\python.exe fs_copy_tool/main.py import-checksums --job-dir .copy-task --old-db old_job/copytool.db --table source_files
  ```
  This will import all checksums from the `source_files` table in the old job's database into the current job's `checksum_cache`.

- **Benefits:**
  - Avoids recomputing checksums for files that have not changed.
  - Greatly speeds up migration and verification for large datasets.
  - Ensures continuity and auditability across multiple migration jobs.

## Database Schema: Old vs. New

### Old Database Schema (prior jobs)
Typically, the old database used for import will have at least the following tables:

- **source_files**
  - `uid` TEXT
  - `relative_path` TEXT
  - `last_modified` INTEGER
  - `size` INTEGER
  - `checksum` TEXT (may be present)
  - (other columns: `copy_status`, `last_copy_attempt`, `error_message`)
  - PRIMARY KEY (`uid`, `relative_path`)

- **destination_files**
  - `uid` TEXT
  - `relative_path` TEXT
  - `last_modified` INTEGER
  - `size` INTEGER
  - `checksum` TEXT (may be present)
  - (other columns: `copy_status`, `error_message`)
  - PRIMARY KEY (`uid`, `relative_path`)

- Indexes may exist on `checksum`, `copy_status`, etc.

### New Database Schema (current job, as of 2025-07-15)
Defined in `fs_copy_tool/db.py`:

- **source_files**
  - `uid` TEXT
  - `relative_path` TEXT
  - `last_modified` INTEGER
  - `size` INTEGER
  - `copy_status` TEXT
  - `last_copy_attempt` INTEGER
  - `error_message` TEXT
  - PRIMARY KEY (`uid`, `relative_path`)

- **destination_files**
  - `uid` TEXT
  - `relative_path` TEXT
  - `last_modified` INTEGER
  - `size` INTEGER
  - `copy_status` TEXT
  - `error_message` TEXT
  - PRIMARY KEY (`uid`, `relative_path`)

- **checksum_cache**
  - `uid` TEXT
  - `relative_path` TEXT
  - `size` INTEGER
  - `last_modified` INTEGER
  - `checksum` TEXT
  - `imported_at` INTEGER
  - `last_validated` INTEGER
  - `is_valid` INTEGER DEFAULT 1
  - PRIMARY KEY (`uid`, `relative_path`)

- **verification_shallow_results**
  - `uid` TEXT
  - `relative_path` TEXT
  - `exists` INTEGER
  - `size_matched` INTEGER
  - `last_modified_matched` INTEGER
  - `expected_size` INTEGER
  - `actual_size` INTEGER
  - `expected_last_modified` INTEGER
  - `actual_last_modified` INTEGER
  - `verify_status` TEXT
  - `verify_error` TEXT
  - `timestamp` INTEGER
  - PRIMARY KEY (`uid`, `relative_path`, `timestamp`)

- **verification_deep_results**
  - `uid` TEXT
  - `relative_path` TEXT
  - `checksum_matched` INTEGER
  - `expected_checksum` TEXT
  - `src_checksum` TEXT
  - `dst_checksum` TEXT
  - `verify_status` TEXT
  - `verify_error` TEXT
  - `timestamp` INTEGER
  - PRIMARY KEY (`uid`, `relative_path`, `timestamp`)

- **Indexes**
  - On `copy_status`, `checksum`, and (`uid`, `relative_path`) for fast lookups and robust state tracking.

## Key Features
- Block-wise (4KB) file copying with SHA-256 checksums
- Deduplication: skips files already present in the destination (by checksum)
- Fully resumable: safely interrupt and resume at any time
- All state, logs, and planning files are stored in a dedicated job directory
- Stateful, file-level job setup and modification
- CLI commands for all phases: initialization, analysis, checksum, copy, resume, verification, audit, and more
- Comprehensive verification and audit commands
- Handles edge cases: partial/incomplete copies, missing files, already copied files, corrupted files (reports errors, does not fix)
- Cross-platform: Windows & Linux
- Full automated and manual test suite for all features and edge cases

## How It Works
1. **Initialize a job directory** to store all state and logs.
2. **Add files or directories** to the job database (file-level stateful setup).
3. **Analyze** source and destination volumes to gather file metadata.
4. **Compute checksums** for all files.
5. **Copy** only non-duplicate files from source to destination.
6. **Resume** interrupted or failed jobs safely.
7. **Verify** and audit all copy operations (shallow and deep verification).
8. **Import checksums** from old databases if needed.

## CLI Usage
All commands are run via Python (use the virtual environment if available):
```
.venv\Scripts\python.exe fs_copy_tool/main.py <command> [options]
```
Or, if installed as a package:
```
fs-copy-tool <command> [options]
```

### Main Commands & Options
- `init --job-dir <path>`
- `import-checksums --job-dir <path> --old-db <old_db_path> [--table <source_files|destination_files>]`
- `analyze --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...]`
- `checksum --job-dir <path> --table <source_files|destination_files> [--threads N] [--no-progress]`
- `copy --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...] [--threads N] [--no-progress] [--resume]`
- `resume --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...] [--threads N] [--no-progress]`
- `status --job-dir <path>`
- `log --job-dir <path>`
- `verify --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...] [--stage <shallow|deep>]`
- `deep-verify --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...]`
- `verify-status --job-dir <path>`
- `deep-verify-status --job-dir <path>`
- `verify-status-summary --job-dir <path>`
- `verify-status-full --job-dir <path>`
- `deep-verify-status-summary --job-dir <path>`
- `deep-verify-status-full --job-dir <path>`
- `add-file --job-dir <path> --file <file_path>`
- `add-source --job-dir <path> --src <src_dir>`
- `list-files --job-dir <path>`
- `remove-file --job-dir <path> --file <file_path>`

### Example Workflow
```
pip install -r requirements.txt
.venv\Scripts\python.exe fs_copy_tool/main.py init --job-dir .copy-task
.venv\Scripts\python.exe fs_copy_tool/main.py add-source --job-dir .copy-task --src <SRC_ROOT>
.venv\Scripts\python.exe fs_copy_tool/main.py analyze --job-dir .copy-task --src <SRC_ROOT> --dst <DST_ROOT>
.venv\Scripts\python.exe fs_copy_tool/main.py checksum --job-dir .copy-task --table source_files
.venv\Scripts\python.exe fs_copy_tool/main.py checksum --job-dir .copy-task --table destination_files
.venv\Scripts\python.exe fs_copy_tool/main.py copy --job-dir .copy-task --src <SRC_ROOT> --dst <DST_ROOT>
.venv\Scripts\python.exe fs_copy_tool/main.py status --job-dir .copy-task
.venv\Scripts\python.exe fs_copy_tool/main.py verify --job-dir .copy-task --src <SRC_ROOT> --dst <DST_ROOT>
.venv\Scripts\python.exe fs_copy_tool/main.py deep-verify --job-dir .copy-task --src <SRC_ROOT> --dst <DST_ROOT>
```

## Edge Cases & Robustness
- Skips already copied files (deduplication)
- Handles partial/incomplete copies and resumes them
- Reports but does not fix corrupted files
- All operations are auditable and stateful

## Testing
- Run all tests with `./scripts/test.ps1` (Windows) or `./scripts/test.sh` (Linux/macOS)
- Full E2E, integration, and unit test coverage for all features and edge cases
- See `docs/requirements-test.md` for detailed test protocols and scenarios

## Project Structure
- `fs_copy_tool/` — Main source code
- `tests/` — Automated tests
- `e2e_tests/` — End-to-end and integration tests
- `docs/` — Documentation
- `scripts/` — Automation scripts
- `Taskfile.yml` — Cross-platform automation tasks

## Requirements & Protocols
- See `docs/requirements.md` for full requirements and design
- See `docs/requirements-test.md` for test requirements
- See `docs/cli.md` for detailed CLI reference
- See `AGENTS.md` for agent workflow protocols

## Packaging & Installation
- Standard Python packaging via `setup.py` and `pyproject.toml`
- Install dependencies with `pip install -r requirements.txt`
- Install as a package: `pip install .`
- Entry point: `fs-copy-tool` (console script) or `python -m fs_copy_tool.main`

## License
MIT License
