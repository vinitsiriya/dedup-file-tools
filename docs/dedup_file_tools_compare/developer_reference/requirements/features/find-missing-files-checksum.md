# Find Missing Files by Comparing Two Directories Using Checksums

## Requirements

- The tool must compare two directory trees (left and right) and find files that are:
  - Present in left but missing in right (missing_right)
  - Present in right but missing in left (missing_left)
  - Present in both with identical checksums (identical)
  - Present in both with different checksums (different)
- The tool must use a persistent checksum cache for efficient repeated runs.
- The tool must support multithreaded, batched directory scanning and checksum calculation.
- The tool must provide a CLI with commands for:
  - Initializing a job
  - Adding files to left/right pools
  - Ensuring checksum cache is up to date for each pool
  - Running the comparison
  - Showing results in summary, full, CSV, and JSON formats
- The tool must store all results in a SQLite database for auditability and scripting.
- The tool must provide clear, scriptable, and human/machine-readable output.
- The tool must be robust to large directory trees and handle errors gracefully.
- The tool must be fully testable, with per-phase and CLI workflow tests.
