# Database Design Strategy for dedup_file_tools_dupes_move

## Context
This document proposes and explains the database schema for the deduplication move tool (`dedup_file_tools_dupes_move`). The schema is designed to support robust, auditable, and resumable duplicate file move operations, in line with project workflow protocols.

## Requirements
- Track all files considered for deduplication (with UID, relative path, size, mtime, checksum)
- Track move status for each file (pending, moved, error, etc.)
- Support error logging and auditability
- Enable efficient queries for duplicate detection and status
- Integrate with the shared checksum cache (in commons)
- Ensure checksum data is managed centrally by the shared schema and API in `dedup_file_tools_commons/db.py` and `checksum_cache.py`.

## Proposed Tables


### 1. dedup_files_pool
Tracks all files in the deduplication pool (candidates for move). No checksum data is stored in this database; all checksum logic is handled by the shared commons. Each file is identified by its volume UID and relative path, along with metadata such as size and last modified time.

```sql
CREATE TABLE dedup_files_pool (
    uid TEXT,
    relative_path TEXT,
    size INTEGER,
    last_modified INTEGER,
    PRIMARY KEY (uid, relative_path)
);
```


### 2. dedup_status
Tracks the move status and errors for each file. Each entry records the file's UID, relative path, current status (such as pending, moved, or error), error details if any, and the last update time.

```sql
CREATE TABLE dedup_status (
    uid TEXT,
    relative_path TEXT,
    status TEXT, -- e.g., 'pending', 'moved', 'error'
    error_message TEXT,
    updated_at INTEGER,
    PRIMARY KEY (uid, relative_path)
);
```

## Rationale
- File pool and status are separated for clarity and auditability.
- No checksum data is stored in the move tool database; all checksum logic is handled by commons for deduplication and integration.
- The schema is simple, flexible, and can be changed as requirements evolve.

## Open Questions / Feedback Needed
- Should move history (multiple attempts/errors per file) be tracked?
- Are additional fields needed for audit or integration?
- Is the separation of pool and status sufficient for all workflows?
- Is the current approach to checksum management (externalized in commons) sufficient for all move logic?

---

**Please review and suggest refinements or approval.**
