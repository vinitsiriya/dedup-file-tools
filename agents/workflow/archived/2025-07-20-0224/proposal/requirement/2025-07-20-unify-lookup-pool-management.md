# Requirement Proposal: Unified and Auditable Lookup Pool Management

## Problem Statement

- The current deduplication workflow does not track the provenance of files when analyzing multiple pools.
- There is no way to audit or report which pool a file originated from after deduplication.
- Directory structure is not always preserved when moving duplicates, risking collisions and loss of provenance.

## Solution Overview

- The `analyze` command remains the only way to scan a pool. It takes a single pool path as input.
- The `dedup_files_pool` table will be extended with a new column: `pool_base_path TEXT`.
- For every file scanned during analysis, the `pool_base_path` column will be set to the pool path provided to `analyze`.
- When moving duplicates to the removal directory, the tool will preserve the relative path from the file's `pool_base_path`, mirroring the original directory structure in the removal directory.

## Implementation Details

### Database Schema

```sql
CREATE TABLE IF NOT EXISTS dedup_files_pool (
    uid TEXT,
    relative_path TEXT,
    size INTEGER,
    last_modified INTEGER,
    checksum TEXT,
    scanned_at INTEGER,
    pool_base_path TEXT,  -- denotes the pool path for this file
    PRIMARY KEY (uid, relative_path)
);
```

### Workflow

1. `init` — Create a new job.
2. `analyze --job-dir ... --job-name ... --lookup-pool /path/to/folder1`
3. `analyze --job-dir ... --job-name ... --lookup-pool /path/to/folder2`
4. Continue with `move`, `verify`, etc.

- Each call to `analyze` scans the specified pool and records the pool path for every file.
- All deduplication and reporting is performed globally across all files in `dedup_files_pool`.

### Moving Duplicates

- When moving duplicates, the tool will preserve the relative path to `pool_base_path` in the removal directory.
- This ensures no collisions, full auditability, and easy restoration if needed.

### Moving Duplicates: Path Preservation Protocol

- When a duplicate file is moved to the removal directory (dupes folder), its relative path with respect to its `pool_base_path` will be preserved.
- This means:
  - If a file was originally at `<pool_base_path>/subdir1/file.txt`, it will be moved to `<removal_dir>/subdir1/file.txt`.
  - The full directory structure under each pool is mirrored inside the removal directory.
- This guarantees:
  - No collisions between files with the same name from different pools.
  - Full traceability and auditability of file origins after deduplication.
  - The removal directory is organized and mirrors the original pool structure for easy review or restoration.
- This protocol is mandatory for all move operations in the deduplication workflow.

## Benefits

- Full auditability and provenance tracking for every file.
- No risk of file collisions when moving duplicates.
- Simple, extensible, and protocol-compliant workflow.

---

**Status:** _Draft for review. Please provide feedback or approval._
