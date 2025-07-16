# Deep Verify Feature Requirements

## Purpose
Deep verification ensures that files at the destination are exact, bit-for-bit copies of the source by comparing cryptographic checksums (e.g., SHA-256). It is a thorough check for data integrity after copy.
Deep verify is a superset of shallow verify: it performs all shallow checks (existence, size, mtime) and additionally verifies cryptographic checksums.


## Requirements
- The tool must compute and compare cryptographic checksums (e.g., SHA-256) for each file in the source and destination.
- The tool must verify that every file in the source set has a corresponding file at the destination, and that the destination file really exists on disk (not just in a database or index).
- For each file, the following must match between source and destination:
  - File size (in bytes)
  - Last modified timestamp (to the nearest second)
  - Cryptographic checksum (e.g., SHA-256)
- If a file is missing, or any attribute or checksum does not match, the tool must report the file as a verification failure.
- The tool must log a summary of verification results, including counts of passed and failed files.
- The tool must support batch operation and scale to millions of files.
- The tool must provide a summary output suitable for automation and scripting.
- The tool must log all failures with enough detail for audit and troubleshooting.
- There must be an option (e.g., `--reverify`) that, when used, will undo any previous 'done' status marking for files and force all files to be re-verified, regardless of their prior status.

## Out of Scope
- Deep verify does not attempt to repair or re-copy failed files (verification only).
- Does not guarantee detection of corruption if both source and destination are identically corrupted before verification.
