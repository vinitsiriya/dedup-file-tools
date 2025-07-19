# Code Conventions, Libraries, and CLI Design

## Code Conventions
- All file operations and references use the `UidPath` abstraction for cross-platform compatibility and auditability.
- Block-wise (e.g., 4KB) reads are used for all checksum and file copy operations to avoid loading entire files into memory.
- All persistent state is stored in SQLite databases, never in memory.
- Logging is performed using the Python `logging` module, never `print`.
- All scripts and code must be cross-platform (Windows and Linux).
- The codebase must remain free of duplicate or obsolete files; refactor and consolidate logic as the project evolves.
- All Python scripts, tests, and automation use the Python interpreter from the `/.venv` virtual environment at the project root.
- All new features and bugfixes require tests in `tests/` mirroring the source structure.
- No lint/type errors are allowed in main branches; use `black`, `flake8`, and `mypy` for code quality.

## Libraries Used
- `pathlib` for all filesystem operations.
- `logging` for logging and audit trails.
- `sqlite3` (via `RobustSqliteConn`) for persistent state and job tracking.
- `tqdm` for progress bars in CLI operations.
- `argparse` for CLI argument parsing.
- `concurrent.futures.ThreadPoolExecutor` for parallel file operations.
- `wmi` (Windows only) for volume serial number detection.
- `subprocess` for system calls (e.g., `lsblk` on Linux).

## CLI Design
- All tools provide a CLI interface using `argparse`.
- CLI supports subcommands for major operations (e.g., `copy`, `verify`, `log`).
- CLI options include source/destination directories, job names, log level, dry-run, and summary output.
- All CLI commands are resumable and idempotent.
- CLI provides clear error messages and help output.
- CLI includes commands for audit log review and job status.
- All user-facing messages are clear, actionable, and avoid technical jargon where possible.
