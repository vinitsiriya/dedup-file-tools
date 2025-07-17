# Proposal: Enhance Destination Pool Checksum Cache Validation

## Background
Currently, the `exists_at_destination_pool` method in `ChecksumCache` only checks the database for a valid checksum entry via SQL join. It does not verify the actual file's existence, modification time (mtime), or size on disk, nor does it log reasons for invalidation or mark cache entries as invalid if checks fail.

## Problem
This approach can result in false positives: the database may indicate a valid file, but the file may be missing or altered on disk. This undermines the reliability of the cache and makes debugging difficult.

## Proposed Solution
- Update `exists_at_destination_pool` to:
  1. Resolve the actual file path for the destination pool entry (using UID and relative path).
  2. Check if the file exists on disk.
  3. Compare the file's size and mtime with the cached values.
  4. If any check fails, log the reason (missing file, size mismatch, mtime mismatch).
  5. Mark the cache entry as not valid in the database if validation fails.
  6. Return `False` if any check fails, `True` only if all checks pass.

## Benefits
- Ensures the cache reflects the true state of the destination pool.
- Provides clear logging for debugging and auditability.
- Automatically invalidates stale or incorrect cache entries.

## Open Question
- Should the file path resolution for the destination pool use a configurable root directory, or infer from the database schema? (Default: infer from context if not specified.)

## Request for Feedback
Please review and provide feedback or approval. Refinements will be made as needed before implementation.
