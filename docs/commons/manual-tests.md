# Manual Tests Documentation

## Purpose
Manual tests are used for interactive or exploratory testing, especially for scenarios not easily automated.


## Location & Organization
- Manual test scripts: `manual_tests/<package>/` (each package/module gets its own subdirectory, e.g., `manual_tests/dedup_file_tools_dupes_move/`, `manual_tests/dedup_file_tools_fs_copy/`)
- Each scenario should be in its own subdirectory under the relevant package/module.
- Fixture generator for manual tests: `scripts/generate_fixtures_manual.py`
- **All manual test operations should be performed in the `.temp/manual_tests/<package>/` directory to avoid polluting the main workspace.**

## How to Run
- On Windows, run the relevant script in `manual_tests/<scenario>/` in PowerShell.
- Use `generate_fixtures_manual.py` to create custom test directories and files in the appropriate workspace (e.g., `.temp/manual_tests/<scenario>`).

## Architecture Note (2025-07)
- All job databases are now named `<job-name>.db` in the job directory. All CLI commands require `--job-name`.
- The checksum cache database is always named `checksum-cache.db` in the job directory.


## Guidelines
- Organize manual tests by package/module for clarity and scalability.
- Use manual tests to verify UI/CLI feedback, logging, and edge cases.
- Record observations and issues in the appropriate planning or log files.
- Use manual tests to validate new features before automating them.
- Always perform manual test operations in the `.temp/manual_tests/<package>/` directory.


## Extending
- Add new manual test scripts in the appropriate `manual_tests/<package>/` directory for each scenario as needed.
- Document manual test procedures and expected outcomes in this file or in the planning docs.

## Stateful CLI Manual Testing
- Manually test the new file-level stateful CLI commands:
  - `add-file`, `add-source`, `list-files`, `remove-file`
- Verify incremental job setup, file addition/removal, and correct operation of all phases after stateful setup.
- Directory-level state is not supported; manual tests must operate at the file level.


## Destination Pool Manual Test Scenarios

### 1. Pool Index Creation and Update
- Create a destination directory with several files.
- Run `add-to-destination-index-pool` to scan and index all files.
- Add, modify, or remove files in the destination and rerun the command to verify updates.
- Check the database to confirm the `destination_pool_files` table is accurate.

### 2. Pool Deduplication During Copy
- Create a source directory with files, some of which are already present in the destination.
- Run the full workflow: `init`, `analyze`, `checksum`, `add-to-destination-index-pool`, then `copy`.
- Verify that files already present in the pool are skipped and only new files are copied.
- Check CLI/log output and database for correct deduplication behavior.

### 3. Pool Index Resilience
- Interrupt the pool scan or copy operation and resume.
- Verify that the pool index and deduplication remain correct and idempotent.

### 4. Edge Cases
- Test with large files, deeply nested directories, and files with special characters in the destination.
- Verify that the pool index and deduplication logic handle all cases robustly.


### 5. Manual Database Inspection
- Use a SQLite browser to inspect the relevant tables (e.g., `destination_pool_files`, `dedup_files_pool`, etc.) after each operation.
- Confirm that all expected files are indexed and deduplication logic is correct.

---
To add more scenarios, copy and adapt scripts in the appropriate `manual_tests/<package>/` directory.
