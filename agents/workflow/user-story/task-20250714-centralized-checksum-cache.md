# Task: Implement Centralized Checksum Cache

## Steps
1. Redesign schema: make cache the only checksum store, add validity marker, remove per-table checksums.
2. Refactor all code paths (copy, verify, analyze, import, export, status, log) to use the cache.
3. Write migration script for existing jobs/databases.
4. Update all tests and fixtures.
5. Document migration and upgrade process.
6. Run full E2E and manual test suites.

## Expected Results
- All features work as before or better, using the cache.
- Migration is safe and documented.
- All tests pass.

---

Linked user story: story-20250714-centralized-checksum-cache.md
