# Common Checksum DB Design: dedup_file_tools_commons

This document describes the schema and design of the shared checksum/index database used by all dedup-file-tools modules.

## Purpose
- Provide a single, robust, and reusable database for storing file checksums and related metadata.
- Enable fast lookup, deduplication, and validation across all tools and workflows.

## Schema

```
CREATE TABLE IF NOT EXISTS checksum_cache (
    uid TEXT,
    relative_path TEXT,
    size INTEGER,
    last_modified INTEGER,
    checksum TEXT,
    imported_at INTEGER,
    last_validated INTEGER,
    is_valid INTEGER DEFAULT 1, -- 1=valid, 0=stale
    PRIMARY KEY (uid, relative_path)
);
CREATE INDEX IF NOT EXISTS idx_checksum_cache_uid_relpath ON checksum_cache(uid, relative_path);
CREATE INDEX IF NOT EXISTS idx_checksum_cache_checksum_valid ON checksum_cache(checksum, is_valid);
```

## Table Description
- **checksum_cache:**
  - Stores the checksum and metadata for every file seen by any tool, indexed by UID and relative path.
  - Used for deduplication, validation, and fast comparison.

## Usage
- All modules (fs_copy, compare, dupes_move, etc.) should use this shared DB for checksum operations.
- The DB is typically named `checksum-cache.db` and located in the job directory.
- See `dedup_file_tools_commons/db.py` for schema and initialization code.

## References
- [Commons Utilities Structure](../docs/dedup_file_tools_commons/structure.md)
- [UidPath Abstraction](../docs/dedup_file_tools_commons/uidpath.md)

---

This design ensures a single source of truth for checksums and enables robust, cross-tool deduplication and validation.
