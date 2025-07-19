# Code Review Notes: dedup_file_tools_dupes_move

## Key Review Points
- All file references must use `UidPath` abstraction.
- No direct manipulation of `rel_path` outside of `UidPath` utilities.
- All file move and checksum operations must be logged.
- No file deletions—only moves, and only if the destination does not already contain the file.
- CLI must support dry-run and log level options.
- All error handling must be robust and logged.
- Tests must cover edge cases and error conditions.
- Code must be cross-platform and follow project conventions.
