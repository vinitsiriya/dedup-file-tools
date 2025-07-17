# Shallow Verify Feature Requirements

## Purpose
Shallow verification checks that files exist at the destination and that their basic attributes (size and last modified time) match the source. It is a fast, non-cryptographic check to ensure files were copied without obvious corruption or truncation.


## Requirements
- The tool must verify that every file in the source set has a corresponding file at the destination, and that the destination file really exists on disk (not just in a database or index).
- For each file, the following attributes must match between source and destination:
  - File size (in bytes)
  - Last modified timestamp (to the nearest second)
- If a file is missing or attributes do not match, the tool must report the file as a verification failure.
- The tool must log a summary of verification results, including counts of passed and failed files.
- The tool must support batch operation and scale to millions of files.
- The tool must not require reading file contents (no checksums or hashes).
- The tool must provide a summary output suitable for automation and scripting.
- The tool must log all failures with enough detail for audit and troubleshooting.
- There must be an option (e.g., `--reverify`) that, when used, will undo any previous 'done' status marking for files and force all files to be re-verified, regardless of their prior status.

## Out of Scope
- Shallow verify does not check file contents or cryptographic hashes.
- Does not detect silent bit-level corruption if size and mtime are unchanged.

## Architecture Note (2025-07)
- All job databases are now named `<job-name>.db` in the job directory. All CLI commands require `--job-name`.
- The checksum cache database is always named `checksum-cache.db` in the job directory.
