# Requirement Proposal: Robust Destination Pool Checksum Cache Validation

## Title
Robust Validation and Logging for Destination Pool Checksum Cache

## Date
2025-07-17

## Status
Draft

## Authors
- GitHub Copilot (agent)
- [Your Name Here]

## Background
Currently, the `exists_at_destination_pool` method in the `ChecksumCache` class only checks the database for a valid checksum entry. It does not verify the actual file's existence, modification time (mtime), or size on disk, nor does it log reasons for invalidation or mark cache entries as invalid if checks fail. This can result in false positives and unreliable cache validation.

## Problem Statement
- The destination pool checksum cache may indicate a file is valid when it is missing or altered on disk.
- There is no logging of reasons for invalidation, making debugging and auditing difficult.
- Stale or incorrect cache entries are not automatically invalidated.

## Requirements
1. **File Existence Check:**
   - The system must check if the destination file exists on disk when validating a checksum cache entry.
2. **File Metadata Validation:**
   - The system must compare the file's size and modification time (mtime) with the cached values.
3. **Logging:**
   - If any check fails (missing file, size mismatch, mtime mismatch), the system must log the reason in the logger file.
4. **Automatic Invalidation:**
   - If validation fails, the cache entry must be marked as not valid (`is_valid = 0`) in the database.
5. **Return Value:**
   - The method must return `False` if any check fails, and `True` only if all checks pass.
6. **Configurability:**
   - The file path resolution for the destination pool should use a configurable root directory if available, or infer from the database schema if not specified.

## Out of Scope
- Changes to the source pool checksum cache logic (already robust).
- Changes to unrelated modules or workflow processes.

## Acceptance Criteria
- All requirements above are implemented and tested.
- Logging is clear and actionable for debugging and audit.
- No false positives in destination pool cache validation.
- Documentation is updated to reflect the new logic.

---

**Status:** Awaiting review and feedback. Please provide comments or approval to proceed to implementation.
