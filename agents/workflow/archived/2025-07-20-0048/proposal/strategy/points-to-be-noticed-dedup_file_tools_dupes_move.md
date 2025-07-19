# Points to Be Noticed: dedup_file_tools_dupes_move

- Only one copy of each duplicate group should remain in the source; all others must be moved to the destination.
- Never move a file if the destination already contains a file with the same checksum.
- All operations must be resumable and idempotent.
- Use block-wise reads for checksums to avoid memory issues with large files.
- All logs must be persistent and reviewable.
- The tool must be cross-platform (Windows, Linux).
- No file deletions—user must manually review and delete after move.
- Handle symlinks, permission errors, and edge cases gracefully.
- Reference and follow all audit, implementation, and agent protocol notes in this directory.
