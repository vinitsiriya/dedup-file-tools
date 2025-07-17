# User Story: Robust Validation of Destination Pool Checksum Cache

## Title
As a user, I want the destination pool checksum cache to always reflect the true state of files on disk, so that file existence, size, and modification time are validated and logged, and invalid cache entries are automatically detected and handled.

## Context
Currently, the cache may indicate a file is valid even if it is missing or altered on disk. This can cause silent errors and makes debugging difficult.

## Acceptance Criteria
- When checking for a valid checksum in the destination pool, the system must:
  - Resolve the actual file path using UID and relative path.
  - Check if the file exists on disk.
  - Compare the file's size and mtime with the cached values.
  - If any check fails, log the specific reason (missing file, size mismatch, mtime mismatch).
  - Mark the cache entry as not valid in the database if validation fails.
  - Only return `True` if all checks pass; otherwise, return `False`.
- All validation failures must be clearly logged for audit and debugging.
- The file path resolution method must be documented and, if configurable, clearly described.

## Notes
- This user story is based on the proposal "Enhance Destination Pool Checksum Cache Validation".
- Implementation must follow the workflow protocol for proposal/user story chronology and archival.
