# Implementation Guidelines: dedup_file_tools_dupes_move

## 1. Use UidPath for All File References
- Always convert absolute paths to (uid, relative_path) using `UidPathUtil`.
- Never operate on raw file paths for cross-platform compatibility.

## 2. Block-wise Checksum Calculation
- Use block-wise (e.g., 4KB) reads for all checksum operations.
- Never load entire files into memory.

## 3. Logging and Audit
- Use the Python `logging` module for all logs.
- Log every file move, error, and warning.
- Provide CLI options for log level and audit review.
- Persist all logs for later review.

## 4. CLI and User Experience
- Provide a CLI for specifying source and destination directories, dry-run, and summary output.
- Ensure all operations are resumable and idempotent.
- Never delete files automatically—only move duplicates.

## 5. Error Handling
- Handle missing files, permission errors, and checksum mismatches gracefully.
- Log all such events for auditability.

## 6. Testing
- Provide tests for all major code paths, including edge cases (e.g., symlinks, permission errors, large files).
- Use the same test and logging conventions as `dedup_file_tools_fs_copy`.
