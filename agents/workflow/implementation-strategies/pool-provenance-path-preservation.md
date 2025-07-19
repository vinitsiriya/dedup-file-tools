# Implementation Strategy: Pool Provenance and Path Preservation

## 1. Database Schema Update

- Add a new column `pool_base_path TEXT` to the `dedup_files_pool` table.
- Migration: On upgrade, alter the table to add this column if it does not exist.

## 2. Analysis Phase (`phases/analysis.py`)

- When scanning files in `find_and_queue_duplicates`, for each file:
  - Compute the relative path to the provided `src_root` (which is the pool path).
  - Insert or update the row in `dedup_files_pool` with `pool_base_path=src_root`.
- Update the SQL insert to include the new column.

## 3. Move Phase (`phases/move.py`)

- When moving a file:
  - Query `dedup_files_pool` for the `pool_base_path` for the file’s `uid` and `relative_path`.
  - Compute the file’s path relative to its `pool_base_path`.
  - Move the file to `<removal_dir>/<relative_path_to_pool_base_path>`, preserving the directory structure.
- Update the move logic to use this computed relative path instead of just the filename.

## 4. CLI and Handler

- No changes to CLI arguments: `analyze` continues to take a single pool path.
- No changes to handler signatures, but update handler and phase code to support the new column and logic.

## 5. Tests

- Update or add tests to ensure:
  - The `pool_base_path` is correctly set for all files in the DB.
  - Files are moved to the correct relative path in the removal directory.
  - No collisions occur when files with the same name exist in different pools.

## 6. Migration/Backward Compatibility

- On upgrade, ensure the new column is added to existing databases.
- For legacy rows, if `pool_base_path` is missing, treat as an error or require re-analysis.

## 7. Documentation

- Update user and developer documentation to describe:
  - The meaning and use of `pool_base_path`.
  - The path preservation protocol when moving files.

---

**Summary Table**

| Step                | File(s)                | Change/Action                                                                 |
|---------------------|------------------------|-------------------------------------------------------------------------------|
| DB Schema           | db.py                  | Add `pool_base_path` column to `dedup_files_pool`                             |
| Analysis            | phases/analysis.py     | Set `pool_base_path` for each file during analysis                            |
| Move                | phases/move.py         | Use `pool_base_path` to compute and preserve relative path in removal dir     |
| CLI/Handlers        | main.py, handlers.py   | No CLI change; update handler/phase logic as needed                           |
| Tests               | tests/                 | Add/modify tests for provenance and path preservation                         |
| Migration           | db.py, docs/           | Add migration logic and document upgrade path                                 |

---
