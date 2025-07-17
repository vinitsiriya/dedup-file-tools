# dedup_file_tools_fs_copy: File Structure and Responsibilities

## Overview
This document describes the file structure and responsibilities of the `dedup_file_tools_fs_copy` package, as well as the CLI structure and phase-based workflow. It is intended as a strategy reference for maintainers and contributors.

---

## Package Structure

```
dedup_file_tools_fs_copy/
├── __init__.py
├── main.py                # Main orchestration and CLI entry point
├── phases/
│   ├── __init__.py
│   ├── analysis.py        # Analysis phase: scans and indexes source/destination files
│   ├── copy.py            # Copy phase: deduplicated, resumable file copy logic
│   ├── verify.py          # Verification phase: shallow/deep integrity checks
│   └── summary.py         # Summary phase: reporting and CSV generation
├── utils/                 # (If present) CLI and workflow utilities
│   └── ...
```

### Key Files and Responsibilities
- **main.py**: Orchestrates the workflow, parses CLI arguments, and dispatches to phase handlers. Supports both one-shot and stepwise operation.
- **phases/analysis.py**: Scans source/destination roots, builds file index, and populates the database.
- **phases/copy.py**: Handles deduplicated file copying, status tracking, and error handling. Ensures resumability and auditability.
- **phases/verify.py**: Provides shallow (existence, size, mtime) and deep (checksum) verification of copied files. Results are stored for audit.
- **phases/summary.py**: Generates a summary report and CSV of errors or incomplete files for user review.
- **utils/**: Contains supporting utilities for CLI, config loading, and destination pool management.

---

## CLI Structure

The CLI is designed for both full workflow (one-shot) and granular phase control. Subcommands include:

- `generate-config`         : Interactive YAML config generator
- `init`                    : Initialize a new job directory
- `import-checksums`        : Import checksums from another database
- `analyze`                 : Analyze source/destination volumes
- `checksum`                : Update checksums for files
- `copy`                    : Copy files (deduplicated, resumable)
- `verify`                  : Shallow or deep verification
- `deep-verify`             : Deep verification (checksums)
- `summary`                 : Print summary and generate CSV report
- `add-file`/`add-source`   : Add files or directories to the job state
- `remove-file`             : Remove a file from the job state
- `list-files`              : List all files in the job state
- `status`                  : Show job progress and statistics
- `log`                     : Show job log or audit trail

### One-Shot Mode
The `one-shot` command runs the entire workflow in sequence:
1. `init`
2. `import-checksums` (optional)
3. `add-source`
4. `add-to-destination-index-pool`
5. `analyze`
6. `checksum` (source & destination)
7. `copy`
8. `verify` (shallow, then deep if requested)
9. `summary`

---

## Phase Responsibilities
- **Analysis**: Build file index, detect duplicates, and prepare for copy.
- **Copy**: Perform deduplicated, resumable file copy with status tracking.
- **Verify**: Ensure integrity of copied files (shallow: existence/size/mtime, deep: checksum).
- **Summary**: Report results, errors, and generate audit CSV.

---

## Extensibility
- The phase-based structure allows for easy addition of new phases or modification of existing ones.
- Utilities and shared logic should be placed in `dedup_file_tools_commons` for reuse across packages.

---

## References
- See `main.py` for orchestration logic and CLI argument definitions.
- See each `phases/*.py` file for phase-specific logic and documentation.
- See `README.md` for user-facing instructions.
