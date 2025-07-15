# Requirement: Destination Index Pool for Duplicate Detection

## Summary

Introduce the concept of a **destination index pool** to enhance duplicate detection during file copy operations. This allows the system to check for duplicates not just at the target destination path, but across an entire pool (e.g., a whole drive or logical group of files).

## Motivation

- In some workflows, it is necessary to avoid copying files that already exist anywhere in the destination pool, not just at the specific target path.
- This prevents unnecessary duplication across the destination, saving space and ensuring data consistency.
- There are also scenarios where a file must be copied to a specific location, regardless of its presence elsewhere in the pool.

## Requirements

- Implement a `destination_index_pool` abstraction that represents the set of all files (and their checksums) in the destination pool.
- Add a function or method `exists_at_destination_index_pool(checksum)` that checks if a file with the given checksum exists anywhere in the pool.
- Allow configuration of duplicate detection mode:
  - **Path-specific**: Only check for duplicates at the target destination path.
  - **Pool-wide**: Check for duplicates across the entire destination index pool.
- Ensure the logic is efficient for large pools (consider indexing, caching, or database-backed approaches).
- Document the behavior and provide clear CLI/configuration options for users to select the desired mode.

## Use Cases

- **Backup/De-duplication**: Avoid storing multiple copies of the same file anywhere in the backup destination.
- **Targeted Copy**: Allow copying to a specific location even if the file exists elsewhere, when required by the user.

## Implementation Notes

- The destination index pool can be implemented as a database or in-memory index of checksums and paths.
- The system should support switching between path-specific and pool-wide duplicate detection as needed.

---

_Proposed: 2025-07-15_
_Author: GitHub Copilot_
