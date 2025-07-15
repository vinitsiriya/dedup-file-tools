# Task: Implement Centralized Checksum Cache

## Steps
1. Redesign schema: make cache the only checksum store, keyed by (uid, relative_path), remove per-table checksums and all source fields.
2. Refactor all code paths (copy, verify, analyze, import, export, status, log) to use the cache interface (`ChecksumCache` with `UidPath`).
3. Write migration script for existing jobs/databases.
4. Update all tests and fixtures.
5. Document migration and upgrade process.
6. Run full E2E and manual test suites.

## Expected Results
- All features work as before or better, using the cache interface.
- Migration is safe and documented.
- All tests pass.
- The tool must update the checksum_cache table on the go, so it always reflects the latest valid checksums for all files as they are processed.
- Only the storage location and access method for checksums changes; the deduplication, verification, and copy algorithms are routed through the cache interface.

---

Linked user story: story-20250714-centralized-checksum-cache.md
