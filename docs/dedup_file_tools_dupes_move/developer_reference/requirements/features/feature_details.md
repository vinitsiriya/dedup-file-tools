# Feature Details: dedup_file_tools_dupes_move

This document provides detailed descriptions of each feature listed in `feature_list.md`.

## Modular, phase-based CLI
- The CLI is organized into distinct phases (e.g., scan, move, verify), each with its own handler and options.
- Supports chaining of phases and custom workflows.

## SQLite-backed database
- All file operations, statuses, and metadata are tracked in a local SQLite database for auditability and recovery.

## Robust duplicate detection and move/removal logic
- Uses checksums and file metadata to identify duplicates.
- Moves or removes duplicates according to user-specified rules.

## Auditable, idempotent operations
- All actions are logged and can be safely re-run without data loss or duplication.
- Supports dry-run and rollback for safe operation.

## Handler/phase structure
- Each phase is implemented as a handler, allowing for easy extension and maintenance.
- New phases can be added with minimal changes to the CLI.

## Comprehensive test suite
- Unit and integration tests cover all phases, CLI options, and edge cases.
- Tests are located in `tests/dedup_file_tools_dupes_move/`.

## Protocol-driven documentation
- Documentation is generated and updated according to a strict protocol, ensuring consistency and completeness.

## Support for dry-run, verify, and rollback
- Users can preview actions, verify results, and roll back changes as needed.

## Agent-based documentation update workflows
- Documentation updates are managed by autonomous agents following the project protocol.

---

For requirements mapping, see `../requirements.md`.
