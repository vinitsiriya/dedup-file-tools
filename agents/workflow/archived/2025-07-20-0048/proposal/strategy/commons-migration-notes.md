# Commons Migration Notes



## Migration to dedup_file_tools_commons (Updated)
The following utility files must be moved from `dedup_file_tools_fs_copy/` to the new package `dedup_file_tools_commons`:

- `utils/uidpath.py` (system-independent file reference abstraction)
- `utils/checksum_cache.py` (centralized checksum cache logic)
- `utils/robust_sqlite.py` (robust SQLite connection handling)
- `utils/logging_config.py` (logging setup utility)
- `utils/fileops.py` (file operations: copy, verify, compute_sha256)
- `db.py` (database schema and initialization logic)

These files provide core abstractions and utilities required for both `dedup_file_tools_fs_copy` and `dedup_file_tools_dupes_move`.

**Migration Protocol:**
- Move the above files to `dedup_file_tools_commons` using a full-featured IDE (e.g., PyCharm), not the agent.
- Update all imports in both packages to use the new commons package paths.
- Test both packages after migration to ensure all references are correct and nothing is broken.
- Document all such moves and refactors in this file for audit and review.

## Implementation Pattern for New Tools
- The code structure for new deduplication tools should follow the modular, phase-based pattern used in `dedup_file_tools_fs_copy`:
  - Each major phase (analysis, copy/move, summary, verify) should be implemented in its own module (e.g., `phases/analysis.py`, `phases/copy.py`, etc.).
  - The main orchestration and CLI logic should reside in `main.py`.
  - All persistent state and job tracking should use the shared `db.py` logic from commons.
  - Utilities and helpers should be imported from `dedup_file_tools_commons`.
  - Logging, progress bars, and error handling should follow the conventions in the current codebase.
- This ensures consistency, maintainability, and auditability across all related tools.

## Observations from Existing Code
- All phases use robust, thread-safe database access via `RobustSqliteConn`.
- File and volume abstraction is handled via `UidPathUtil` for cross-platform compatibility.
- Progress bars (`tqdm`) and thread pools are used for efficient, user-friendly batch operations.
- Logging is always performed using the Python `logging` module, with log files stored in the job directory.
- The main script (`main.py`) coordinates all phases, sets up logging, and provides a CLI using `argparse`.
- The summary phase generates a CSV report of errors and pending files for audit and review.
- Verification phases support both shallow (metadata) and deep (checksum) verification, with results stored in the database.
- All code is designed to be resumable, idempotent, and auditable.

## Important Note for File Moves and Refactoring
- Whenever a file is moved to or updated in `dedup_file_tools_commons`, do NOT use the agent or automated scripts for the move/refactor.
- Always use a full-featured IDE (such as PyCharm) to perform the move/refactor, ensuring all references, imports, and usages are updated project-wide.
- This is required to avoid broken imports, missed references, and subtle bugs.
- After moving, update all dependent packages to use the new import paths.
- Document all such moves and refactors in this file for audit and review.
