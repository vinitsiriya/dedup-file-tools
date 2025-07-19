# Implementation: dedup_file_tools_dupes_move

This document describes the implementation of the deduplication/removal tool, following the generic documentation protocol.

## Overview

The tool is implemented as a modular, phase-based CLI application in Python. It uses a SQLite database for tracking file operations and supports robust, auditable workflows for deduplication and removal.

## Key Components

- **CLI (cli.py, main.py):** Entry point for all operations, parses arguments, and dispatches to phase handlers.
- **Handlers/Phases:** Each phase (scan, move, verify, etc.) is implemented as a handler for extensibility.
- **Database (db.py):** Manages SQLite database for file metadata, operation status, and audit logs.
- **Utils:** Shared utilities for file operations, checksums, and logging.
- **Tests:** Comprehensive test suite in `tests/dedup_file_tools_dupes_move/`.

## Workflow

1. **Scan Phase:** Identifies duplicate files using checksums and metadata.
2. **Move Phase:** Moves or removes duplicates according to user rules.
3. **Verify Phase:** Confirms that operations were successful and data integrity is maintained.
4. **Rollback Phase:** Optionally reverts changes if needed.

## Extensibility

- New phases can be added by implementing a handler and registering it with the CLI.
- The database schema is designed for easy extension.

## Auditability

- All actions are logged in the database and to log files for traceability.
- Operations are idempotent and can be safely re-run.

---

See `requirements/requirements.md` and `features/feature_list.md` for requirements and features.
