# Implementation Strategy: dedup_file_tools_compare

## Module Name
`dedup_file_tools_compare`



## What It Will Do
- Accept two directory paths (left and right) as input.
- Recursively list all files in both directories.
- Compute or load checksums for all files.
- Build two tables (left and right) mapping relative paths to checksums and metadata.
- Compare the tables to:
  - Identify files present in both with matching checksums (identical)
  - Identify files present in both with different checksums (differing)
  - Identify files unique to left
  - Identify files unique to right
- Output results to console, CSV, or JSON.
- Provide progress feedback and logging.
- Expose a Python API for programmatic use.



## Notes
- The tool will use efficient, multi-threaded checksum calculation.
- Designed for extensibility (future: database pool support, advanced diff, sync/merge).
- All output will clearly indicate which pool (left/right) each file belongs to.
- The CLI will be user-friendly and scriptable for automation.
