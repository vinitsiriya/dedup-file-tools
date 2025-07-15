# Proposal: Single Source of Truth for Checksums via Centralized Cache Table

## Purpose
Migrate to a model where the `checksum_cache` table is the only source of truth for file checksums. All other tables (e.g., `source_files`, `destination_files`) reference this cache for checksums, and do not store their own checksum columns. This ensures consistency, reduces duplication, and simplifies invalidation logic.

## Key Changes
- Remove `checksum` and `checksum_stale` columns from `source_files` and `destination_files`.
- All checksum lookups and updates go through the `checksum_cache` table, keyed only by `(uid, relative_path)`.
- The cache table has no `source` or per-table fields; it is a single, global cache for all files.
- All code uses a single `ChecksumCache` class (with `UidPath`) for all cache access, lookup, update, and cache-miss handling.
- When using a cached checksum, always validate by checking file size and last modified time. Invalidate and recompute if any of these change.
- All copy, verify, and analysis logic must reference the cache, not local columns.
- The tool is responsible for updating the checksum_cache table on the go, ensuring it always reflects the latest valid checksums for all files.
- Only the storage location and access method for checksums changes; all deduplication, verification, and copy logic is routed through the cache interface.

## Migration & Compatibility
- Write a migration script to move all existing checksums into the cache and remove checksum columns from file tables.
- Update all code paths and tests to use the cache interface.
- Provide clear upgrade instructions for users.

## Risks
- Breaking change: All jobs and databases must be migrated.
- All code and tests must be updated to avoid logic errors.

## Status
Final — Implemented and in use as of 2025-07-15.
