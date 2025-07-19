# Implementation Details: dedup_file_tools_dupes_move

This document describes the implementation of the deduplication/removal workflow for the `dedup_file_tools_dupes_move` module, following the strict documentation agent protocol.

## Architecture
- Modular, phase-based CLI (see main.py, cli.py, handlers.py)
- Each phase (init, analyze, move, verify, summary, one-shot) is implemented as a handler
- SQLite database for job state, file metadata, and audit logs
- Utilities for checksums, file operations, and logging

## Workflow
1. **init**: Sets up a new deduplication job and database
2. **analyze**: Scans lookup pool, computes checksums, groups duplicates
3. **move**: Moves/removes duplicates to dupes folder
4. **verify**: Checks that moves/removals were successful
5. **summary**: Generates CSV report and prints summary
6. **one-shot**: Runs all phases in order

## Extensibility
- New phases can be added by implementing a handler and registering it in the CLI
- Database schema is designed for easy extension

## Auditability
- All actions are logged in the database and to log files
- Operations are idempotent and can be safely re-run

---

See requirements/features/dupes_move.md and feature/dupes_move.md for related docs.
