## Related Document

For the design and schema of the shared checksum/index database used by all modules, see:

- [Common Checksum DB Design](strategy-20250721-commons-db.md)
# Database Design: dedup_file_tools_compare

This document outlines the recommended SQLite schema for the `dedup_file_tools_compare` module, inspired by the design of `dedup_file_tools_fs_copy`.

## Goals
- Track files in left and right pools with UID and relative path abstraction
- Store comparison results (identical, different, unique)
- Support resumable, auditable, and efficient comparison workflows

## Schema

```
-- Pool tables (no checksum column; checksums are managed in commons db)
CREATE TABLE IF NOT EXISTS left_pool_files (
    uid TEXT,
    relative_path TEXT,
    last_modified INTEGER,
    size INTEGER,
    PRIMARY KEY (uid, relative_path)
);

CREATE TABLE IF NOT EXISTS right_pool_files (
    uid TEXT,
    relative_path TEXT,
    last_modified INTEGER,
    size INTEGER,
    PRIMARY KEY (uid, relative_path)
);

-- Comparison results: files missing from right (present in left, not in right)
CREATE TABLE IF NOT EXISTS compare_results_right_missing (
    uid TEXT,
    relative_path TEXT,
    last_modified INTEGER,
    size INTEGER,
    PRIMARY KEY (uid, relative_path)
);

-- Comparison results: files missing from left (present in right, not in left)
CREATE TABLE IF NOT EXISTS compare_results_left_missing (
    uid TEXT,
    relative_path TEXT,
    last_modified INTEGER,
    size INTEGER,
    PRIMARY KEY (uid, relative_path)
);

CREATE INDEX IF NOT EXISTS idx_left_pool_uid_relpath ON left_pool_files(uid, relative_path);
CREATE INDEX IF NOT EXISTS idx_right_pool_uid_relpath ON right_pool_files(uid, relative_path);
CREATE INDEX IF NOT EXISTS idx_right_missing_uid_relpath ON compare_results_right_missing(uid, relative_path);
CREATE INDEX IF NOT EXISTS idx_left_missing_uid_relpath ON compare_results_left_missing(uid, relative_path);
```

## Table Descriptions
- **left_pool_files / right_pool_files:**
  - Store all files discovered in the left/right directory pools, with UID, relative path, size, and mtime. No checksum column; checksums are managed in the commons checksum db.
- **compare_results_right_missing:**
  - Files present in left pool but missing from right pool.
- **compare_results_left_missing:**
  - Files present in right pool but missing from left pool.

## Notes
- All file references use the UID/relative path abstraction for portability (see UidPath docs).
- Checksums and index work are handled by the shared commons db (`dedup_file_tools_commons`).
- The schema is designed for extensibility (future: multi-way compare, metadata, audit logs).
- All operations should be resumable and auditable, with clear status tracking.

---

This schema provides a robust, auditable foundation for file pool comparison workflows in dedup_file_tools_compare.
