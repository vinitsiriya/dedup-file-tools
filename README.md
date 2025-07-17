# fs-copy-tool

Safely copy media files (photos, videos) from a source HDD pool to a destination HDD pool, ensuring **no redundant (duplicate) files** at the destination. The tool is robust, resumable, and fully auditable, using an SQLite database for all state and supporting both fixed and removable drives.

---

## Features
- Block-wise (4KB) file copying and SHA-256 checksums
- No file is copied if its checksum already exists in the destination (deduplication)
- All state, logs, and planning files are stored in a dedicated job directory
- Fully resumable and idempotent: safely interrupt and resume at any time
- **Stateful, file-level job setup:**
  - `add-file` — Add a single file to the job state/database
  - `remove-file` — Remove a file from the job state/database
- CLI commands for all phases: `init`, `analyze`, `import-checksums`, `checksum`, `copy`, `resume`, `status`, `log`, `verify`, `deep-verify`, and more
- **One-Shot Command:** Run the entire workflow in a single step with `one-shot` (see Quick Start)
- **YAML Config Support:** Use `-c <config.yaml>` to load all CLI options from a YAML file for any command. CLI args override YAML values. See CLI docs for details.
- Verification and audit commands: `verify`, `deep-verify`, `verify-status`, `deep-verify-status`, `verify-status-summary`, `verify-status-full`, `deep-verify-status-summary`, `deep-verify-status-full`, `status`, `log`
- Handles edge cases: partial/incomplete copies, missing files, already copied files, corrupted files (reports errors, does not fix)
- Cross-platform: Windows & Linux
- Full test suite for all features, edge cases, and workflows

---


## Quick Start

### 1. Install Requirements
```
pip install -r requirements.txt
```




### 2. One-Shot Workflow (Recommended)
Run the entire workflow (init, import, add-source, analyze, checksum, copy, verify, summary) in a single command:
```
python -m fs_copy_tool.main one-shot --job-dir .copy-task --job-name <job-name> --src <SRC_ROOT> --dst <DST_ROOT> [options]
```
Or, use a YAML config file for all options:
```
python -m fs_copy_tool.main one-shot -c config.yaml
```
*All CLI options can be set in the YAML file. CLI args override YAML values. See CLI docs for YAML format and details.*

#### Generate a Config File Interactively
To create a YAML config file interactively, run:
```
python -m fs_copy_tool generate-config
```
Follow the prompts to generate a config file for use with `-c`.

**If any step fails, the workflow will stop immediately and print an error. On success, "Done" is printed.**

### 3. Manual (Step-by-Step) Workflow

#### a. Initialize Job Directory
```
python -m fs_copy_tool.main init --job-dir .copy-task --job-name <job-name>
```

#### b. Add Files or Sources to the Job
# Add a single file:
python -m fs_copy_tool.main add-file --job-dir .copy-task --job-name <job-name> --file <FILE_PATH>
# Add all files from a directory:
python -m fs_copy_tool.main add-source --job-dir .copy-task --job-name <job-name> --src <SRC_ROOT>
# List all files in the job:
python -m fs_copy_tool.main list-files --job-dir .copy-task --job-name <job-name>
# Remove a file from the job:
python -m fs_copy_tool.main remove-file --job-dir .copy-task --job-name <job-name> --file <FILE_PATH>

#### c. Analyze Source and Destination Volumes
```
python -m fs_copy_tool.main analyze --job-dir .copy-task --job-name <job-name> --src <SRC_ROOT> --dst <DST_ROOT>
```

#### d. Compute Checksums
```
python -m fs_copy_tool.main checksum --job-dir .copy-task --job-name <job-name> --table source_files
python -m fs_copy_tool.main checksum --job-dir .copy-task --job-name <job-name> --table destination_files
```

#### e. Copy Non-Redundant Files (with Destination Pool Validation)
```
python -m fs_copy_tool.main copy --job-dir .copy-task --job-name <job-name> --src <SRC_ROOT> --dst <DST_ROOT>
```
*Before copying, the tool will update and validate all destination pool checksums with a progress bar to ensure deduplication is accurate and up to date.*

---

## Important Architecture Notes (2025-07)

- All job databases are now named `<job-name>.db` in the job directory. You must specify `--job-name` for all CLI commands that operate on a job.
- The checksum cache database is always named `checksum-cache.db` in the job directory.
- All CLI usage examples must include `--job-name <job-name>`.
- The tool will not operate on legacy `copytool.db` files; migrate or re-initialize jobs as needed.

### 7. Resume, Status, and Logs
```
python -m fs_copy_tool.main resume --job-dir .copy-task --src <SRC_ROOT> --dst <DST_ROOT>
python -m fs_copy_tool.main status --job-dir .copy-task
python -m fs_copy_tool.main log --job-dir .copy-task
```

### 8. Verification and Audit
```
python -m fs_copy_tool.main verify --job-dir .copy-task --src <SRC_ROOT> --dst <DST_ROOT> [--stage shallow|deep]
python -m fs_copy_tool.main deep-verify --job-dir .copy-task --src <SRC_ROOT> --dst <DST_ROOT>
python -m fs_copy_tool.main verify-status --job-dir .copy-task
python -m fs_copy_tool.main deep-verify-status --job-dir .copy-task
python -m fs_copy_tool.main verify-status-summary --job-dir .copy-task
python -m fs_copy_tool.main verify-status-full --job-dir .copy-task
python -m fs_copy_tool.main deep-verify-status-summary --job-dir .copy-task
python -m fs_copy_tool.main deep-verify-status-full --job-dir .copy-task
```

### 9. Import Checksums from Another Job (Current, 2025-07-15)
```
python -m fs_copy_tool.main import-checksums --job-dir .copy-task --other-db <OTHER_DB_PATH>
```

---


## CLI Commands
- `generate-config` — Interactively generate a YAML config file for use with `-c`
- `init --job-dir <path>` — Create and initialize a job directory
- `import-checksums --job-dir <path> --other-db <other_db_path>` — Import checksums from another job's checksum_cache table
- `analyze --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...]` — Scan source/destination and update the database
- `checksum --job-dir <path> --table <source_files|destination_files> [--threads N] [--no-progress]` — Compute missing/stale checksums
- `copy --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...] [--threads N] [--no-progress] [--resume]` — Before copying, updates and validates all destination pool checksums with a progress bar, then copies only non-duplicate files
- `resume --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...] [--threads N] [--no-progress]` — Resume incomplete/failed operations
- `status --job-dir <path>` — Show job progress and statistics
- `log --job-dir <path>` — Output a log or audit trail
- `verify --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...] [--stage shallow|deep]` — Shallow/deep verification of copied files
- `deep-verify --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...]` — Deep verify: compare checksums
- `verify-status --job-dir <path>` — Show shallow verification results
- `deep-verify-status --job-dir <path>` — Show deep verification results
- `verify-status-summary --job-dir <path>` — Show short summary of shallow verification
- `verify-status-full --job-dir <path>` — Show all shallow verification results
- `deep-verify-status-summary --job-dir <path>` — Show short summary of deep verification
- `deep-verify-status-full --job-dir <path>` — Show all deep verification results
- `add-file --job-dir <path> --file <file_path>` — Add a single file to the job state/database
- `add-source --job-dir <path> --src <src_dir>` — Recursively add all files from a directory
- `list-files --job-dir <path>` — List all files in the job state/database
- `remove-file --job-dir <path> --file <file_path>` — Remove a file from the job state/database

---

## CLI Documentation

See [docs/cli.md](docs/cli.md) for complete CLI command reference, usage examples, and best practices.

---

## Testing
Run all tests (Windows PowerShell):
```
./scripts/test.ps1
```
Or (Linux/macOS):
```
./scripts/test.sh
```

---

## Project Structure
- `fs-copy-tool/` — Main source code
- `tests/` — Automated tests (pytest)
- `e2e_tests/` — End-to-end and integration tests
- `agents/` — Agent planning, memory, and reasoning
- `changes/` — Execution logs and persistent state
- `scripts/` — Automation scripts for testing, linting, formatting, and archival
- `Taskfile.yml` — Cross-platform automation tasks

---

## Requirements & Design
See `requirements.md` and `requirements-test.md` for full requirements, design, and test protocols. See `AGENTS.md` for agent workflow protocols.

---

## License
MIT License
