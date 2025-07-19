# main.py and File Structure Notes

## main.py Overview
- `main.py` serves as the main orchestration script for the tool.
- It defines the CLI interface using `argparse`, supporting subcommands for all major operations (e.g., copy, verify, log, etc.).
- It sets up logging configuration and parses log level arguments.
- It initializes job directories and databases, ensuring all persistent state is managed via SQLite.
- It coordinates the workflow by invoking phase modules (e.g., analysis, copy, verify) and utility modules (e.g., uidpath, checksum_cache).
- It provides centralized error handling and logging for all CLI operations.
- It includes commands for audit log review and job status reporting.
- All CLI commands are designed to be resumable and idempotent.

## File Structure Conventions
- Each major phase of the workflow (analysis, copy, verify, summary) is implemented in its own module under a `phases/` subdirectory.
- Utility modules (e.g., `uidpath.py`, `checksum_cache.py`, `logging_config.py`) are placed under a `utils/` subdirectory for reuse and separation of concerns.
- Database logic is encapsulated in a dedicated `db.py` module.
- The package root contains an `__init__.py` for package initialization.
- All persistent state (job DBs, checksum caches) is stored in the job directory, not in memory.
- Tests are placed in a separate `tests/` directory, mirroring the source structure for easy coverage and maintenance.
- Documentation and workflow planning files are kept outside the source tree, under `docs/` and `agents/workflow/`.
- The codebase is organized for clarity, maintainability, and auditability, with clear separation between orchestration, phases, utilities, and persistent state.
