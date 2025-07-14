# Strategy: Import Checksum as Separate Cache Table (Refined)

## 1. Schema & Data Flow Changes
- **Create a new table** (e.g., `checksum_cache`) to store imported checksums:
  - Columns: `(uid, relative_path, checksum, source, imported_at)`
- **Do not update** `source_files`/`destination_files` directly during import; only populate the cache.

## 2. Code & Workflow Updates
- **Checksum Lookup Logic:**
  - All phases (copy, verify, etc.) must be updated to:
    - First check the main table for a checksum.
    - If missing, look up the checksum in `checksum_cache`.
    - Optionally, copy the checksum from cache to the main table if used.
- **Import Phase:**
  - Only populates `checksum_cache` from external sources (old DB, manifest, etc.).
- **Checksum Phase:**
  - Computes and stores missing checksums in the main tables as before.

## 3. Migration & Compatibility
- **Deprecation:**
  - Warn users that imported checksums are now in a separate cache and will only be used if the main table is missing a checksum.
- **Fallback Logic:**
  - Provide a migration script to copy cache values into the main tables if needed for legacy compatibility.

## 4. Testing & Validation
- **Test all phases** to ensure they correctly use the cache as a fallback.
- **Test performance** and correctness for large datasets and edge cases.

## 5. Documentation & Communication
- **Update all documentation** to explain the new cache mechanism and lookup order.
- **Provide migration and rollback instructions.**

## 6. Risks & Mitigations
- **Missed cache lookups:**
  - Mitigate with comprehensive tests and code review.
- **User confusion:**
  - Mitigate with clear CLI warnings and documentation.

---

**Status: Approved**

*Updated: 2025-07-14*
*Author: Agent (GitHub Copilot)*
