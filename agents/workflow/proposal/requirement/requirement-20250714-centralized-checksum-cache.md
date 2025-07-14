# Proposal: Single Source of Truth for Checksums via Centralized Cache Table

## Purpose
Migrate to a model where the `checksum_cache` table is the only source of truth for file checksums. All other tables (e.g., `source_files`, `destination_files`) will reference this cache for checksums, and will not store their own checksum columns. This ensures consistency, reduces duplication, and simplifies invalidation logic.

## Key Changes
- Remove `checksum` and `checksum_stale` columns from `source_files` and `destination_files`.
- All checksum lookups and updates go through the `checksum_cache` table.
- Add `last_validated` and `last_updated` columns to `checksum_cache` to track freshness and cache state.
- When using a cached checksum, always validate by checking file size, name, and last modified time. Invalidate and recompute if any of these change.
- All copy, verify, and analysis logic must reference the cache, not local columns.

## Migration & Compatibility
- Write a migration script to move all existing checksums into the cache and remove checksum columns from file tables.
- Update all code paths and tests to use the cache.
- Provide clear upgrade instructions for users.

## Risks
- Breaking change: All jobs and databases must be migrated.
- All code and tests must be updated to avoid logic errors.

## Status
Draft — Awaiting review and refinement.
