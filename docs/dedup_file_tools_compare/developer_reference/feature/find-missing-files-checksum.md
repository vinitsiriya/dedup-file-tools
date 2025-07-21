# Feature: Find Missing Files by Comparing Two Directories Using Checksums

## What It Does
- Compares two directory trees (left and right) and finds files that are:
  - Only in left (missing from right)
  - Only in right (missing from left)
  - In both with identical content (by checksum)
  - In both with different content (by checksum)

## How It Works
- Uses a persistent checksum cache for fast, repeatable comparisons.
- Scans directories in parallel and batches DB operations for speed.
- Stores all results in a SQLite DB for auditability and scripting.
- CLI supports summary, full, CSV, and JSON output.

## Who Should Use It
- Anyone needing to audit, verify, or synchronize large directory trees.
- Useful for backup validation, deduplication, and migration checks.

## Example Use Cases
- Find files missing from a backup copy.
- Detect files that have changed between two folders.
- Generate a machine-readable report of all differences for automation.
