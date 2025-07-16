# Granular Checklist: Copy Status Table Refactor

## 1. Schema & Migration
- [ ] Remove `copy_status`, `last_copy_attempt`, `error_message` from `source_files` and `destination_files` in schema (`fs_copy_tool/db.py`)
- [ ] Add new `copy_status` table with columns: `uid`, `relative_path`, `role`, `copy_status`, `last_copy_attempt`, `error_message`
- [ ] Update schema initialization and migration logic in `fs_copy_tool/db.py`
- [ ] Write migration script to move all status data from file tables to new table

## 2. Codebase Refactor (by file)

### A. `fs_copy_tool/main.py`
- [ ] Refactor all `INSERT INTO source_files`/`destination_files` to remove status fields
- [ ] Update all status field updates to use `copy_status` table
- [ ] Update all status queries (e.g., `SELECT ... WHERE copy_status=...`) to join/reference new table
- [ ] Update error/status reporting to use new table
- [ ] Update any CLI or argument logic that references status fields

### B. `fs_copy_tool/phases/copy.py`
- [ ] Refactor `reset_status_for_missing_files` to use new table for status
- [ ] Refactor `get_pending_copies` to select from new table
- [ ] Refactor `mark_copy_status` to update new table
- [ ] Update all status transitions and error handling to use new table

### C. `fs_copy_tool/phases/verify.py`
- [ ] Refactor all queries filtering by `copy_status` to join/reference new table
- [ ] Update all verification logic to use new table for status

### D. `fs_copy_tool/phases/summary.py`
- [ ] Refactor all queries and CSV output involving `copy_status` and `error_message` to use new table
- [ ] Update summary and reporting logic to use new table

### E. `fs_copy_tool/utils/checksum_cache.py`
- [ ] Refactor all queries involving `copy_status` in `destination_files` to use new table
- [ ] Update all logic that checks/filters by status in destination files

### F. Helper Functions
- [ ] Refactor any helper functions that read/write status to use new table
- [ ] Update all function signatures and docstrings as needed

### G. Indexes
- [ ] Update or remove any indexes on status fields in file tables

## 3. Tests (by file)
- [ ] Update all test DB setup to remove status fields from file tables
- [ ] Add creation of new `copy_status` table in test setup
- [ ] Insert status data into new table, not file tables
- [ ] Update all queries/assertions to reference new table (join as needed)
- [ ] Update all status/error checks to use new table
- [ ] Update all status changes (marking as done/pending/error) to update new table
- [ ] Add/extend tests to verify correct migration and status handling in new schema
- [ ] `tests/test_copy_with_destination_pool.py`
- [ ] `tests/test_cli_workflow_copy.py`
- [ ] `tests/test_summary.py`
- [ ] `tests/test_handle_resume.py`
- [ ] Any other test referencing status fields

## 4. Documentation
- [ ] Update all relevant documentation to reflect new schema and logic

## 5. Verification
- [ ] Verify all status logic for both `source` and `destination` roles
- [ ] Remove old status fields from codebase after migration and test updates
- [ ] Ensure all code and tests pass with new schema
