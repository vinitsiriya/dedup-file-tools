# References to `source_files` and `destination_files` Tables

This file lists all locations in the codebase (including tests and docs) where the tables `source_files` or `destination_files` are referenced. Use this as a guide for refactoring and migration.

---

## Code References

- `fs_copy_tool/db.py`
  - Table creation and index definitions for both tables.
- `fs_copy_tool/utils/checksum_cache.py`
  - Comments, queries, and logic referencing `destination_files` (e.g., status checks, joins).
- `fs_copy_tool/main.py`
  - All file insertions, status queries, CLI argument handling, and status/error reporting for both tables.
- `fs_copy_tool/phases/copy.py`
  - All status selection, update, and error handling logic for `source_files` and `destination_files`.
- `fs_copy_tool/phases/verify.py`
  - All queries filtering by status in `source_files`.
- `fs_copy_tool/phases/summary.py`
  - All queries and CSV output involving `source_files`.

## Test References

- `tests/test_copy_with_destination_pool.py`
  - CLI argument usage, status queries, and assertions for both tables.
- `tests/test_cli_workflow_copy.py`
  - CLI argument usage, status queries, and assertions for `source_files`.
- `tests/test_cli_workflow_verify_shallow.py`
  - CLI argument usage for `source_files`.
- `tests/test_summary.py`
  - Table creation, inserts, and queries for `source_files`.
- `tests/test_handle_resume.py`
  - Status updates and queries for `source_files`.
- Any other test referencing these tables or their status fields.

## Documentation References

- `docs/cli.md`, `docs/external_ai_tool_doc.md`, `docs/requirements.md`, `README.md`
  - Usage examples, CLI documentation, and requirements sections referencing these tables.

## Proposal/Strategy/Checklist References

- All proposal, strategy, and checklist markdown files for the copy status table refactor reference these tables in requirements, migration, and implementation steps.

---

**Note:** This list is based on a search for all direct references to `source_files` and `destination_files`. For each location, review the context to determine if it needs to be updated for the new `copy_status` table or for schema normalization.
