# User Story: dedup_file_tools_dupes_move

## Title
Remove and Move Duplicate Files by Checksum

## As a
User with a large directory tree containing duplicate files

## I want
To identify all files with identical content (by checksum) and move all but one copy of each duplicate group to a specified destination directory, so that I can reclaim space and organize my data without risk of data loss.


## Acceptance Criteria
- I can run a CLI tool to scan a directory for duplicate files (by checksum).
- The tool moves all but one copy of each duplicate group to a destination directory, preserving the original relative directory structure under the destination root.
- For each group of duplicates, one file remains in its original location (the "keeper"); all others are moved.
- If a file with the same checksum already exists at the destination, the move is skipped and logged.
- The tool never deletes files automatically; I can review and delete moved files manually.
- The tool provides a dry-run mode, logs all actions, and is resumable and idempotent.
- The tool works on both Windows and Linux.
- The tool provides clear error messages and audit logs for all actions.
