# checksum_cache.md - Requirements Documentation for checksum_cache.py

## Purpose
This module provides a centralized, persistent cache for file checksums, supporting fast deduplication, verification, and resume operations across all phases of the file copy workflow.

## Key Requirements

### 1. Centralized Checksum Storage
- The tool must store checksums for all files in a dedicated table in the job database.
- Each checksum record must be associated with a UID and relative path (from UidPath), file size, and last modification time.

### 2. UID/Path Abstraction
- All checksum operations must use UidPath for path conversion and resolution.
- The UID and relative path must be used as the primary key for cache lookups and updates.

### 3. Get, Insert, and Update
- The cache must support efficient retrieval of a checksum for a given file path.
- It must allow inserting or updating a checksum record, marking it as valid and updating metadata.
- The cache must support checking if a checksum exists and is valid.

### 4. Compute-on-Miss
- If a checksum is not found in the cache, the tool must compute it using a robust hash (e.g., SHA-256), update the cache, and return the value.
- The cache must only compute checksums for files that exist and are accessible.

### 5. Thread Safety and Performance
- The cache must be safe for concurrent access from multiple threads.
- All database operations must be atomic and robust to errors.

### 6. Testability
- The checksum cache must be unit- and integration-testable, with tests verifying correct storage, retrieval, and update of checksums.

---

# Requirements: Checksum Cache

## Overview
The checksum cache must provide a robust, auditable, and efficient mechanism for storing and retrieving file checksums. It is the only supported source for importing checksums from another job (via `import-checksums --other-db`).

## Requirements
- Store SHA-256 checksums for all files in the job
- Use as the fallback source for checksums when main tables are missing a value
- All checksum operations (compute, verify, import) must use the cache
- Importing checksums is only supported from another job's `checksum_cache` table
- All state must be tracked in the job's SQLite database

## Importing Checksums
- Only `import-checksums --other-db` is supported (imports from another job's `checksum_cache` table)
- Imported checksums are used as a fallback when the main tables are missing a checksum
- Legacy/other import options are not supported

## Fallback Logic
- When a checksum is missing in the main tables, the cache is queried
- If not found in the cache, the checksum is computed and stored

## Error Handling
- All operations must be logged for auditability
- Errors in import or fallback must be reported and must not halt the job

---

This document describes the requirements and design intent for `checksum_cache.py` in the file copy tool. Each requirement is traceable to a specific method or workflow step in the implementation.
