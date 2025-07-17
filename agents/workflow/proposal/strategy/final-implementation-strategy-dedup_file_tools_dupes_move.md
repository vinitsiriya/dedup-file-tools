# Final Implementation Strategy: dedup_file_tools_dupes_move

## 1. Package Structure
- Create a new package directory: `dedup_file_tools_dupes_move/`.
- Add `__init__.py`, `cli.py`, and main logic modules (e.g., `dupes_finder.py`, `move_dupes.py`).
- Add a `utils/` subdirectory for any package-specific helpers.
- Add a `tests/` directory mirroring the package structure for unit and integration tests.

## 2. Commons Migration
- Identify common utilities (e.g., `uidpath.py`, logging, checksum helpers) and move them to `dedup_file_tools_commons` using an IDE (not the agent).
- Update imports in both `dedup_file_tools_fs_copy` and `dedup_file_tools_dupes_move` to use the new commons package.

## 3. Core Logic
- Implement a recursive directory scan to collect all files under the user-specified root.
- For each file, compute its checksum using block-wise reads (reuse commons logic).
- Group files by checksum; identify groups with more than one file as duplicates.
- For each duplicate group, select one file to keep in place; mark others for moving.
- For each file to move:
  - Compute the destination path under the user-specified directory, preserving relative structure if required.
  - Before moving, check if the destination already contains a file with the same checksum; if so, skip move and log.
  - Move the file using atomic operations where possible.
  - Log every move, skip, and error.
- Support a dry-run mode that logs intended actions without making changes.
- Ensure all operations are resumable and idempotent (e.g., by maintaining a move log or state DB).

## 4. CLI Design
- Implement a CLI in `cli.py` using `argparse`.
- Support options for source directory, destination directory, dry-run, log level, and summary output.
- Provide subcommands for finding duplicates, moving duplicates, and reviewing logs/audit trails.
- Ensure CLI is user-friendly, with clear help and error messages.

## 5. Logging and Audit
- Use the Python `logging` module for all logs.
- Log all actions, errors, and warnings to a persistent log file in the job directory.
- Provide a CLI command to review logs and audit trails.

## 6. Testing
- Write unit tests for all major logic components (checksum, grouping, move logic, CLI parsing).
- Write integration tests for end-to-end scenarios (including dry-run, error handling, and resumability).
- Ensure tests cover edge cases (symlinks, permission errors, large files, etc.).

## 7. Documentation
- Update all relevant documentation files in `docs/` and strategy notes.
- Document CLI usage, configuration, and audit/review procedures.

## 8. Review and Refactor
- Perform code reviews using the code review notes and agent protocol.
- Refactor as needed for clarity, maintainability, and auditability.
- Archive planning and strategy files as per workflow protocol after completion.
