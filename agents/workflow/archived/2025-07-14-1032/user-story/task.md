# Tasks: Import Checksum Cache Table

- [ ] Design and create the `checksum_cache` table schema in the database.
- [ ] Update the import phase to populate only the cache table.
- [ ] Refactor all phases (copy, verify, etc.) to use the cache as a fallback for missing checksums.
- [ ] Update CLI and documentation to explain the new cache mechanism.
- [ ] Write migration and rollback scripts/instructions.
- [ ] Add tests for cache lookup and fallback logic.
- [ ] Remove legacy import behavior after transition period.

---

*Created: 2025-07-14*
*Author: Agent (GitHub Copilot)*
