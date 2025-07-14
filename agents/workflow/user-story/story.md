# User Story: Import Checksum Cache Table

## As a user of the file copy tool,
I want to be able to import externally provided checksums into a dedicated checksum cache table,
so that the tool can use these checksums as a fallback when the main tables are missing values, improving performance and flexibility without overwriting computed or trusted checksums.

### Acceptance Criteria
- Imported checksums are stored in a new `checksum_cache` table with metadata (source, imported_at).
- All phases (copy, verify, etc.) use the cache as a fallback if the main table is missing a checksum.
- The import phase does not overwrite existing checksums in the main tables.
- Documentation and CLI help are updated to explain the new behavior.
- Migration and rollback instructions are provided.

---

*Created: 2025-07-14*
*Author: Agent (GitHub Copilot)*
