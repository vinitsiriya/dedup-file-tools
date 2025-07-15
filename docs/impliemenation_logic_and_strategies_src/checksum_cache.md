# Implementation Logic and Strategies: checksum_cache.py

## Overview
`checksum_cache.py` implements a centralized, persistent cache for file checksums, enabling fast deduplication, verification, and resume operations. It is designed for robust, concurrent use in a multi-phase file copy workflow.

## Key Implementation Strategies

### 1. UID/Path Abstraction
- All cache operations use `UidPath` to convert absolute file paths to a (UID, relative_path) tuple.
- This ensures that checksums are system-independent and portable across different environments.

### 2. Database Schema and Access
- The cache is stored in a SQLite table (`checksum_cache`) keyed by (uid, relative_path).
- Each record includes file size, last modification time, checksum, timestamps, and a validity flag.
- All database access is performed using context managers to ensure connections are closed and transactions are atomic.

### 3. Get, Insert, and Update Logic
- `get(path)`: Looks up the most recent valid checksum for a file using its UID and relative path.
- `exists(checksum)`: Checks if a valid checksum exists anywhere in the cache.
- `insert_or_update(path, size, mtime, checksum)`: Inserts or updates a checksum record, marking it as valid and updating metadata.
- `get_or_compute(path)`: Returns a cached checksum if available; otherwise, computes it, updates the cache, and returns the value.

### 4. Compute-on-Miss and File Validation
- If a checksum is not found, the file is hashed using `compute_sha256` (from `fileops.py`).
- The cache is only updated if the file exists and is accessible.
- All file operations are robust to missing or inaccessible files.

### 5. Thread Safety and Concurrency
- Each method opens a new SQLite connection, ensuring thread safety for concurrent access.
- All operations are atomic and robust to database errors.

### 6. Integration
- The cache is used by all phases (analysis, copy, verify) for fast lookup and deduplication.
- It is always constructed with a reference to the job database and a `UidPath` instance.

---

# Checksum Cache Logic

## Overview
The `ChecksumCache` module provides a robust, auditable, and efficient mechanism for storing and retrieving file checksums. It is the only supported source for importing checksums from another job (via `import-checksums --other-db`).

## Features
- Stores SHA-256 checksums for all files in the job
- Used as the fallback source for checksums when main tables are missing a value
- All checksum operations (compute, verify, import) use the cache
- Importing checksums is only supported from another job's `checksum_cache` table
- All state is tracked in the job's SQLite database

## Importing Checksums
- Only `import-checksums --other-db` is supported (imports from another job's `checksum_cache` table)
- Imported checksums are used as a fallback when the main tables are missing a checksum
- Legacy/other import options are not supported

## Fallback Logic
- When a checksum is missing in the main tables, the cache is queried
- If not found in the cache, the checksum is computed and stored

## Error Handling
- All operations are logged for auditability
- Errors in import or fallback are reported and do not halt the job

## Example Usage
```
python -m fs_copy_tool.main import-checksums --job-dir .copy-task --other-db <OTHER_DB_PATH>
```

---

This document explains the implementation logic and strategies for `checksum_cache.py`, supporting maintainability and future enhancements.
