# Move Logic for dedup_file_tools_dupes_move

## Overview
- Only true duplicate files (by checksum) are moved.
- For each group of duplicates, one file is kept in its original location (the "keeper").
- All other duplicates are moved to a user-specified destination directory.
- The relative directory structure of each moved file is preserved under the destination root.
- No file is deleted; only moved. The user can review and delete moved files manually.
- If a file with the same checksum already exists at the destination, the move is skipped and logged.
- All operations are resumable, idempotent, and logged for auditability.

## Example
Suppose you have:

```
source_dir/
  a/file1.txt  # checksum: X
  b/file2.txt  # checksum: X (duplicate)
  c/file3.txt  # checksum: Y
```

If destination is `dupes_dir/`, after running the tool:
- `a/file1.txt` remains in place (keeper)
- `b/file2.txt` is moved to `dupes_dir/b/file2.txt`
- `c/file3.txt` is not a duplicate and is not moved

## Implementation Notes
- The analysis phase identifies all duplicate groups and selects one file per group to keep in place.
- The move phase moves all other files in the group to the destination, preserving their relative paths.
- The tool never deletes files automatically.
- All actions are logged and resumable.
