# Strategy: Destination Index Pool & CLI Management

## Overview
This strategy describes how to implement and maintain a destination index pool for global duplicate detection, including robust CLI commands for updating and managing the pool.

## Steps

1. **Database/Table Design**
   - Create a `destination_pool_index` table with columns: `checksum`, `relative_path`, `size`, `mtime`, `last_seen`.
   - Add indexes on `checksum` and `relative_path` for fast lookups.

2. **CLI: add-to-destination-index-pool**
   - Recursively scan the destination root directory.
   - For each file:
     - Calculate checksum (block-wise for efficiency).
     - Upsert (insert or update) the entry in `destination_pool_index`.
     - Skip if already indexed with same checksum and path.
     - Update if file has changed (size, mtime, or checksum).
   - Log progress and summary.
   - Safe to run multiple times (idempotent).

3. **CLI: calculate-checksums-for-destination-pool**
   - For all files in the destination pool, recalculate checksums and update the index table.
   - Useful for refreshing the index after manual changes or corruption.

4. **Duplicate Detection**
   - Implement `exists_at_destination_pool(checksum)` to query the index for any file with the given checksum.
   - Integrate this check into the copy logic, configurable via CLI/config.

5. **Testing & Documentation**
   - Add tests for CLI commands and duplicate detection logic.
   - Document usage, options, and expected behaviors.

## Notes
- Use efficient file scanning and database operations to handle large pools.
- Ensure all operations are resumable and safely interruptible.
- Provide clear CLI feedback and error handling.

---

_Proposed: 2025-07-15_
_Author: GitHub Copilot_
