# UID Path Abstraction

## Overview
The `UidPath` abstraction provides a robust, system-independent way to represent file paths. All file-level state in `fs-copy-tool` is tracked using UIDs, ensuring portability and auditability across platforms and sessions.

## Features
- Converts file paths to unique, system-independent UIDs
- All job state (add-file, add-source, remove-file, list-files) uses UIDs
- Enables robust tracking of files even if paths change or drives are remounted
- Used in all phases: analyze, checksum, copy, verify, import
- All operations are logged for auditability

## Benefits
- Portability: jobs can be resumed on different systems or after drive changes
- Robustness: files are tracked even if their absolute path changes
- Auditability: all file operations are traceable via UIDs

## Example Usage
- Adding a file: `add-file --job-dir <path> --file <file_path>`
- Listing files: `list-files --job-dir <path>`
- All internal operations use UIDs for file identification

---
