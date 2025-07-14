# User Story: Centralized Checksum Cache as Single Source of Truth

## Context
As a user, I want all checksum logic to use a single, centralized cache table, so that deduplication, verification, and all file operations are consistent, efficient, and robust against file changes.

## Scenario
- The cache table is the only source of truth for checksums.
- All file tables reference the cache for checksum lookups.
- The cache is invalidated if any file identity attribute (size, mtime, name, UID) changes.
- The cache table includes an explicit validity marker (e.g., `is_stale` or `is_valid`).
- All migration, CLI, and verification logic is updated to use the cache.

## Acceptance Criteria
- No file table stores its own checksum; all logic uses the cache.
- Cache is always validated and invalidated as required.
- All features (copy, verify, import, status, etc.) work as before or better.
- Migration and upgrade are documented and tested.

---

Linked requirement: requirement-20250714-centralized-checksum-cache.md
