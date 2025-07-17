# Requirement Proposal: Robust Validation and Logging for Destination Pool Checksum Cache

## Summary

Enhance the destination pool checksum cache logic to ensure robust validation of file existence, modification time (mtime), and size, with explicit logging and automatic invalidation of stale cache entries. This will improve reliability, auditability, and user feedback for all operations involving the destination pool.

## Motivation

Currently, the `exists_at_destination_pool` method in `ChecksumCache` only checks the database for a valid checksum entry. It does not verify the actual file's existence, mtime, or size on disk, nor does it log reasons for invalidation or mark cache entries as invalid if checks fail. This can result in false positives and makes debugging difficult.

## Requirements

- The system **must** check the actual file existence, mtime, and size for destination pool entries when validating the checksum cache.
- If any check fails (file missing, size mismatch, mtime mismatch), the system **must**:
  - Log the reason for invalidation in the logger file (e.g., missing file, size mismatch, mtime mismatch).
  - Mark the cache entry as not valid (`is_valid = 0`) in the database.
  - Return `False` for the validation check.
- Only if all checks pass, return `True` for the validation check.
- The file path for the destination pool should be resolved using the UID and relative path, consistent with the project's file resolution logic.
- The implementation **must** be auditable, with clear log messages for every invalidation event.
- The change **must not** break existing interfaces or workflows.

## Acceptance Criteria

- [ ] The `exists_at_destination_pool` method (or equivalent) performs all required file checks and logging.
- [ ] The cache is automatically invalidated in the database if a file fails validation.
- [ ] All reasons for invalidation are logged with sufficient detail for audit and debugging.
- [ ] The implementation passes all existing and new tests for destination pool validation.
- [ ] No regressions or interface changes are introduced.

## Open Questions

- Should the file path resolution for the destination pool use a configurable root directory, or always infer from the database schema? (Default: infer from context if not specified.)

---

**Status:** Draft

**Discussion:** Please review and provide feedback or refinements. No implementation will proceed until this proposal is explicitly marked as "Accepted" or "Ready for implementation" as per the workflow protocol.

---

*Created: 2025-07-17*
*Author: GitHub Copilot*
