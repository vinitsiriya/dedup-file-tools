
# User Story: Find Missing Files by Comparing Two Directories with Checksums

## Title
Find Missing Files by Comparing Two Directories Using Checksums

## Status
Draft

## Author
AI Agent

## Date
2025-07-21

---

## User Story


As a user,
I want to compare the contents of two directories (source and target) by computing and matching file checksums,
So that I can reliably find files that are missing on either side, or present only on one side, and ensure that all files have been copied correctly.

For example, after copying data from one hard drive to another, I want to verify that every file from the source exists on the target, and vice versa, regardless of file names or modification times.

---

## Acceptance Criteria


- The tool accepts two directory paths as input (source and target).
- The tool computes or loads checksums for all files in both directories.
- The tool outputs:
  - Files present in both directories with matching checksums (identical files)
  - Files present in both directories with different checksums (differing files)
  - Files missing from the target (present in source, not in target)
  - Files missing from the source (present in target, not in source)
- The results are available via CLI and API.
- The tool provides clear, human-readable output and supports CSV/JSON export.

---

## Notes

- The comparison is based strictly on checksum values, not just file names or sizes.
- The user can use the results to verify that all files have been copied between two drives or directories, and to detect any missing or extra files.
- The tool should handle large directories efficiently and provide progress feedback.

---

## Status
Draft – Updated to focus on missing file detection and copy verification use case.
