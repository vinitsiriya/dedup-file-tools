# Tasks: Destination Index Pool Implementation

## 1. Database/Table
- [ ] Create `destination_pool_index` table with columns: checksum, relative_path, size, mtime, last_seen
- [ ] Add indexes for fast lookup by checksum and path

## 2. CLI: add-to-destination-index-pool
- [ ] Implement recursive scan of destination root
- [ ] Calculate checksum for each file (block-wise)
- [ ] Upsert entry in `destination_pool_index` (insert or update)
- [ ] Skip files already indexed with same checksum and path
- [ ] Update entry if file has changed (size, mtime, or checksum)
- [ ] Log progress and summary
- [ ] Ensure idempotency (safe to run multiple times)

## 3. CLI: calculate-checksums-for-destination-pool
- [ ] Implement command to recalculate checksums for all files in the pool
- [ ] Update index table as needed

## 4. Duplicate Detection Logic
- [ ] Implement `exists_at_destination_pool(checksum)`
- [ ] Integrate with copy logic, configurable via CLI/config

## 5. Documentation & Testing
- [ ] Document new commands and options
- [ ] Add tests for CLI and duplicate detection logic

_Proposed: 2025-07-15_
_Author: GitHub Copilot_
