# Requirements: Analyze Phase

## Overview
The analyze phase scans the lookup pool, computes checksums, and groups duplicate files for the deduplication workflow.

## Requirements
- The CLI must provide an `analyze` subcommand.
- Must require `--job-dir`, `--job-name`, and `--lookup-pool` arguments.
- Must scan all files in the lookup pool and compute checksums.
- Must group files by checksum to identify duplicates.
- Must update the database with file metadata and duplicate groups.
- Must support multi-threaded scanning (default: 4 threads).
- Must log progress and errors.

## References
- See implementation/analyze.md and feature/analyze.md for details.
