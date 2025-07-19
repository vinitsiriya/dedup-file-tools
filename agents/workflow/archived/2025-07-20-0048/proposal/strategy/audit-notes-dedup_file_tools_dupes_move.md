# Audit Notes: dedup_file_tools_dupes_move

## Key Audit Points

- All file identification and movement must use `UidPath` abstraction for cross-platform correctness and auditability.
- Only `UidPath` should interpret or manipulate `rel_path`; treat it as opaque elsewhere (see `utils/uidpath.py`).
- The format of `relative_path` is only guaranteed to be relative to the detected mount point. It may appear absolute in some environments (e.g., tests/temp dirs).
- All checksum operations, mismatches, and errors must be logged for auditability (see `utils/checksum_cache.py`).
- All file move operations must be logged with sufficient detail for traceability (see `phases/copy.py`).
- CLI must provide options for log level and audit review (see `main.py`).
- Log when no duplicates are found or when verification steps are skipped (see `phases/verify.py`).
- All actions, errors, and warnings must use the Python `logging` module, not `print`.
- The tool must provide a CLI command for showing job logs or audit trails.
- All audit logs must be persistent and reviewable after execution.

## Files to Reference
- `utils/uidpath.py`
- `main.py`
- `utils/checksum_cache.py`
- `phases/verify.py`
- `phases/copy.py`
