# Requirement: Destination Index Pool & CLI Management

## Summary
Implement a destination index pool for global duplicate detection and provide robust CLI commands to manage and update this pool efficiently.

## Requirements

1. **Destination Index Pool Table**
   - Create a table (e.g., `destination_pool_index`) to store checksums, relative paths, and timestamps for all files in the destination pool.
   - This table is not the main job or copy database, and should not be confused with it. It is a separate index for global duplicate detection.
   - All entries must be indexed and checked according to the canonical uidpath abstraction, not just raw filesystem paths.
   - The table must support efficient upserts and queries by checksum and uidpath.

2. **Idempotent CLI Command: add-to-destination-index-pool**
   - Recursively scan a given destination root directory.
   - For each file, calculate its checksum and update/insert into the index table.
   - Skip files already indexed with the same checksum and path.
   - Update entries if files have changed (e.g., size, mtime, or checksum).
   - Safe to run multiple times; must not create duplicates.

3. **CLI Command: calculate-checksums-for-destination-pool**
   - Recalculate checksums for all files in the destination pool and update the index table.
   - Useful for refreshing the index after manual changes or corruption.

4. **Duplicate Detection Function**
   - Implement `exists_at_destination_pool(checksum)` to check if a file exists anywhere in the pool.
   - Allow switching between path-specific and pool-wide duplicate detection via CLI/config.

5. **Documentation & Testing**
   - Document all new commands and options.
   - Add tests to ensure correct indexing, updating, and duplicate detection.

---

_Proposed: 2025-07-15_
_Author: GitHub Copilot_
