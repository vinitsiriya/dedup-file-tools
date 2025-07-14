# Strategy: Safe Migration to Centralized Checksum Cache

## 1. Schema Redesign
- Make `checksum_cache` the only table with checksums.
- Add `last_validated` and `last_updated` columns to `checksum_cache`.
- Remove `checksum` and `checksum_stale` from file tables.

## 2. Code Refactor
- Refactor all code to use the cache for checksum reads/writes.
- On file scan, check cache for (uid, path, size, mtime). If mismatch, recompute and update.
- All copy/verify logic must reference the cache.

## 3. Migration
- Write a migration script to move checksums from file tables to the cache.
- Remove old columns from file tables.
- Update all tests and fixtures.

## 4. Testing
- Add tests for cache invalidation (size/mtime/name change).
- Add migration and backward compatibility tests.
- Run full E2E and manual tests.

## 5. Documentation
- Update requirements, design docs, and migration instructions.
- Clearly mark as a breaking change and provide upgrade steps.

## Features Impacted by Centralized Checksum Cache (and Breaking Changes)

- **Block-wise file copying and SHA-256 checksums**: All checksum logic must use the cache; remove per-table checksums.
- **Deduplication (no redundant copies)**: Deduplication logic must reference the cache for all existence checks.
- **Stateful, file-level job setup**: All file state must reference the cache for checksum status.
- **CLI commands**: `checksum`, `copy`, `verify`, `deep-verify`, `import-checksums`, and all status/log commands must be refactored to use the cache.
- **Online verification (shallow/deep)**: All verification must use the cache for expected checksums, and cache must be invalidated if any of the following change for a file: size, last modified time (mtime), relative path (name), or UID (volume ID). All file identity attributes must be checked for cache validity. The cache table must include an explicit marker/flag (e.g., `is_stale` or `is_valid`) to indicate whether the cached checksum is currently valid or needs recomputation.
- **Import/export/migration**: All import/export logic must migrate checksums to/from the cache.
- **Resume, status, and logs**: All job state and logs must reference the cache for checksum status.
- **Manual and E2E tests**: All tests must be updated to use the cache and validate cache invalidation logic.

## Breaking Changes and Handling Strategy

- **Schema Change**: Remove `checksum` and `checksum_stale` from `source_files` and `destination_files`. Add `last_validated` and `last_updated` to `checksum_cache`.
- **Code Refactor**: All code paths (copy, verify, analyze, import, export, status, log) must use the cache for checksums. Remove all direct checksum logic from file tables.
- **Migration**: Provide a migration script to move all existing checksums into the cache and update the schema. Document the migration process and require users to run it before using the new version.
- **Backward Compatibility**: Clearly mark this as a breaking change. Old jobs must be migrated; fallback logic may be provided for a transition period.
- **Testing**: Add/extend tests for cache invalidation, migration, and all impacted features. Run full E2E and manual test suites.
- **Documentation**: Update all user and developer docs to reflect the new cache-centric model. Provide upgrade and troubleshooting instructions.

---

Status: Draft — Awaiting review and refinement.
