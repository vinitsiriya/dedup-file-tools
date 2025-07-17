# dedup_file_tools_dupes_move: File Structure and Responsibilities

## Overview
This document outlines the intended file structure, responsibilities, and CLI/phase workflow for the `dedup_file_tools_dupes_move` package. This package is designed to identify and move duplicate files across specified locations, supporting auditability, resumability, and integration with the commons utilities.

---

## Package Structure (Planned)

```
dedup_file_tools_dupes_move/
├── __init__.py
├── main.py                # Main orchestration and CLI entry point for duplicate move operations
├── phases/
│   ├── __init__.py
│   ├── analysis.py        # Analysis phase: scans for duplicates, builds index
│   ├── move.py            # Move phase: moves duplicates to target location(s), tracks status
│   ├── verify.py          # Verification phase: ensures duplicates were moved as intended
│   └── summary.py         # Summary phase: reporting and CSV generation
├── utils/                 # (If present) CLI and workflow utilities
│   └── ...
```

### Key Files and Responsibilities
- **main.py**: Orchestrates the duplicate move workflow, parses CLI arguments, and dispatches to phase handlers. Supports both one-shot and stepwise operation.
- **phases/analysis.py**: Scans input locations, identifies duplicate files, and populates the database with candidates for moving.
- **phases/move.py**: Handles the actual moving of duplicate files, status tracking, error handling, and ensures resumability.
- **phases/verify.py**: Verifies that duplicates have been moved correctly (existence, absence at source, presence at destination, etc.).
- **phases/summary.py**: Generates a summary report and CSV of moved, pending, or error files for audit and review.
- **utils/**: Contains supporting utilities for CLI, config loading, and move logic.

---

## CLI Structure (Planned)

The CLI will mirror the phase-based design of the copy tool, with subcommands for each phase and utility:

- `generate-config`         : Interactive YAML config generator
- `init`                    : Initialize a new job directory
- `analyze`                 : Analyze input locations for duplicates
- `move`                    : Move duplicate files to target location(s)
- `verify`                  : Verify that duplicates were moved as intended
- `summary`                 : Print summary and generate CSV report
- `add-file`/`add-source`   : Add files or directories to the job state
- `remove-file`             : Remove a file from the job state
- `list-files`              : List all files in the job state
- `status`                  : Show job progress and statistics
- `log`                     : Show job log or audit trail

### One-Shot Mode
The `one-shot` command will run the entire workflow in sequence:
1. `init`
2. `add-source`
3. `analyze`
4. `move`
5. `verify`
6. `summary`

---

## Phase Responsibilities
- **Analysis**: Identify duplicate files and build a move plan.
- **Move**: Move duplicates to the designated location(s), update status, and handle errors.
- **Verify**: Ensure that duplicates have been moved and are absent from their original locations.
- **Summary**: Report results, errors, and generate audit CSV.

---

## Extensibility
- The phase-based structure allows for easy addition of new phases or modification of existing ones.
- Utilities and shared logic should be placed in `dedup_file_tools_commons` for reuse across packages.

---

## References
- See `main.py` (to be implemented) for orchestration logic and CLI argument definitions.
- See each `phases/*.py` file (to be implemented) for phase-specific logic and documentation.
- See `README.md` for user-facing instructions (to be updated).
